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
# Filtro por faixa de Battery Drain
battery_min, battery_max = st.sidebar.slider(
    "Battery Drain (mAh/dia):",
    min_value=float(300),
    max_value=float(3000),
    value=(
        float(300),
        float(3000)
    ),
    step=150.0
)

# Filtro por faixa de Apps Instalados
apps_min, apps_max = st.sidebar.slider(
    "Apps Instalados:",
    min_value=int(df["Number of Apps Installed"].min()),
    max_value=int(df["Number of Apps Installed"].max()),
    value=(
        int(df["Number of Apps Installed"].min()),
        int(df["Number of Apps Installed"].max())
    )
)

# Aplicar filtros

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
    & (df["Battery Drain (mAh/day)"].between(battery_min, battery_max)) 
    & (df["Number of Apps Installed"].between(apps_min, apps_max))
    & (df["Class Label"].isin(selected_class_labels)) # Usa o novo filtro
].copy() 

# Criar a coluna 'Age Group' no DataFrame filtrado para uso no gráfico
df_filtered["Age Group"] = pd.cut(
    df_filtered["Age"],
    bins=[18, 25, 33, 42, 50, 60],
    right=False,
    labels=["18-25", "26-33", "34-41", "42-49", "50-60"],
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
                axis=alt.Axis(labelAngle=0)
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
        "Tempo Médio de Uso por Gênero e Idade",
        "Porcentagem Celulares e SO",
        "Gasto de Bateria por Modelo",
        "Eficiência Energética",
        "Apps Instalados vs Screen On Time"
    ]
)

if selected_analysis == "Métricas por Sistema Operacional":
    st.subheader("Métricas de Uso Comparadas por Sistema Operacional e Gênero")

    # Criar coluna combinada OS + Gênero
    df_filtered["OS_Gender"] = df_filtered["Operating System"] + " & " + df_filtered["Gender"]

    # Agrupar por OS+Gênero e calcular médias
    df_os_gender_agg = (
        df_filtered.groupby("OS_Gender")[
            ["Screen On Time (hours/day)", "Data Usage (MB/day)", "Number of Apps Installed"]
        ]
        .mean()
        .reset_index()
    )

    # Renomear para ficar mais legível
    df_os_gender_agg = df_os_gender_agg.rename(columns={
        "Screen On Time (hours/day)": "Tempo de Tela (h/dia)",
        "Data Usage (MB/day)": "Uso de Dados (MB/dia)",
        "Number of Apps Installed": "Apps Instalados"
    })

    métricas = ["Tempo de Tela (h/dia)", "Uso de Dados (MB/dia)", "Apps Instalados"]

    for metrica in métricas:
        st.markdown(f"### 📊 {metrica}")

        chart = (
            alt.Chart(df_os_gender_agg)
            .mark_bar()
            .encode(
                x=alt.X("OS_Gender:N", title="Sistema Operacional + Gênero", axis=alt.Axis(labelAngle=0)),
                y=alt.Y(f"{metrica}:Q", title=metrica),
                color=alt.Color("OS_Gender:N", legend=None),
                tooltip=["OS_Gender:N", alt.Tooltip(f"{metrica}:Q", format=".2f")],
            )
            .properties(height=400)
        )

        st.altair_chart(chart, use_container_width=True)




elif selected_analysis == "Tempo Médio de Uso por Gênero e Idade":
    st.subheader("Tempo Médio de Uso de App por Gênero e Faixa Etária")

    # Agrupar antes para garantir que a média seja correta
    df_gender_age = (
        df_filtered.groupby(["Age Group", "Gender"])["App Usage Time (min/day)"]
        .mean()
        .reset_index()
    )

    gender_age_chart = (
        alt.Chart(df_gender_age)
        .mark_bar()
        .encode(
            x=alt.X("Age Group:N", title="Faixa Etária",axis=alt.Axis(labelAngle=0)),
            xOffset="Gender:N",  #SEPARA BARRAS POR GÊNERO DENTRO DO GRUPO
            y=alt.Y("App Usage Time (min/day):Q", title="Tempo Médio de Uso de App (min)"),
            color=alt.Color("Gender:N", title="Gênero"),
            tooltip=[
                "Gender:N",
                "Age Group:N",
                alt.Tooltip("App Usage Time (min/day):Q", format=".0f", title="Tempo Médio (min)")
            ],
        )
        .properties(title="Uso de App por Gênero e Faixa Etária")
    )

    st.altair_chart(gender_age_chart, use_container_width=True)


elif selected_analysis == "Porcentagem Celulares e SO":

    # ==========================================================
    # 1) GRÁFICO MODELOS DE CELULAR
    # ==========================================================

    phone_counts = (
        df_filtered["Device Model"]
        .value_counts()
        .rename_axis("Phone Model")
        .reset_index(name="Count")
    )

    total_phone = phone_counts["Count"].sum()
    phone_counts["Percent"] = (phone_counts["Count"] / total_phone) * 100

    pie_phone = (
        alt.Chart(phone_counts)
        .mark_arc()
        .encode(
            theta=alt.Theta("Count:Q", title="Quantidade"),
            color=alt.Color("Phone Model:N", title="Modelo"),
            tooltip=[
                alt.Tooltip("Phone Model:N", title="Modelo"),
                alt.Tooltip("Count:Q", title="Quantidade"),
                alt.Tooltip("Percent:Q", title="Porcentagem", format=".2f"),
            ],
        )
    )

    st.altair_chart(
        pie_phone.properties(
            title="Distribuição dos Modelos de Celular"
        ),
        use_container_width=True,
    )

    # ==========================================================
    # 2) GRÁFICO SISTEMAS OPERACIONAIS
    # ==========================================================

    os_counts = (
        df_filtered["Operating System"]
        .value_counts()
        .rename_axis("OS")
        .reset_index(name="Count")
    )

    total_os = os_counts["Count"].sum()
    os_counts["Percent"] = (os_counts["Count"] / total_os) * 100

    pie_os = (
        alt.Chart(os_counts)
        .mark_arc()
        .encode(
            theta=alt.Theta("Count:Q", title="Quantidade"),
            color=alt.Color("OS:N", title="Sistema Operacional"),
            tooltip=[
                alt.Tooltip("OS:N", title="Sistema Operacional"),
                alt.Tooltip("Count:Q", title="Quantidade"),
                alt.Tooltip("Percent:Q", title="Porcentagem", format=".2f"),
            ],
        )
    )

    st.altair_chart(
        pie_os.properties(
            title="Distribuição dos Sistemas Operacionais"
        ),
        use_container_width=True,
    )

elif selected_analysis == "Gasto de Bateria por Modelo":

    # Agrupar consumo de bateria médio por modelo
    battery_drain = (
        df_filtered.groupby("Device Model")["Battery Drain (mAh/day)"]
        .mean()
        .reset_index()
        .sort_values(by="Battery Drain (mAh/day)", ascending=False)
    )

    chart = (
        alt.Chart(battery_drain)
        .mark_bar()
        .encode(
            x=alt.X("Battery Drain (mAh/day):Q", title="Battery Drain (mAh/day) Médio (por dia)"),
            y=alt.Y("Device Model:N", sort="-x", title="Modelo"),
            tooltip=[
                alt.Tooltip("Device Model:N", title="Modelo"),
                alt.Tooltip("Battery Drain (mAh/day):Q", format=".2f", title="Consumo Médio"),
            ],
            color=alt.Color("Device Model:N", legend=None)
        )
        .properties(title="Battery Drain (mAh/day) Médio por Modelo")
    )

    st.altair_chart(chart, use_container_width=True)

elif selected_analysis == "Eficiência Energética":


    # Remove linhas inválidas
    df_filtered = df_filtered[df_filtered["Screen On Time (hours/day)"] > 0]

    # Criar métrica: consumo por hora de tela
    df_filtered["Energy Efficiency"] = (
        df_filtered["Battery Drain (mAh/day)"] / df_filtered["Screen On Time (hours/day)"]
    )

    efficiency = (
        df_filtered.groupby("Device Model")["Energy Efficiency"]
        .mean()
        .reset_index()
        .sort_values(by="Energy Efficiency")
    )

    chart = (
        alt.Chart(efficiency)
        .mark_bar()
        .encode(
            x=alt.X("Energy Efficiency:Q", title="Battery Drain por Hora de Tela (↓ melhor)"),
            y=alt.Y("Device Model:N", sort="x", title="Modelo"),
            tooltip=[
                alt.Tooltip("Device Model:N", title="Modelo"),
                alt.Tooltip("Energy Efficiency:Q", format=".3f", title="Eficiência"),
            ],
            color=alt.Color("Device Model:N", legend=None)
        )
        .properties(title="Ranking de Eficiência Energética dos Dispositivos")
    )

    st.altair_chart(chart, use_container_width=True)

elif selected_analysis == "Apps Instalados vs Screen On Time":
    st.subheader("Relação entre Número de Apps Instalados e Tempo de Tela (horas/dia)")

    scatter_chart = (
        alt.Chart(df_filtered)
        .mark_circle(size=90, opacity=0.7)
        .encode(
            x=alt.X(
                "Number of Apps Installed:Q",
                title="Número de Apps Instalados"
            ),
            y=alt.Y(
                "Screen On Time (hours/day):Q",
                title="Tempo de Tela (horas/dia)"
            ),
            color=alt.Color("Gender:N", title="Gênero"),  # opcional
            tooltip=[
                "Number of Apps Installed",
                "Screen On Time (hours/day)",
                "Gender",
                "Age Group"
            ]
        )
        .properties(
            title="Relação entre Apps Instalados e Tempo de Tela"
        )
        .interactive()
    )

    st.altair_chart(scatter_chart, use_container_width=True)




st.markdown("---")

# 5.3 Tabela de Dados (opcional, para ver a saída)
if st.checkbox("Mostrar Tabela de Dados Brutos"):
    st.dataframe(df_filtered.head(700))  # Limita a visualização para performance
