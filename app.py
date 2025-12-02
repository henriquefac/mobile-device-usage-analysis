import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from src.utils.load_data import load_data

# --- 1. FUNÇÃO DE SIMULAÇÃO DE DADOS ---
# Cria um DataFrame sintético que simula o conjunto de dados descrito
@st.cache_data
def load_data_streamlit():
    """Gera o conjunto de dados sintético."""
    return load_data()

# Carregar os dados simulados
df = load_data_streamlit()

# --- 2. CONFIGURAÇÃO DO STREAMLIT ---

st.set_page_config(
    page_title="Painel de Análise de Uso de Dispositivos Móveis",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📱 Painel de Análise de Uso de Dispositivos Móveis")
st.markdown("Análise de padrões de uso e classificação de comportamento do usuário.")

# --- 3. SIDEBAR PARA FILTROS ---
st.sidebar.header("Filtros Interativos")

# Filtro por Sistema Operacional
selected_os = st.sidebar.multiselect(
    "Sistema Operacional (OS)",
    options=df["Operating System"].unique(),
    default=df["Operating System"].unique(),
)

# Filtro por Modelo de Dispositivo
selected_model = st.sidebar.multiselect(
    "Modelo de Dispositivo",
    options=df["Device Model"].unique(),
    default=df["Device Model"].unique(),
)

# NOVO: Filtro por Gênero
selected_gender = st.sidebar.multiselect(
    "Gênero", options=df["Gender"].unique(), default=df["Gender"].unique()
)

# Filtro por Faixa Etária
age_min, age_max = st.sidebar.slider(
    "Faixa Etária",
    min_value=int(df["Age"].min()),
    max_value=int(df["Age"].max()),
    value=(int(df["Age"].min()), int(df["Age"].max())),
)

# Filtrar o DataFrame
df_filtered = df[
    (df["Operating System"].isin(selected_os))
    & (df["Device Model"].isin(selected_model))
    & (df["Gender"].isin(selected_gender))  # Adiciona o filtro de Gênero
    & (df["Age"] >= age_min)
    & (df["Age"] <= age_max)
]

st.subheader(f"Dados Filtrados: {len(df_filtered)} Usuários")

if df_filtered.empty:
    st.warning("Nenhum dado corresponde aos filtros selecionados.")
    st.stop()


# --- 4. EXIBIÇÃO DE KPIS (Métricas Chave de Desempenho) ---

col1, col2, col3, col4 = st.columns(4)

total_users = len(df_filtered)
avg_app_time = df_filtered["App Usage Time (min/day)"].mean()
avg_screen_time = df_filtered["Screen On Time (hours/day)"].mean()
avg_data_usage = df_filtered["Data Usage (MB/day)"].mean()

col1.metric("Total de Usuários", f"{total_users}")
col2.metric(
    "Tempo Médio de Uso de App",
    f"{avg_app_time:,.0f} min",
    delta=f"Total: {df_filtered['App Usage Time (min/day)'].sum():,.0f} min",
)
col3.metric(
    "Tempo Médio de Tela Ligada",
    f"{avg_screen_time:.1f} horas",
    delta=f"Máx: {df_filtered['Screen On Time (hours/day)'].max():.1f} h",
)
col4.metric(
    "Consumo Médio de Dados",
    f"{avg_data_usage:,.0f} MB",
    delta=f"Total: {df_filtered['Data Usage (MB/day)'].sum():,.0f} MB",
)

st.markdown("---")

# --- 5. GRÁFICOS DE VISUALIZAÇÃO ---

# 5.1 Distribuição da Classe de Comportamento
st.header("Distribuição e Padrões de Uso")
col_dist, col_corr = st.columns([1, 1])


with col_corr:
    st.subheader("Correlação: Uso de App vs. Drenagem de Bateria")

    # Gráfico de Dispersão
    corr_chart = (
        alt.Chart(df_filtered)
        .mark_circle(size=60)
        .encode(
            x=alt.X("App Usage Time (min/day)", title="Tempo de Uso de App (min)"),
            y=alt.Y("Battery Drain (mAh/day)", title="Drenagem de Bateria (mAh)"),
            color=alt.Color("Operating System", title="OS"),
            tooltip=[
                "App Usage Time (min/day)",
                "Battery Drain (mAh/day)",
                "Operating System",
                "Gender",
                "User Behavior Class",
            ],
        )
        .properties(title="Uso de App vs. Drenagem de Bateria (por OS)")
        .interactive()
    )  # Adiciona zoom e pan

    st.altair_chart(corr_chart, use_container_width=True)

st.markdown("---")

# 5.2 Análise por SO e Demografia
st.header("Análise Detalhada por Sistema Operacional e Gênero")
col_os, col_gender = st.columns(2)

with col_os:
    st.subheader("Métricas por Sistema Operacional")

    # Agrupar por OS e calcular médias
    df_os_agg = (
        df_filtered.groupby("Operating System")[
            ["Screen On Time (hours/day)", "Data Usage (MB/day)", "Number of Apps Installed"]
        ]
        .mean()
        .reset_index()
    )
    df_os_melt = df_os_agg.melt(
        "Operating System", var_name="Métrica", value_name="Valor Médio"
    )

    # Gráfico de Barras para comparação de métricas por OS
    os_metrics_chart = (
        alt.Chart(df_os_melt)
        .mark_bar()
        .encode(
            x=alt.X("Métrica:N", title="Métrica de Uso"),
            y=alt.Y("Valor Médio:Q", title="Valor Médio"),
            color=alt.Color("Operating System", title="OS"),
            column=alt.Column(
                "Métrica:N",
                header=alt.Header(titleOrient="bottom", labelOrient="bottom"),
            ),
            tooltip=[
                "Operating System",
                "Métrica",
                alt.Tooltip("Valor Médio", format=".1f"),
            ],
        )
        .properties(title="Comparação de Métricas de Uso (Screen On, Data, Apps)")
        .interactive()
    )

    st.altair_chart(os_metrics_chart, use_container_width=True)

with col_gender:
    st.subheader("Tempo Médio de Uso de App por Gênero e Idade")

    # Agrupar por Gênero e Idade (Criar Faixas Etárias para o gráfico)
    # Criar a coluna 'Age Group' no DataFrame filtrado para uso no gráfico
    df_filtered["Age Group"] = pd.cut(
        df_filtered["Age"],
        bins=[18, 25, 35, 45, 55, 65],
        right=False,
        labels=["18-24", "25-34", "35-44", "45-54", "55-65"],
    )

    gender_age_chart = (
        alt.Chart(df_filtered)
        .mark_bar()
        .encode(
            x=alt.X("Age Group:N", title="Faixa Etária"),
            y=alt.Y("mean(App Usage Time (min/day)):Q", title="Tempo Médio de Uso de App (min)"),
            color=alt.Color("Gender", title="Gênero"),
            tooltip=[
                "Gender",
                "Age Group",
                alt.Tooltip("mean(App Usage Time (min/day))", format=".0f"),
            ],
        )
        .properties(title="Uso de App por Gênero e Faixa Etária")
        .interactive()
    )

    st.altair_chart(gender_age_chart, use_container_width=True)

st.markdown("---")

# 5.3 Tabela de Dados (opcional, para ver a saída)
if st.checkbox("Mostrar Tabela de Dados Brutos"):
    st.dataframe(df_filtered.head(200))  # Limita a visualização para performance

# Rodar o aplicativo:
# Salve o código acima como 'app.py' e execute no terminal:
# streamlit run app.py
