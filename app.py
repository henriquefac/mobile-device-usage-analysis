import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from src.utils.load_data import load_data

# --- 1. FUNÇÃO DE SIMULAÇÃO DE DADOS ---
# Cria um DataFrame sintético que simula o conjunto de dados descrito
@st.cache_data
def load_data_streamlit():
    """
    Carrega o DataFrame usando a lógica de carregamento do usuário.
    Adiciona um fallback simplificado caso o carregamento falhe,
    para que o painel não quebre.
    """
    # Tabela de classificação para referência (necessário para os gráficos)
    class_labels_map = {
        '1': 'Leve',
        '2': 'Moderado',
        '3': 'Alto',
        '4': 'Muito Alto',
        '5': 'Extremo'
    }


        # Tenta carregar os dados reais
    df = load_data()
        
        # Garante que a coluna de classe seja string para mapeamento
    if 'User Behavior Class' in df.columns:
        df['User Behavior Class'] = df['User Behavior Class'].astype(str)
            
            # CRIAÇÃO DA COLUNA 'Class Label' APÓS O CARREGAMENTO
        df['Class Label'] = df['User Behavior Class'].map(class_labels_map)
        
    st.success("Dados reais carregados com sucesso!")
    return df


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

# filtrar pelo padrão de uso

selected_class_labels = st.sidebar.multiselect(
    "Classe de Usuário",
    options=df["Class Label"].unique(),
    default=df["Class Label"].unique()
)

# Filtrar o DataFrame
df_filtered = df[
    (df["Operating System"].isin(selected_os))
    & (df["Device Model"].isin(selected_model))
    & (df["Gender"].isin(selected_gender))
    & (df["Age"] >= age_min)
    & (df["Age"] <= age_max)
    & (df["Class Label"].isin(selected_class_labels)) # Usa o novo filtro
].copy() 

# Criar a coluna 'Age Group' no DataFrame filtrado para uso no gráfico
df_filtered["Age Group"] = pd.cut(
    df_filtered["Age"],
    bins=[18, 25, 35, 45, 55, 65],
    right=False,
    labels=["18-24", "25-34", "35-44", "45-54", "55-65"],
)
# -------------------------------------------------------------

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

# 5.1 Distribuição e Correlação
st.header("Distribuição e Padrões de Uso")
col_dist, col_corr = st.columns([1, 1])

with col_dist:
    st.subheader("Distribuição por Classe de Comportamento")

    # Tabela de classificação (apenas para ordem)
    class_labels_order = ['Leve', 'Moderado', 'Alto', 'Muito Alto', 'Extremo']
    
    # Criar o gráfico de barras
    class_chart = (
        alt.Chart(df_filtered)
        .mark_bar()
        .encode(
            x=alt.X(
                "Class Label:N",
                title="Classe de Comportamento",
                sort=class_labels_order,
            ),
            y=alt.Y("count():Q", title="Contagem de Usuários"),
            tooltip=["Class Label:N", "count():Q"],
            color=alt.Color("Class Label:N", legend=None),
        )
        .properties(title="Contagem de Usuários por Classe de Comportamento")
        .interactive()
    )

    st.altair_chart(class_chart, use_container_width=True)


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
                "Class Label",
            ],
        )
        .properties(title="Uso de App vs. Drenagem de Bateria (por OS)")
        .interactive()
    )  # Adiciona zoom e pan

    st.altair_chart(corr_chart, use_container_width=True)

st.markdown("---")

# 5.2 ANÁLISE DETALHADA POR SELEÇÃO DO USUÁRIO
st.header("Análise Detalhada (Selecionável)")

# Widget de seleção que substitui as duas colunas fixas
selected_analysis = st.selectbox(
    "Selecione a Análise de Detalhe:",
    [
        "Métricas por Sistema Operacional",
        "Tempo Médio de Uso por Gênero e Idade"
    ]
)

if selected_analysis == "Métricas por Sistema Operacional":
    st.subheader("Métricas de Uso Comparadas por Sistema Operacional")

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
    ).resolve_scale(x='independent') # Permite que cada coluna tenha sua própria escala X

    st.altair_chart(os_metrics_chart, use_container_width=True)

elif selected_analysis == "Tempo Médio de Uso por Gênero e Idade":
    st.subheader("Tempo Médio de Uso de App por Gênero e Faixa Etária")

    # O DataFrame filtrado já tem a coluna 'Age Group' criada
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
    st.dataframe(df_filtered.head(700))  # Limita a visualização para performance