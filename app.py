import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tablero NPS & Voz del Cliente", layout="wide")

st.title("📊 Tablero Unificado de Experiencia del Cliente")

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv("respuestas_nps.csv")

try:
    df = load_data()
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Filtros
    st.sidebar.header("🔍 Filtros de Visualización")
    areas = list(df["area"].unique())
    area_sel = st.sidebar.multiselect("Área / Módulo:", options=areas, default=areas)

    df_filtered = df[df["area"].isin(area_sel)]

    # Cálculo NPS
    def calc_nps(scores):
        if len(scores) == 0:
            return 0, 0, 0, 0
        prom = (scores >= 9).sum()
        det = (scores <= 6).sum()
        pas = ((scores >= 7) & (scores <= 8)).sum()
        tot = len(scores)
        nps = round(((prom - det) / tot) * 100, 1)
        return nps, prom, pas, det

    nps_val, prom, pas, det = calc_nps(df_filtered["score_nps"])

    # Tarjetas de KPI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("NPS Global", f"{nps_val}%")
    c2.metric("Promotores (9-10)", f"{prom}")
    c3.metric("Pasivos (7-8)", f"{pas}")
    c4.metric("Detractores (0-6)", f"{det}")

    st.markdown("---")

    tab1, tab2 = st.tabs(["📈 Análisis por Área y Motivo", "🤖 Verbatims & Extractos IA"])

    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Puntaje Promedio por Área")
            avg_area = df_filtered.groupby("area")["score_nps"].mean().reset_index()
            st.bar_chart(avg_area.set_index("area"))

        with col_b:
            st.subheader("Principales Motivos Reclamados/Elogiados")
            motivos = df_filtered["motivo"].value_counts()
            st.bar_chart(motivos)

    with tab2:
        st.subheader("Comentarios de Clientes y Resúmenes de IA")
        sent = st.radio("Filtrar Sentimiento IA:", ["Todos"] + list(df_filtered["ia_sentimiento"].unique()), horizontal=True)
        
        df_display = df_filtered if sent == "Todos" else df_filtered[df_filtered["ia_sentimiento"] == sent]
        
        st.dataframe(
            df_display[["fecha", "area", "score_nps", "verbatim", "ia_extracto", "ia_sentimiento"]],
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
