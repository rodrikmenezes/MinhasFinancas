import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Carregar arquivo de dados, se existir
if os.path.exists('Dados.xlsx'):
    tabela_final = pd.read_excel('Dados.xlsx', sheet_name='Dados')
else:
    tabela_final = pd.DataFrame(columns=['Índice', 'Data', 'Competência', 'Tipo', 'Descrição', 'Receita/Despesa', 'Valor', 'Classificação'])

# Remover colunas desnecessárias
tabela_final.drop(columns=['Unnamed: 0'], errors='ignore', inplace=True)

# Remover linhas sem descrição ou classificação vazia
tabela_final.dropna(subset=['Descrição'], inplace=True)

# Criar uma nova coluna combinando "Descrição" e "Classificação" (caso já esteja classificado)
tabela_final['Texto'] = tabela_final['Descrição'] + " " + tabela_final['Classificação'].fillna("")

# Separar dados classificados e não classificados
df_classificados = tabela_final[tabela_final['Classificação'].notna() & (tabela_final['Classificação'] != 'Sem Classificação')]
df_nao_classificados = tabela_final[tabela_final['Classificação'].isna() | (tabela_final['Classificação'] == 'Sem Classificação')]

# Verifica se há pelo menos 10 categorias distintas antes de treinar
if not df_classificados.empty and df_classificados['Classificação'].nunique() >= 10:

    # Vetorização TF-IDF das descrições + classificação
    vectorizer = TfidfVectorizer(max_features=500)
    X = vectorizer.fit_transform(df_classificados['Texto'])
    y = df_classificados['Classificação']

    # Divisão dos dados para avaliação do modelo
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Modelo de Machine Learning - Random Forest
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    # Avaliação do modelo
    y_pred = modelo.predict(X_test)
    acuracia = accuracy_score(y_test, y_pred)
    print(f"Acurácia do modelo: {acuracia:.2%}")

    # Aplicar modelo se existirem transações não classificadas
    if not df_nao_classificados.empty:
        X_novos = vectorizer.transform(df_nao_classificados['Texto'])
        df_nao_classificados['Classificação Prevista'] = modelo.predict(X_novos)
        df_nao_classificados['Alterado'] = df_nao_classificados['Classificação'] != df_nao_classificados['Classificação Prevista']
        df_nao_classificados['Classificação'] = df_nao_classificados['Classificação Prevista']
        df_nao_classificados.drop(columns=['Classificação Prevista'], inplace=True)

    # Atualizar os dados na tabela final
    tabela_final.update(df_nao_classificados)

else:
    print("⚠️ Poucos dados classificados! Marcar registros para revisão manual.")
    tabela_final.loc[tabela_final['Classificação'] == 'Sem Classificação', 'Classificação'] = "Revisão Manual"

# Criar uma tabela de frequências das classificações
classificacao = pd.DataFrame(tabela_final['Classificação'].value_counts().reset_index())
classificacao.columns = ['Classificação', 'Frequência']

# Criar um relatório financeiro
relatorio = tabela_final.groupby(['Tipo', 'Competência', 'Receita/Despesa'])['Valor'].sum().unstack()
if 'Receita' in relatorio.columns and 'Despesa' in relatorio.columns:
    relatorio['Resultado'] = relatorio['Receita'] - relatorio['Despesa']

# Salvar os resultados no Excel
with pd.ExcelWriter('Dados.xlsx', engine='xlsxwriter') as writer:
    tabela_final.to_excel(writer, sheet_name='Dados', index=False, freeze_panes=(1, 0))
    classificacao.to_excel(writer, sheet_name='Classificação', index=False, freeze_panes=(1, 0))
    relatorio.to_excel(writer, sheet_name='Relatório', index=True, freeze_panes=(1, 0))

print("Processo concluído!")
