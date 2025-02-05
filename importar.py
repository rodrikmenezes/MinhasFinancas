
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

# Remover linhas duplicadas, priorizando as linhas do arquivo Excel 
tabela_final = pd.concat([tabela_classificado, tabela_concatenada], ignore_index=True).drop_duplicates(
    subset=['Índice', 'Data', 'Competência', 'Tipo', 'Descrição', 'Receita/Despesa', 'Valor', 'Classificação'],
    keep='first'
    ).reset_index(drop=True).sort_values(by='Data')

# Resetar Índice
tabela_final.reset_index(drop=True, inplace=True)

# Tabela Classificação
classificacao = pd.DataFrame(tabela_final['Classificação'].value_counts().reset_index())
classificacao.columns = ['Classificação', 'Frequência']

# Tabela Relatório
relatorio = tabela_final.groupby(['Tipo', 'Competência', 'Receita/Despesa'])['Valor'].sum().unstack()
relatorio['Resultado'] = relatorio['Receita'] - relatorio['Despesa'] 

# Exportar a tabela final para um arquivo Excel
with pd.ExcelWriter('Dados.xlsx') as arquivo_excel:
    tabela_final.to_excel(arquivo_excel, sheet_name='Dados', freeze_panes=(1,0))
    classificacao.to_excel(arquivo_excel, sheet_name='Classificação', index=False, freeze_panes=(1,0))
    relatorio.to_excel(arquivo_excel, sheet_name='Relatório', index=True, freeze_panes=(1,0))

print('FIM')





