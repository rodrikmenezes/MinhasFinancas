
import pandas as pd
import numpy as np
import os

# Diretorio dados
conta_corrente = 'Dados//Conta Corrente'
cartao_credito = 'Dados//Cartão de Crédito'

# Importar Conta Corrente
arquivos = [arquivo for arquivo in os.listdir(conta_corrente) if arquivo.endswith('.csv')]
tabela_debito = []
for arquivo in arquivos:
    diretorio = os.path.join(conta_corrente, arquivo)
    competencia = arquivo[15:-4]
    tabela = pd.read_csv(diretorio)
    tabela['Competência'] = competencia
    tabela_debito.append(tabela)

# Importar Cartão de Crédito
arquivos = [arquivo for arquivo in os.listdir(cartao_credito) if arquivo.endswith('.csv')]
tabela_credito = []
for arquivo in arquivos:
    diretorio = os.path.join(cartao_credito, arquivo)
    competencia = arquivo[18:-4]
    tabela = pd.read_csv(diretorio)
    tabela['Competência'] = competencia
    tabela_credito.append(tabela)

# Concatenar lista com as tabelas
tabela_debito = pd.concat(tabela_debito)
tabela_credito = pd.concat(tabela_credito)

# Adicionar coluna Tipo
tabela_debito['Tipo'] = 'Conta Corrente'
tabela_credito['Tipo'] = 'Cartão de Crédito'

# Padronizar as colunas para combinar os dados
tabela_credito.columns = ['Data', 'Descrição', 'Valor', 'Competência', 'Tipo']

# Reordenar colunas
tabela_credito = tabela_credito[['Data', 'Competência', 'Tipo', 'Descrição', 'Valor']]
tabela_debito = tabela_debito[['Data', 'Competência', 'Tipo', 'Descrição', 'Valor']]

# Converter a coluna Data 
tabela_debito['Data'] = pd.to_datetime(tabela_debito['Data'], format='%d/%m/%Y', errors='coerce')
tabela_credito['Data'] = pd.to_datetime(tabela_credito['Data'], format='%Y-%m-%d', errors='coerce')

# Adicionar coluna 'Receita/Despesa'
tabela_debito['Receita/Despesa'] = np.where(tabela_debito['Valor'] < 0, 'Despesa', 'Receita' )
tabela_credito['Receita/Despesa'] = np.where(tabela_credito['Valor'] > 0, 'Despesa', 'Receita' )

# Ajustar tabela crédito
tabela_debito['Valor'] = np.where(tabela_debito['Valor'] < 0, tabela_debito['Valor'] * (-1), tabela_debito['Valor'])
tabela_credito['Valor'] = np.where(tabela_credito['Valor'] < 0, tabela_credito['Valor'] * (-1), tabela_credito['Valor'])

# Combinar as tabelas em um único DataFrame final
tabela_concatenada = pd.concat([tabela_credito, tabela_debito], ignore_index=True)

# Adicionar uma coluna vazia 'Classificação'
tabela_concatenada['Classificação'] = 'Sem Classificação'

# Adicionar coluna indice
tabela_concatenada['Índice'] = range(len(tabela_concatenada))

# Reordenar colunas
tabela_concatenada = tabela_concatenada[['Índice', 'Data', 'Competência', 'Tipo', 'Descrição', 'Receita/Despesa', 'Valor', 'Classificação']]

# Ajuste estorno
condicao = (tabela_concatenada['Descrição'].str[:7] == 'Estorno') & (tabela_concatenada['Receita/Despesa'] == 'Receita')
tabela_concatenada.loc[condicao, 'Valor'] = -tabela_concatenada.loc[condicao, 'Valor']
tabela_concatenada.loc[condicao, 'Receita/Despesa'] = 'Despesa'

# Importar dados
if os.path.exists('Dados.xlsx'): 
    tabela_classificado = pd.read_excel('Dados.xlsx')
    tabela_classificado['Data'] = pd.to_datetime(tabela_classificado['Data'], format='%d/%m/%Y', errors='coerce')
else:
    tabela_classificado = pd.DataFrame(columns=['Índice', 'Data', 'Competência', 'Tipo', 'Descrição', 'Receita/Despesa', 'Valor', 'Classificação'])

# Remove colunas vazias ou totalmente NA de cada DataFrame antes da concatenação
tabela_classificado = tabela_classificado.dropna(axis=1, how='all')
tabela_concatenada = tabela_concatenada.dropna(axis=1, how='all')

# Remover linhas duplicadas, priorizando as linhas do arquivo Excel 
tabela_final = pd.concat([tabela_classificado, tabela_concatenada], ignore_index=True).drop_duplicates(
    subset=['Índice', 'Data', 'Competência', 'Tipo', 'Descrição', 'Receita/Despesa', 'Valor'],
    keep='first').reset_index(drop=True).sort_values(by=['Competência', 'Tipo', 'Data'])

# Adicionar coluna 'Sugestão' em tabela_final
tabela_final['Sugestão'] = False

# Tabela Classificação
tabela_classificacao = pd.DataFrame(tabela_final['Classificação'].value_counts().reset_index())
tabela_classificacao.columns = ['Classificação', 'Frequência']
tabela_classificacao['%'] = tabela_classificacao['Frequência'] / tabela_classificacao['Frequência'].sum() * 100

# Tabela Relatório
tabela_relatorio = tabela_final.groupby(['Tipo', 'Competência', 'Receita/Despesa'])['Valor'].sum().unstack()
tabela_relatorio['Resultado'] = tabela_relatorio['Receita'] - tabela_relatorio['Despesa'] 

# Calcular totais por competência
totais = tabela_relatorio.groupby('Competência').sum()
totais['Tipo'] = 'Total'

# Adicionar totais à tabela_relatorio
totais = totais.set_index(['Tipo'], append=True).reorder_levels(['Tipo', 'Competência'])
tabela_relatorio = pd.concat([tabela_relatorio, totais])

# Exportar para Excel 
with pd.ExcelWriter('Dados.xlsx', engine='xlsxwriter') as arquivo_excel:
    
    # Abas
    tabela_final.to_excel(arquivo_excel, sheet_name='Dados', index=False, freeze_panes=(1, 0))
    tabela_relatorio.to_excel(arquivo_excel, sheet_name='Relatório', index=True, freeze_panes=(1, 0))
    tabela_classificacao.to_excel(arquivo_excel, sheet_name='Classificação', index=False, freeze_panes=(1, 0))

print('FIM')



