import streamlit as st
import requests
import pandas as pd
import time

#Armazena o arquivo na cache
@st.cache_data
#Função para converter o arquivo para '.csv'
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

# Função para mensagem de sucesso
def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon = '✅')
    time.sleep(5)
    sucesso.empty()

st.title('Dados Brutos')

url = 'https://labdados.com/produtos'

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

#### Filtro de seleção de Colunas
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

######################## Filtros da Barra lateral ##########################
st.sidebar.title('Filtros')
# Filtro do Produto
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())

# Filtro do Preço
with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o Preço', 0, 5000, (0, 5000))

# Filtro da data da compra
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max())) 

# Filtro da Categoria
with st.sidebar.expander('Categoria do Produto'):
    categoria = st.multiselect('Selecione a categoria', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())

# Filtro do frete da venda
with st.sidebar.expander('Valor do Frete'):
    frete = st.slider('Frete', 0, 250, (0, 250))

# Filtro de vendedores
with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Selecione o(s) vendedor(es)', dados['Vendedor'].unique(), dados['Vendedor'].unique())

# Filtro do local da compra
with st.sidebar.expander('Local da Compra'):
    local_compra = st.multiselect('Selecione o(s) Local(ais) da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())

# Filtro da avaliação da compra
with st.sidebar.expander('Avaliação da Compra'):
    avaliacao_compra = st.slider('Avaliação', 1,5, (1,5))

#Filtro do tipo do pagamento
with st.sidebar.expander('Tipo do Pagamento'):
    tipo_pagamento = st.multiselect('Selecione o(s) tipo(s) de pagamento(s)', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())

# Filtro das parcelas
with st.sidebar.expander('Quantidade de Parcelas'):
    parcelas = st.slider('Parcelas',  1, 24, (1,24))


#################### Filtragem das colunas #########

query = """
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and\
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
`Categoria do Produto` in @categoria and \
@frete[0] <= Frete <= @frete[1] and \
Vendedor in @vendedores and \
`Local da compra` in @local_compra and \
@avaliacao_compra[0] <= `Avaliação da compra` <= @avaliacao_compra[1] and \
`Tipo de pagamento` in @tipo_pagamento and \
@parcelas[0] <= `Quantidade de parcelas` <= @parcelas[1]
"""

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]


st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')

coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
    nome_arquivo += '.csv'

with coluna2:
    st.download_button('Fazer Download da tabela em csv', data = converte_csv(dados_filtrados), file_name = nome_arquivo, 
                       mime= 'text/csv', on_click = mensagem_sucesso)
