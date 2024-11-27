import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from query import conexao  # Certifique-se de que o arquivo query.py e a função conexao existem

# Configuração da página
st.set_page_config(
    page_title="Dashboard Interativo",
    page_icon="📊",
    layout="wide"
)

#with open("styles.css") as f:
#    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Consulta ao banco de dados
query = "SELECT * FROM tb_registro"

# Carregar os dados do banco e arquivos locais
df = conexao(query)
df_queimadas_sp = pd.read_csv('queimadas_sp.csv')

file_path = "producao.xlsx"  # Substitua pelo caminho correto do arquivo Excel
df_toneladas = pd.read_excel(file_path, sheet_name="Total")
df_produtos = pd.read_excel(file_path, sheet_name="Produto")

# Botão para atualizar os dados
if st.button("Atualizar Dados"):
    df = conexao(query)

# Menu lateral
st.sidebar.header("Configurações do Gráfico")
ColunaX = st.sidebar.selectbox(
    "Eixo Horizontal",
    options=["umidade", "temperatura", "pressao", "altitude", "co2", "poeira"],
    index=0
)
ColunaY = st.sidebar.selectbox(
    "Eixo Vertical",
    options=["umidade", "temperatura", "pressao", "altitude", "co2", "poeira"],
    index=1
)

# Filtro dinâmico para cada variável
def adicionar_filtro(nome_coluna, label, step=0.1):
    if nome_coluna in [ColunaX, ColunaY]:
        min_val = float(df[nome_coluna].min())
        max_val = float(df[nome_coluna].max())
        return st.sidebar.slider(
            label,
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val),
            step=step
        )
    return None

umidade_range = adicionar_filtro("umidade", "Umidade (%)")
temperatura_range = adicionar_filtro("temperatura", "Temperatura (°C)")
pressao_range = adicionar_filtro("pressao", "Pressão")
altitude_range = adicionar_filtro("altitude", "Altitude")
co2_range = adicionar_filtro("co2", "CO2 (ppm)")
poeira_range = adicionar_filtro("poeira", "Poeira")

# Aplicar os filtros ao DataFrame
df_selecionado = df.copy()

def aplicar_filtro(df, coluna, valores_range):
    if valores_range:
        df = df[(df[coluna] >= valores_range[0]) & (df[coluna] <= valores_range[1])]
    return df

df_selecionado = aplicar_filtro(df_selecionado, "umidade", umidade_range)
df_selecionado = aplicar_filtro(df_selecionado, "temperatura", temperatura_range)
df_selecionado = aplicar_filtro(df_selecionado, "pressao", pressao_range)
df_selecionado = aplicar_filtro(df_selecionado, "altitude", altitude_range)
df_selecionado = aplicar_filtro(df_selecionado, "co2", co2_range)
df_selecionado = aplicar_filtro(df_selecionado, "poeira", poeira_range)

# Função de visualização principal
def Home():
    st.title("Dashboard de Sensores e Produção Agrícola(SP)")
    with st.expander("Visualizar Dados"):
        colunas = st.multiselect(
            "Selecione colunas para visualizar",
            df_selecionado.columns,
            default=[]
        )
        if colunas:
            st.dataframe(df_selecionado[colunas])

    # Métricas
    if not df_selecionado.empty:
        media_umidade = df_selecionado["umidade"].mean()
        media_temperatura = df_selecionado["temperatura"].mean()
        media_co2 = df_selecionado["co2"].mean()

        

        col1, col2, col3 = st.columns(3)
        col1.metric("Média de Umidade", f"{media_umidade:.2f}")
        col2.metric("Média de Temperatura", f"{media_temperatura:.2f}")
        if pd.isna(media_co2):
            col3.metric("Média de CO2", f"Dado não disponível")
        else:
            col3.metric("Média de CO2", f"{media_co2:.2f}")

# Função de gráficos
def graficos():
    st.header("Gráficos Interativos")
    aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
        "Dispersão (Sensores)", "Queimadas", "Queimadas x Sensores",
        "Produção Geral", "Produção por Produto", "Produção x Queimadas"
    ])
    
    # Gráfico de dispersão
    with aba1:
        if ColunaX == ColunaY:
            st.warning("Selecione eixos diferentes para X e Y")
        else:
            fig = px.scatter(
                df_selecionado,
                x=ColunaX,
                y=ColunaY,
                color_discrete_sequence=["#197917"],
                title=f"Relação entre {ColunaX.capitalize()} e {ColunaY.capitalize()}",
                template="plotly_white"
            )
            st.plotly_chart(fig)
    
    # Gráfico de queimadas
    with aba2:
        grupo_dados = df_queimadas_sp.groupby(by=["date"])['focuses'].sum().reset_index(name="total_focos")
        fig_valores1 = px.bar(
            grupo_dados,
            x="total_focos",
            y="date",
            orientation="h",
            labels={"total_focos": "Total de Focos", "date": "Data"},
            title="Quantidade de focos de queimado por data em São Paulo",
            color_discrete_sequence=["#F51111"],
            template="plotly_white"
        )
        st.plotly_chart(fig_valores1, use_container_width=True)
    
    # Gráfico de "Queimadas x Sensores"
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

                #df_sensor_meses = df_selecionado.groupby(df_selecionado['date'])

                # Faz a junção das bases de dados usando 'tempo_registro' no lugar de 'date' para a tabela de sensores
                #df_combinado = df_sensor_meses.merge(df_queimadas_sp[['date', 'focuses']], how='inner', left_on='tempo_registro', right_on='date')

                df_combinado = df_selecionado.merge(df_queimadas_sp[['date', 'focuses']], how='inner', left_on='tempo_registro', right_on='date')

                df_combinado['tempo_registro'] = df_combinado['tempo_registro'].astype(str)
                df_combinado['date'] = df_combinado['date'].astype(str)

                # Criação do gráfico relacionando as variáveis selecionadas com os focos de queimadas
                fig_valores2 = px.density_heatmap(
                    df_combinado,
                    x=ColunaX,
                    y=ColunaY,
                    z="focuses",  # Intensidade baseada nos focos de queimadas
                    color_continuous_scale="OrRd",
                    labels={
                        ColunaX: ColunaX.capitalize(),
                        ColunaY: ColunaY.capitalize(),
                        "focuses": "Focos de Queimadas"
                    },
                    title=f"Mapa de Calor: {ColunaX.capitalize()} vs {ColunaY.capitalize()} com Focos de Queimadas",
                    template="plotly_white"
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
            color_discrete_sequence=["#197917"],
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

    with aba6:
        try:
            # Processar os dados do gráfico 1
            grupo_dados = df_queimadas_sp.groupby(by=["date"])['focuses'].sum().reset_index(name="total_focos")

            # Processar os dados do gráfico 2
            df_toneladas2 = df_toneladas.iloc[::-1].reset_index(drop=True)
            df_toneladas2 = df_toneladas2.rename(columns={'Data': 'date', 'Toneladas': 'toneladas'})

            if pd.api.types.is_period_dtype(grupo_dados['date']):
                grupo_dados['date'] = grupo_dados['date'].dt.to_timestamp()

            if pd.api.types.is_period_dtype(df_toneladas2['date']):
                df_toneladas2['date'] = df_toneladas2['date'].dt.to_timestamp()

            # Converter as colunas 'date' para o tipo datetime
            grupo_dados['date'] = pd.to_datetime(grupo_dados['date'], format='%Y/%m')
            df_toneladas2['date'] = pd.to_datetime(df_toneladas2['date'], format='%Y/%m')

            # Mesclar os dados com base na coluna 'date'
            dados_cruzados = pd.merge(grupo_dados, df_toneladas2, on="date", how="inner")

            # Se não houver dados após o merge, mostrar um aviso
            if dados_cruzados.shape[0] == 0:
                st.warning("Não há dados para as datas selecionadas nos dois conjuntos.")

            # Criar o gráfico cruzado com Plotly Graph Objects
            if dados_cruzados.shape[0] > 0:
                fig = go.Figure()

                # Adicionar a linha para os focos de queimadas
                fig.add_trace(go.Scatter(
                    x=dados_cruzados['date'],
                    y=dados_cruzados['total_focos'],
                    name='Focos de Queimada',
                    mode='lines+markers',
                    marker=dict(color='red'),
                    yaxis='y1'
                ))

                # Adicionar a linha para as toneladas
                fig.add_trace(go.Scatter(
                    x=dados_cruzados['date'],
                    y=dados_cruzados['toneladas'],
                    name='Toneladas Produzidas',
                    mode='lines+markers',
                    marker=dict(color='blue'),
                    yaxis='y2'
                ))

                # Configurar os eixos y
                fig.update_layout(
                    title="Comparação de Focos de Queimada e Toneladas Produzidas",
                    xaxis=dict(title='Data'),
                    yaxis=dict(
                        title='Total de Focos de Queimada',
                        side='left',
                        range=[0, dados_cruzados['total_focos'].max() * 1.1]  # Ajuste do intervalo do eixo Y1
                    ),
                    yaxis2=dict(
                        title='Toneladas Produzidas',
                        side='right',
                        overlaying='y',  # Coloca o eixo y2 sobre o eixo y1
                        range=[0, dados_cruzados['toneladas'].max() * 1.1]  # Ajuste do intervalo do eixo Y2
                    ),
                    template="plotly_white"
                )

                st.plotly_chart(fig, use_container_width=True)

        except FileNotFoundError as e:
            st.error(f"Erro ao carregar os arquivos: {e}")
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")

# Rodar as funções
Home()
graficos()
