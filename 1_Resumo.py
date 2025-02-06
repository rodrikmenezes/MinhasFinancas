import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# config
st.set_page_config(
    
    layout='wide', 
    page_title='Finanças',
    page_icon='⭐',
    initial_sidebar_state='auto'
    
)

# Importar dados
dados = pd.read_excel('Dados.xlsx', sheet_name='Dados')
st.session_state['dados'] = dados

# Titulo
st.markdown('# Minhas Finanças')
st.markdown('## Balanço Mensal')

# Selecionar competência
competencia = st.sidebar.selectbox('Competência', dados['Competência'].unique())

# Informações
tabela_totais = pd.DataFrame(dados[(dados['Competência'] == competencia)].groupby('Receita/Despesa')['Valor'].sum())
resultado_mes = tabela_totais[tabela_totais.index == 'Receita'].iloc[0] - tabela_totais[tabela_totais.index == 'Despesa'].iloc[0]
tabela_resumo = pd.pivot_table(dados, index='Competência', columns='Receita/Despesa', values='Valor', aggfunc='sum')
tabela_resumo['Resultado'] = tabela_resumo['Receita'] - tabela_resumo['Despesa']

# Print Resultado 
st.metric(label='Resultado', value=round(resultado_mes, 2))

# Print Balanço Mensal
st.bar_chart(tabela_totais)

# Print Histórico
st.table(tabela_resumo)







