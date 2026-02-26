import pandas as pd
import numpy as np
import re

pd.set_option('display.max_colwidth', None)
# Para melhorar a visualização dos DataFrames, tendo em vista que ele pode cortar algumas informações das células.

dados = pd.read_csv('cadastro_pj_legado.csv', sep=';', encoding='utf-8')
# Leitura do CSV.

dados['razao_social'] = (dados['razao_social']
                         .str.replace(r"\s+", " ", regex=True)
                         .str.strip()
                         .str.title()
                         .str.replace(r"ltda\.?", "LTDA", flags=re.IGNORECASE, regex=True)
                         .str.replace(r"s\.?a\.?", "S.A.", flags=re.IGNORECASE, regex=True)
                         .str.replace(r"\bme\b", "ME", flags=re.IGNORECASE, regex=True))
# Organizar os dados da coluna 'razao_social', limpando os espaços duplos,
# espaços extras, Title Case, e mantendo LTDA, S.A., ME maiúsculos.

dados['cnpj'] = (dados['cnpj']
                 .str.replace(r"\D", "", regex=True))
# Retirando tudo que não é número.

padrao_cnpj = r'(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})'
mascara_cnpj = r'\1.\2.\3/\4-\5'
dados['cnpj'] = (dados['cnpj']
                 .str.replace(padrao_cnpj, mascara_cnpj, regex=True))
# Ajustando o CNPJ para o formato correto.

dados['endereco_completo'] = (dados['endereco_completo']
 .str.split(r'(?<![a-zA-Z0-9])-|-(?![a-zA-Z0-9])'))
# Criando uma lista, a partir do hífen.

dados[['logradouro', 'complemento', 'bairro', 'cidade', 'uf', 'cep']] = pd.DataFrame(dados['endereco_completo'].to_list())
dados[['logradouro', 'complemento', 'bairro', 'cidade', 'uf', 'cep']] = dados[['logradouro', 'complemento', 'bairro', 'cidade', 'uf', 'cep']].apply(lambda x: x.str.strip())
# Criando as colunas.

dados = dados.drop(columns='endereco_completo')
# Dropando a coluna que não será mais utilizada.

dados['email_contato'] = (dados['email_contato']
                          .str.lower())
condicao = r'^[^@]+@[^@]+\.[^@]+$'
dados.insert(4, 'email_valido', dados['email_contato'].str.fullmatch(condicao))
# Converte a coluna 'email_contato' para minúscula e insere uma nova coluna,
# informando se o e-mail é válido ou não.

dados['tags_servico'] = (dados['tags_servico']
 .str.replace(r'[/;]', ',', regex=True)
 .str.strip()
 .str.split(',')
 )
dados['tags_servico'] = (dados['tags_servico']
 .str.join('|')
 .str.replace(r'\s*\|\s*', '|', regex=True))
# Troca os caracteres pelo delimitador que será utilizado para criar a lista.
# Junta as strings da lista pelo delimitador '|' e retira os espaços em branco.

dados['valor_contrato_mensal'] = (dados['valor_contrato_mensal']
 .str.replace(r'[R$ \.]', '', regex=True)
 .str.replace(',', '.', regex=True)
 .astype(np.float64))
# Ajuste dos dados numéricos e conversão para float.

dados.to_csv('cadastro_pj_padronizado.csv', sep=';', index=False, encoding='utf-8')
# Cria o csv com os dados transformados.

