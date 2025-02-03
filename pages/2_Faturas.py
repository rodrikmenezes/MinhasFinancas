import streamlit as st
import pandas as pd

# config
st.set_page_config(
    
    layout="wide", 
    page_title="Jogadores",
    page_icon="🏃‍♂️",
    initial_sidebar_state="expanded"
    
)

# importar dados
dados = st.session_state["dados"]

# Titulo
st.markdown("# Minhas Finanças")

