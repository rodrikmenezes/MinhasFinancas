import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

# Carregar arquivo de dados, se existir
if os.path.exists('Dados.xlsx'):
    tabela_final = pd.read_excel('Dados.xlsx', sheet_name='Dados')
else:
    tabela_final = pd.DataFrame(columns=['Índice', 'Data', 'Competência', 'Tipo', 'Descrição', 'Receita/Despesa', 'Valor', 'Classificação'])

# Remover coluna Unnamed se existir
tabela_final.drop(columns=['Unnamed: 0'], errors='ignore', inplace=True)

# Separar classificados e não classificados
df_classificados = tabela_final[tabela_final['Classificação'] != 'Sem Classificação']
df_nao_classificados = tabela_final[tabela_final['Classificação'] == 'Sem Classificação']

# Vetorização das descrições
vectorizer = CountVectorizer()
tf = vectorizer.fit_transform(df_classificados['Descrição'])

# Função para prever a classificação
def classificar(descricao, threshold=0.1):
    vec = vectorizer.transform([descricao]) 
    similaridades = cosine_similarity(vec, tf).flatten()
    max_sim = similaridades.max()
    if max_sim > threshold:
        return df_classificados.iloc[similaridades.argmax()]['Classificação']
    return 'Sem Classificação'

# Aplicar a classificação automática
tabela_final['Nova Classificação'] = tabela_final['Classificação']
tabela_final.loc[tabela_final['Classificação'] == 'Sem Classificação', 'Nova Classificação'] = tabela_final.loc[
    tabela_final['Classificação'] == 'Sem Classificação', 'Descrição'].apply(classificar)

# Criar uma coluna que marca as linhas alteradas
tabela_final['Alterado'] = tabela_final['Classificação'] != tabela_final['Nova Classificação']

# Atualizar a coluna de classificação com os novos valores
tabela_final['Classificação'] = tabela_final['Nova Classificação']
tabela_final.drop(columns=['Nova Classificação'], inplace=True)

# Tabela Classificação
classificacao = pd.DataFrame(tabela_final['Classificação'].value_counts().reset_index())
classificacao.columns = ['Classificação', 'Frequência']

# Tabela Relatório
relatorio = tabela_final.groupby(['Tipo', 'Competência', 'Receita/Despesa'])['Valor'].sum().unstack()
relatorio['Resultado'] = relatorio['Receita'] - relatorio['Despesa']

# Exportar para Excel 
with pd.ExcelWriter('Dados.xlsx', engine='xlsxwriter') as writer:
    
    # Abas
    tabela_final.to_excel(writer, sheet_name='Dados', index=False, freeze_panes=(1, 0))
    classificacao.to_excel(writer, sheet_name='Classificação', index=False, freeze_panes=(1, 0))
    relatorio.to_excel(writer, sheet_name='Relatório', index=True, freeze_panes=(1, 0))


print('FIM')
