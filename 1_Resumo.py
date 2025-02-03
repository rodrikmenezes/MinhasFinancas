import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# config
st.set_page_config(
    
    layout="wide", 
    page_title="Finanças",
    page_icon="⭐",
    initial_sidebar_state="auto"
    
)

# Importar dados
dados = pd.read_excel("Dados.xlsx", sheet_name="Dados")
st.session_state["dados"] = dados

# Titulo
st.markdown("# Minhas Finanças")
st.markdown("## Balanço Mensal")

# Selecionar competência
competencia = st.sidebar.selectbox("Competência", dados["Competência"].unique())

# Info
conta_corrente = pd.DataFrame(dados[(dados["Competência"] == competencia) & (dados["Tipo"] == "Conta Corrente")].groupby("Receita/Despesa")["Valor"].sum())
resultado = conta_corrente[conta_corrente.index == "Receita"].iloc[0] - conta_corrente[conta_corrente.index == "Despesa"].iloc[0]
tabela_conta_corrente = dados[dados["Tipo"] == "Conta Corrente"]
tabela_resumo = pd.pivot_table(tabela_conta_corrente, index="Competência", columns="Receita/Despesa", values="Valor", aggfunc="sum")
tabela_resumo["Resultado"] = tabela_resumo["Receita"] - tabela_resumo["Despesa"]

# Resultado print
st.metric(label="Resultado", value=round(resultado, 2))

# Balanço mensal print
st.bar_chart(data=conta_corrente)

# Histórico
st.table(tabela_resumo)







