import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout = 'wide')

# Formatação dos valores, com o acréscimo do prefixo
def formata_numero(valor, prefixo = ''):

    for unidade in ['','mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000 

    return f'{prefixo} {valor:.2f} milhões'

# Inserção do título
st.title('DASHBOARD DE VENDAS :shopping_trolley:')

# Pegando os dados da url
url = 'https://labdados.com/produtos'

###### Filtragem de regiões ########
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

##### Criando uma sidebar para os filtros
st.sidebar.title('Filtros')

#### Select box para a região
regiao = st.sidebar.selectbox('Região', regioes)

#### Caso a regiao seja Brasil não será feita nenhuma filtragem, a url será mantida na forma padrão
if regiao == 'Brasil':
    regiao = '' 

############ Filtragem dos anos ########

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)

##### Slider para selecionar um ano específico
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

### Dicionário para identificar o valor 'regiao' e o valor 'ano'
query_string = {'regiao': regiao.lower(), 'ano': ano} 

# Armazenando os dados coletados na url no response
response = requests.get(url, params = query_string)

# Transformando o response em arquivo .json
dados = pd.DataFrame.from_dict(response.json())

# Formatando a coluna 'Data da Compra'
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# Filtro para Vendedores

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]
    
########################################## TABELAS ################################

# Agrupando as receitas por estados
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

# Agrupando a receita mensal, separada por ano
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

# Tabela para receita de cada uma das categorias dos produtos
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending = False)

### Tabela de quantidade de vendas

# Tabela de quantidade de vendas por estado
vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

# Tabela de quantidade de vendas mensais
qtd_vendas_mensais = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].count()).reset_index()
qtd_vendas_mensais['Ano'] = qtd_vendas_mensais['Data da Compra'].dt.year
qtd_vendas_mensais['Mes'] = qtd_vendas_mensais['Data da Compra'].dt.month_name()

# Tabela dos 5 estados com maiores vendas (Não é necessária, basta pegar as primeiras 5 linhas da tabela vendas_estados)

# Quantidade de vendas por categoria do produto

qtd_vendas_produto_categoria = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))

### Tabela Vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

#------------------------------------------ #GRÁFICOS# -------------------------------------------------------#

# Gráfico do mapa da América do sul #
fig_mapa_receita = px.scatter_geo(receita_estados, lat = 'lat', lon = 'lon', scope = 'south america', size = 'Preço',
                                   template = 'seaborn', hover_name = 'Local da compra', hover_data = {'lat': False, 'lon': False},
                                   title = 'Receita por estado')

# Gráfico das receitas mensais #
fig_receita_mensal = px.line(receita_mensal, x = 'Mes', y = 'Preço', markers = True, range_y = (0, receita_mensal.max()), 
                             color = 'Ano', line_dash = 'Ano', title = 'Receita Mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')

# Gráfico de barras da receita de estados #
fig_receita_estados = px.bar(receita_estados.head(), x = 'Local da compra', y = 'Preço', text_auto = True, title = 'Top estados (Receita)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

# Gráfico da receita por categoria do Produto #
fig_receita_categorias = px.bar(receita_categorias, text_auto = True, title = 'Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

# Gráfico de quantidade de vendas mensais #
fig_vendas_mensais = px.line(qtd_vendas_mensais, x = 'Mes', y = 'Preço', markers = True, range_y = (0,qtd_vendas_mensais.max()),
                                     color = 'Ano', line_dash = 'Ano', title = 'Quantidades de vendas Mensal')
fig_vendas_mensais.update_layout(yaxis_title = 'Quantidade')

# Gráfico da quantidade de vendas por estado #
fig_vendas_estados = px.scatter_geo(vendas_estados, lat = 'lat', lon = 'lon', scope = 'south america' , template = 'seaborn',
                                            size = 'Preço', hover_name = 'Local da compra', hover_data = {'lat': False, 'lon': False},
                                            title = 'Vendas por estado')

# Gráfico dos 5 estados com maiores vendas #
fig_top5_estados = px.bar(vendas_estados.head(), x = 'Local da compra', y = 'Preço', text_auto = True, title = 'Top 5 estados')
fig_top5_estados.update_layout(yaxis_title = 'Quantidade de vendas')

# Gráfico da quantidade de vendas por categoria do produto

fig_qtd_categorias = px.bar(qtd_vendas_produto_categoria, text_auto = True, title= 'Vendas por Categoria')
fig_qtd_categorias.update_layout(yaxis_title = 'Quantidade', showlegend = False)

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+ Melhorando a visualização das métricas usando colunas (Streamlit) -+-+-+-+-+-+-+-+-+-+-+-+-+#

# Criando abas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:

    coluna1, coluna2 = st.columns(2)
    with coluna1:
        # Adicionando métricas (Total de vendas)
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)

    with coluna2:
        # Adicionando métricas (Qtd de vendas)
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)

with aba2:
    
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        # Adicionando métricas (Total de vendas)
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))

        #Plotando o gráfico de vendas por estados
        st.plotly_chart(fig_vendas_estados, use_container_width = True)
        st.plotly_chart(fig_top5_estados, use_container_width = True)

    with coluna2:
        # Adicionando métricas (Qtd de vendas)
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))

        # Gráfico da quantidade de vendas mensais
        st.plotly_chart(fig_vendas_mensais, use_container_width = True)
        st.plotly_chart(fig_qtd_categorias, use_container_width = True)
        

with aba3:

    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        # Adicionando métricas (Total de vendas)
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores),
                                        x = 'sum', y = vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True, title = f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)

    with coluna2:
        # Adicionando métricas (Qtd de vendas)
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores),
                                        x = 'count', y = vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True, title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores)

# Criação do Data Frame
#st.dataframe(dados)

