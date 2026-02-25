import pandas as pd
import numpy as np
import csv
import chardet
import ast

def farejar_csv(caminho_arquivo):
    with open(caminho_arquivo, 'rb') as arquivo_binario:
        amostra_bytes = arquivo_binario.read(10000)
        resultado_chardet = chardet.detect(amostra_bytes)
        encoding_descoberto = resultado_chardet['encoding']

    with open(caminho_arquivo, 'r', encoding=encoding_descoberto) as arquivo_texto:
        amostra_texto = arquivo_texto.read(1024)
        farejador = csv.Sniffer()
        separador_descoberto = farejador.sniff(amostra_texto).delimiter

    return encoding_descoberto, separador_descoberto

def extrair_metricas(lista_precos):
    p_min = min(lista_precos)
    p_max = max(lista_precos)
    p_med = round(np.mean(lista_precos), 2)

    return pd.Series([p_min, p_max, p_med])

meu_enc, meu_sep = farejar_csv('vendas_q4_raw.csv')

dados = pd.read_csv('vendas_q4_raw.csv', sep=meu_sep, encoding=meu_enc)

dados[['preco_venda', 'custo']] = dados[['preco_venda', 'custo']].map(lambda x: x.replace('R$ ', '').replace('.', '').replace(',', '.').strip())
dados[['preco_venda', 'custo']] = dados[['preco_venda', 'custo']].astype(np.float64)

dados['margem_bruta'] = dados['margem_bruta'].apply(lambda x: x.replace(',', '.').replace('%', '').strip())
dados['margem_bruta'] = dados['margem_bruta'].astype(np.float64)

dados['precos_concorrentes'] = dados['precos_concorrentes'].apply(ast.literal_eval)

dados[['preco_concorrente_min', 'preco_concorrente_max', 'preco_concorrente_medio']] = dados['precos_concorrentes'].apply(extrair_metricas)

dados.drop('precos_concorrentes', axis=1, inplace=True)

condicoes = [
    (dados['preco_venda'] < dados['preco_concorrente_medio']),
    (dados['preco_venda'] > dados['preco_concorrente_medio'])
]
escolhas = ['abaixo', 'acima']
dados['posicao_mercado'] = np.select(condicoes, escolhas, default='alinhado')

dados['data_venda'] = pd.to_datetime(dados['data_venda'], format='%Y-%m-%d')

dados.to_csv('vendas_q4_tratado.csv', sep=';', index=False, encoding='utf-8')