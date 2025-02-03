
# módulos
import pandas as pd
import os

### importar cartão de crédito ###

# lista de arquivos a serem importados
arquivos_cartao_de_credito = [arquivo for arquivo in os.listdir("Cartão de Crédito") if arquivo.endswith('.csv')]

# tabela vazia cartão de crédito
tabela_cartao_de_credito = [] 

# adicionar dados dos arquivos na tabela vazia
for arquivo in arquivos_cartao_de_credito:
    
    # diretório do arquivo a ser importado
    diretorio = os.path.join("Cartão de Crédito", arquivo)
    
    # dados do arquivo
    tabela = pd.read_csv(diretorio)
    
    # lista com os dados
    tabela_cartao_de_credito.append(tabela)

# juntar as tabelas da lista em um dataframe 
tabela_cartao_de_credito = pd.concat(tabela_cartao_de_credito, ignore_index=True)


### importar conta corrente ###

# lista de arquivos a serem importados
arquivos_conta_corrente = [arquivo for arquivo in os.listdir("Conta Corrente") if arquivo.endswith('.csv')]

# tabela vazia conta corrente
tabela_conta_corrente = [] 

# adicionar dados dos arquivos na tabela vazia
for arquivo in arquivos_conta_corrente:

    # diretório do arquivo a ser importado
    diretorio = os.path.join("Conta Corrente", arquivo)

    # dados do arquivo
    tabela = pd.read_csv(diretorio)

    # lista com os dados
    tabela_conta_corrente.append(tabela)

tabela_conta_corrente = pd.concat(tabela_conta_corrente, ignore_index=True)

### combinar dados ###

# mudar nome das colunas
tabela_cartao_de_credito.columns = ["Data", "Descrição", "Valor"]

# organizar dados
tabela_conta_corrente = tabela_conta_corrente[["Data", "Descrição", "Valor"]]

# adicionar coluna cartão ou conta corrente
tabela_conta_corrente["Crédito/Débito"] = "Débito"
tabela_cartao_de_credito["Crédito/Débito"] = "Crédito"

# combinar
tabela_final = pd.concat([tabela_cartao_de_credito, tabela_conta_corrente], ignore_index=True)





