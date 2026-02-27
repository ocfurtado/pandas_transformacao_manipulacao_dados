# Importações
import pandas as pd

# Leitura do arquivo csv
relatorio_operacional_logistica = pd.read_csv('entregas_legado.csv', sep=';', encoding='utf-8')

## Tokenização da coluna 'rota'
# Remoção das '/', dos '->', dos espaços no início e no fim e conversão para lista a partir do ','
relatorio_operacional_logistica['rota'] = (relatorio_operacional_logistica['rota']
 .str.replace(r"/", ',', regex=True)
 .str.replace(r"\s*->\s*", ',', regex=True)
 .str.strip()
 .str.split(','))

# Criação das novas colunas, a partir da lista que foi criada na coluna 'rotas'
relatorio_operacional_logistica[['cidade_origem', 'uf_origem', 'cidade_destino', 'uf_destino']] = pd.DataFrame(relatorio_operacional_logistica['rota'].to_list(), index=relatorio_operacional_logistica.index)

# Remoção da coluna 'rota'
relatorio_operacional_logistica = relatorio_operacional_logistica.drop(columns='rota')

## Formatação das colunas 'data_pedido' e 'data_entrega'
# Não foi possível garantir a formatação correta da data por meio da inferência do Pandas
# As datas ISO e Brasileiras estavam sendo misturadas
# Devido a isso, foi necessário criar datas ISO e BR separadas e, depois, juntá-las
datas_iso = pd.to_datetime(relatorio_operacional_logistica['data_pedido'], format='%Y/%m/%d', errors='coerce')
datas_br = pd.to_datetime(relatorio_operacional_logistica['data_pedido'], format='%d/%m/%Y', errors='coerce')
relatorio_operacional_logistica['data_pedido'] = datas_iso.fillna(datas_br)

datas_iso = pd.to_datetime(relatorio_operacional_logistica['data_entrega'], format='%Y-%m-%d', errors='coerce')
datas_br = pd.to_datetime(relatorio_operacional_logistica['data_entrega'], format='%d-%m-%Y', errors='coerce')
relatorio_operacional_logistica['data_entrega'] = datas_iso.fillna(datas_br)

## Transformação da coluna 'tempo_transporte'
# Criação de uma Series que auxiliará na criação de um timedelta
mascara_timedelta = (relatorio_operacional_logistica['tempo_transporte']
 .str.replace(r'dia', 'day', regex=True)
 .str.replace(r'horas', 'hours', regex=True)
 .str.replace(r'e\s+', '', regex=True)
 .str.strip())
mascara_timedelta = pd.to_timedelta(mascara_timedelta)

# Criação da coluna 'horas_transporte' com horas totais de transporte
relatorio_operacional_logistica.insert(
    5,
    'horas_transporte',
    mascara_timedelta.dt.total_seconds() / 3600
)

# Drop da coluna 'tempo_transporte' que não será mais utilizada
relatorio_operacional_logistica = relatorio_operacional_logistica.drop(columns='tempo_transporte')

## Ajustes na coluna 'peso_kg'
# Conversão de ',' para '.'; remoção de espaços inicias e finais; e conversão para 'float64'
relatorio_operacional_logistica['peso_kg'] = (relatorio_operacional_logistica['peso_kg']
 .str.replace(r',', '.', regex=True)
 .str.strip()
 .astype('float64'))

## Formatação da coluna 'valor_frete'
# Remoção dos caracteres 'R$ '; substituição de '.' por vazio; conversão do decimal para o utilizado pelo Pandas;
# Remoção de espaços iniciais e finais; e conversão para 'float64'
relatorio_operacional_logistica['valor_frete'] = (relatorio_operacional_logistica['valor_frete']
 .str.replace(r'R\$\s+', '', regex=True)
 .str.replace(r'\.', '', regex=True)
 .str.replace(r'\,', '.', regex=True)
 .str.strip()
 .astype('float64'))

## Criar a tabela 'custo_por_hora'
# Criação da coluna 'custo_por_hora', conforme divisão entre as colunas 'valor_frete' e 'horas_transporte'
# Arredondamento para 2 casas decimais
relatorio_operacional_logistica['custo_por_hora'] = (relatorio_operacional_logistica['valor_frete'] / relatorio_operacional_logistica['horas_transporte']).round(2)


## Criar a coluna 'prazo_dias'
# Criação da coluna 'prazo_dias', conforme os dias derivado da subtração entre as colunas 'data_entrega' e 'data_pedido'
relatorio_operacional_logistica.insert(
    4,
    'prazo_dias',
    (relatorio_operacional_logistica['data_entrega'] - relatorio_operacional_logistica['data_pedido']).dt.days
) 

## Formatação da coluna 'status_entrega'
# Criação da coluna 'entregue', a partir de um Series (True/False) com condição de 'ENTREGUE'
relatorio_operacional_logistica['entregue'] = relatorio_operacional_logistica['status_entrega'].str.contains('ENTREGUE', case=False, na=False)

# Criação da coluna 'ocorrencia', a partir da coluna 'status_entrega'
# Corte a partir de '- ' para frente; remoção de espaços iniciais/finais e conversão para minúsculas
relatorio_operacional_logistica['ocorrencia'] = (relatorio_operacional_logistica['status_entrega']
 .str.replace(r'.*?- ', '', regex=True)
 .str.strip()
 .str.lower())

# Drop da coluna 'status_entrega' que não será mais utilizada
relatorio_operacional_logistica = relatorio_operacional_logistica.drop(columns='status_entrega')

## Criar CSV final
# Criação do csv final
relatorio_operacional_logistica.to_csv('entregas_padronizado.csv', sep=';', index=False, encoding='utf-8')



