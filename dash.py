import numpy as np
import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
from query import *

# Consulta o banco de dados
query = "SELECT * FROM tb_registro"

# Carregar os dados do MySQL
df = conexao(query)
df_queimadas_sp = pd.read_csv('queimadas_sp.csv')

# Carregar o arquivo Excel e especificar as abas
file_path = "producao.xlsx"  # substitua pelo caminho do seu arquivo Excel
df_toneladas = pd.read_excel(file_path, sheet_name="Total")
df_produtos = pd.read_excel(file_path, sheet_name="Produto") 

# Botão para atualização dos dados
if st.button("Atualizar Dados"):
    df = conexao(query)

# Menu lateral
st.sidebar.header("Selecione a informação para gerar o gráfico")

# Seleção de colunas X
# Selectbox -> cria uma caixa de seleção na barra lateral
ColunaX = st.sidebar.selectbox(
    "Eixo X",
    options=["umidade", "temperatura", "pressao", "altitude", "co2", "poeira"],
    index=0
)

ColunaY = st.sidebar.selectbox(
    "Eixo Y",
    options=["umidade", "temperatura", "pressao", "altitude", "co2", "poeira"],
    index=1
)

# Verificar quais os atributos do filtro
def filtros(atributo):
    return atributo in [ColunaX, ColunaY]

# Filtro de Range -> Slider
st.sidebar.header("Selecione o Filtro")

# UMIDADE
if filtros("umidade"):
    umidade_range = st.sidebar.slider(
        # Titulo
        "umidade (%)",
        # Valor mínimo
        min_value=float(df["umidade"].min()),
        # Valor máximo
        max_value=float(df["umidade"].max()),
        # Faixa de valores selecionados
        value=(float(df["umidade"].min()), float(df["umidade"].max())),
        # Incremento para cada movimento do slider
        step=0.1,
    )

# TEMPERATURA
if filtros("temperatura"):
    temperatura_range = st.sidebar.slider(
        # Titulo
        "Temperatura (°C)",
        # Valor mínimo
        min_value=float(df["temperatura"].min()),
        # Valor máximo
        max_value=float(df["temperatura"].max()),
        # Faixa de valores selecionados
        value=(float(df["temperatura"].min()), float(df["temperatura"].max())),
        # Incremento para cada movimento do slider
        step=0.1,
    )

# PRESSÃO
if filtros("pressao"):
    pressao_range = st.sidebar.slider(
        # Titulo
        "pressao",
        # Valor mínimo
        min_value=float(df["pressao"].min()),
        # Valor máximo
        max_value=float(df["pressao"].max()),
        # Faixa de valores selecionados
        value=(float(df["pressao"].min()), float(df["pressao"].max())),
        # Incremento para cada movimento do slider
        step=0.1,
    )

# ALTITUDE
if filtros("altitude"):
    altitude_range = st.sidebar.slider(
        # Titulo
        "altitude",
        # Valor mínimo
        min_value=float(df["altitude"].min()),
        # Valor máximo
        max_value=float(df["altitude"].max()),
        # Faixa de valores selecionados
        value=(float(df["altitude"].min()), float(df["altitude"].max())),
        # Incremento para cada movimento do slider
        step=0.1,
    )

# CO2
if filtros("co2"):
    co2_range = st.sidebar.slider(
        # Titulo
        "co2 (ppm)",
        # Valor mínimo
        min_value=float(df["co2"].min()),
        # Valor máximo
        max_value=float(df["co2"].max()),
        # Faixa de valores selecionados
        value=(float(df["co2"].min()), float(df["co2"].max())),
        # Incremento para cada movimento do slider
        step=0.1,
    )

# Poeira
if filtros("poeira"):
    poeira_range = st.sidebar.slider(
        # Titulo
        "poeira",
        # Valor mínimo
        min_value=float(df["poeira"].min()),
        # Valor máximo
        max_value=float(df["poeira"].max()),
        # Faixa de valores selecionados
        value=(float(df["poeira"].min()), float(df["poeira"].max())),
        # Incremento para cada movimento do slider
        step=0.1,
    )

df_selecionado = df.copy()

if filtros("umidade"):
    df_selecionado = df_selecionado[
        (df_selecionado["umidade"] >= umidade_range[0]) &
        (df_selecionado["umidade"] <= umidade_range[1])
    ]

if filtros("temperatura"):
    df_selecionado = df_selecionado[
        (df_selecionado["temperatura"] >= temperatura_range[0]) &
        (df_selecionado["temperatura"] <= temperatura_range[1])
    ]

if filtros("pressao"):
    df_selecionado = df_selecionado[
        (df_selecionado["pressao"] >= pressao_range[0]) &
        (df_selecionado["pressao"] <= pressao_range[1])
    ]

if filtros("altitude"):
    df_selecionado = df_selecionado[
        (df_selecionado["altitude"] >= altitude_range[0]) &
        (df_selecionado["altitude"] <= altitude_range[1])
    ]

if filtros("co2"):
    df_selecionado = df_selecionado[
        (df_selecionado["co2"] >= co2_range[0]) &
        (df_selecionado["co2"] <= co2_range[1])
    ]
    
if filtros("poeira"):
    df_selecionado = df_selecionado[
        (df_selecionado["poeira"] >= poeira_range[0]) &
        (df_selecionado["poeira"] <= poeira_range[1])
    ]

# GRAFICOS
def Home():
    with st.expander("Tabela"):
        mostrarDados = st.multiselect(
            "Filtro",
            df_selecionado.columns,
            default=[],
            key="showData_home"
        )

        if mostrarDados:
            st.write(df_selecionado[mostrarDados])

    if not df_selecionado.empty:
        media_umidade = df_selecionado["umidade"].mean()    
        media_temperatura = df_selecionado["temperatura"].mean()    
        media_co2 = df_selecionado["co2"].mean()    

        media1, media2, media3 = st.columns(3, gap="large")

        with media1:
            st.info("Média de Registros de Umidade", icon='📌')
            st.metric(label="Média", value=f"{media_umidade:.2f}")

        with media2:
            st.info("Média de Registros de Temperatura", icon='📌')
            st.metric(label="Média", value=f"{media_temperatura:.2f}")

        with media3:
            st.info("Média de Registros de CO2", icon='📌')
            st.metric(label="Média", value=f"{media_co2:.2f}")
        
        st.markdown("""---------""")

#GRAFICOS
def graficos():
    aba1, aba2, aba3, aba4, aba5 = st.tabs(["Gráfico de Dispersão (Sensores)", "Gráfico das queimadas", "Comparação Queimadas x Sensores", "Produção Geral Em São Paulo", "Produção Por Produto"])
    with aba1:
        if df_selecionado.empty:
            st.write("Nenhum dado está disponível para gerar o gráfico")
            return
            
        if ColunaX == ColunaY:
            st.warning("Selecione uma opção diferente para os eixos X e Y")
            return
            
        try:
            fig_valores = px.scatter(
                df_selecionado,
                x=ColunaX,
                y=ColunaY,
                title=f"Relação entre {ColunaX.capitalize()} e {ColunaY.capitalize()}",
                color_discrete_sequence=["#de171a"],
                template="plotly_white",
                #trendline="ols"  # Opcional: adiciona uma linha de tendência (regressão linear)
            )

        except Exception as e:
            st.error(f"Erro ao criar o gráfico de linha: {e}")

        st.plotly_chart(fig_valores)
    
    with aba2:
        try:
            grupo_dados = df_queimadas_sp.groupby(by=["date"])['focuses'].sum().reset_index(name="total_focos")

            # Criando o gráfico de barras horizontal com Plotly Express
            fig_valores1 = px.bar(
                grupo_dados,
                x="total_focos",
                y="date",
                orientation="h",
                labels={"total_focos": "Total de Focos", "date": "Data"},
                title="Quantidade de focos de queimado por data em São Paulo",
                color_discrete_sequence=["#de171a"],
                template="plotly_white"
            )

        except Exception as e:
            st.error(f"Erro ao criar o gráfico de linha: {e}")

        st.plotly_chart(fig_valores1, use_container_width=True)
    
    with aba3:
        
        if ColunaX == ColunaY:
            st.warning("Selecione uma opção diferente para os eixos X e Y")
            return

        # Converter a coluna 'tempo_registro' para 'YYYY-MM'
        df_selecionado['tempo_registro'] = df_selecionado['tempo_registro'].dt.to_period('M')

        # Converter a coluna 'date' de queimadas para 'YYYY-MM' (ano/mês)
        df_queimadas_sp['date'] = pd.to_datetime(df_queimadas_sp['date'], format='%Y/%m')
        df_queimadas_sp['date'] = df_queimadas_sp['date'].dt.to_period('M')
        
        # Verifica se as colunas selecionadas estão presentes nas bases
        if ColunaX in df_selecionado.columns and ColunaY in df_selecionado.columns and 'date' in df_queimadas_sp.columns:
            try:
                # Faz a junção das bases de dados usando 'tempo_registro' no lugar de 'date' para a tabela de sensores
                df_combinado = df_selecionado.merge(df_queimadas_sp[['date', 'focuses']], how='inner', left_on='tempo_registro', right_on='date')

                # Criação do gráfico relacionando as variáveis selecionadas com os focos de queimadas
                fig_valores2 = px.scatter(
                    df_combinado,
                    x=ColunaX,
                    y=ColunaY,
                    size="focuses",  # Tamanho das bolhas representa os focos de queimadas
                    color="focuses",  # Cor representa a quantidade de queimadas
                    labels={ColunaX: ColunaX.capitalize(), ColunaY: ColunaY.capitalize(), "focuses": "Focos de Queimadas"},
                    title=f"Relação entre {ColunaX.capitalize()}, {ColunaY.capitalize()} e Focos de Queimadas",
                    template="plotly_white",
                    color_continuous_scale=px.colors.sequential.OrRd
                )

            except Exception as e:
                st.error(f"Erro ao criar o gráfico: {e}")

            st.plotly_chart(fig_valores2, use_container_width=True)
        else:
            st.warning("Não foi possível relacionar as bases. Verifique as colunas de data.")
    
    with aba4:
        # Criando o gráfico de linha
        fig = px.line(
            df_toneladas.iloc[::-1].reset_index(drop=True), 
            x='Data', 
            y='Toneladas', 
            title='Toneladas Por Mês',
            labels={'Data': 'Mês/Ano', 'Toneladas': 'Quantidade (Toneladas)'})

        # Exibindo o gráfico no Streamlit
        st.plotly_chart(fig, use_container_width=True)
    
    with aba5:
        # Converter a coluna 'Data' para datetime (no formato ano/mês)
        df_produtos['Data'] = pd.to_datetime(df_produtos['Data'], format='%Y/%m')
        # Ordenar os dados pela Data para que os meses apareçam na ordem correta no gráfico
        df_produtos.sort_values(by='Data', inplace=True)

        # Criar o gráfico de barras com barras empilhadas ou agrupadas
        fig = px.bar(
            df_produtos, 
            x='Data', 
            y='Toneladas', 
            color='Produtos Agrícolas',  # Cada produto terá uma cor diferente
            title='Evolução Mensal das Toneladas por Produto Agrícola',
            labels={'Toneladas': 'Quantidade (Toneladas)', 'Data': 'Mês/Ano'}
        )

        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig, use_container_width=True)


Home()
graficos()