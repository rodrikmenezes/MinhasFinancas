import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

try:
    # Carregar arquivo de dados, se existir
    if os.path.exists('Dados.xlsx'):
        tabela_final = pd.read_excel('Dados.xlsx', sheet_name='Dados')
    else:
        tabela_final = pd.DataFrame(columns=['Índice', 'Data', 'Competência', 'Tipo', 'Descrição', 'Receita/Despesa', 'Valor', 'Classificação'])

    # Remover colunas desnecessárias
    tabela_final.drop(columns=['Unnamed: 0'], errors='ignore', inplace=True)

    # Remover linhas sem descrição ou classificação vazia
    tabela_final.dropna(subset=['Descrição'], inplace=True)

    # Separar dados classificados e não classificados
    df_classificados = tabela_final[tabela_final['Classificação'].notna() & (tabela_final['Classificação'] != 'Sem Classificação')]
    df_nao_classificados = tabela_final[tabela_final['Classificação'].isna() | (tabela_final['Classificação'] == 'Sem Classificação')]

    # Verifica se há pelo menos 10 categorias distintas antes de treinar
    if not df_classificados.empty and df_classificados['Classificação'].nunique() >= 10:

        # Vetorização TF-IDF das descrições
        vectorizer = TfidfVectorizer(max_features=500)
        X = vectorizer.fit_transform(df_classificados['Descrição'])
        y = df_classificados['Classificação']

        # Divisão dos dados para avaliação do modelo
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Modelo de Machine Learning - Random Forest
        modelo = RandomForestClassifier(n_estimators=100, random_state=42)
        modelo.fit(X_train, y_train)

        # Avaliação do modelo
        y_pred = modelo.predict(X_test)
        acuracia = accuracy_score(y_test, y_pred)
        print(f'Acurácia do modelo: {acuracia:.2%}')

        # Aplicar modelo se existirem transações não classificadas
        if not df_nao_classificados.empty:
            X_novos = vectorizer.transform(df_nao_classificados['Descrição'])
            df_nao_classificados['Classificação Prevista'] = modelo.predict(X_novos)
            df_nao_classificados['Sugestão'] = df_nao_classificados['Classificação'].isna() | (df_nao_classificados['Classificação'] != df_nao_classificados['Classificação Prevista'])
            df_nao_classificados['Classificação'] = df_nao_classificados['Classificação Prevista']
            df_nao_classificados.drop(columns=['Classificação Prevista'], inplace=True)

        # Atualizar os dados na tabela final
        tabela_final.update(df_nao_classificados)
        
        # Adicionar coluna 'Sugestão' em tabela_final
        tabela_final['Sugestão'] = tabela_final.index.isin(df_nao_classificados.index)

        # Tabela Classificação
        tabela_classificacao = pd.DataFrame(tabela_final['Classificação'].value_counts().reset_index())
        tabela_classificacao.columns = ['Classificação', 'Frequência']

        # Tabela Relatório
        tabela_relatorio = tabela_final.groupby(['Tipo', 'Competência', 'Receita/Despesa'])['Valor'].sum().unstack()
        tabela_relatorio['Resultado'] = tabela_relatorio['Receita'] - tabela_relatorio['Despesa'] 

        # Exportar para Excel 
        with pd.ExcelWriter('Dados.xlsx', engine='xlsxwriter') as arquivo_excel:
            
            # Abas
            tabela_final.to_excel(arquivo_excel, sheet_name='Dados', index=False, freeze_panes=(1, 0))
            tabela_classificacao.to_excel(arquivo_excel, sheet_name='Classificação', index=False, freeze_panes=(1, 0))
            tabela_relatorio.to_excel(arquivo_excel, sheet_name='Relatório', index=True, freeze_panes=(1, 0))
            
    else:
        
        # Mensagem
        print('⚠️ Poucos dados classificados! Marcar registros para revisão manual.')
            
except Exception as e:
    print(f'Ocorreu um erro: {e}')
    
    
    