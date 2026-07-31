import streamlit as st
import pandas as pd

# 1. Configuración general
st.set_page_config(page_title="Tablero Unificado de Experiencia (VoC)", layout="wide")
st.title("📊 Tablero Unificado de Voz del Cliente & Experiencia")

# 2. URLs de tus 4 bases de datos en formato CSV
URL_NPS_RELACIONAL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQkRId_MTUvXjEoeQoB5DRTVBy5LZSBwFJLnCD9tIkXu5mLLUWKuMfZYli95RWhZQBVhD0DiLqcr9fY/pub?output=csv"
URL_AUDITORIA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSqX6kWb9zVRCqouqL9yE-gkhcODTU-rNKGHs4uaGBXKIvAZv8I4xc2a3yoi1jrBJmXhSP1HSbsnLFD/pub?output=csv"
URL_ATENCION = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1I2VSwaUgunJRLpWFwFGor26ckwmHTPtN6H6alVnOx_tOshcvbzjMaA4h_-zPGJS-NC9KQWqTSNHp/pub?output=csv"
URL_AP5 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTbFTv5ei5f-lzMBdRGx3nCnT8RZw3va6OPQN2s_wmZjmpcoSWG82scnWt2hcjjEF-LB0VIJ1cQYmVN/pub?output=csv"

# Funciones de carga con caché rápida
@st.cache_data(ttl=15)
def load_data():
    df_nps = pd.read_csv(URL_NPS_RELACIONAL)
    df_auditoria = pd.read_csv(URL_AUDITORIA)
    df_atencion = pd.read_csv(URL_ATENCION)
    df_ap5 = pd.read_csv(URL_AP5)
    return df_nps, df_auditoria, df_atencion, df_ap5

try:
    df_nps, df_auditoria, df_atencion, df_ap5 = load_data()

    # Función auxiliar para calcular NPS
    def calcular_nps(series):
        numeric_series = pd.to_numeric(series, errors='coerce').dropna()
        if len(numeric_series) == 0:
            return 0, 0, 0, 0
        prom = (numeric_series >= 9).sum()
        det = (numeric_series <= 6).sum()
        pas = ((numeric_series >= 7) & (numeric_series <= 8)).sum()
        tot = len(numeric_series)
        nps_val = round(((prom - det) / tot) * 100, 1)
        return nps_val, prom, pas, det

    # --- PESTAÑAS DEL DASHBOARD ---
    tab_global, tab_nps, tab_auditoria, tab_atencion, tab_ap5 = st.tabs([
        "🌐 Resumen Unificado", 
        "🏢 NPS Relacional", 
        "📋 Auditoría", 
        "🎧 Atención al Cliente", 
        "💻 Experiencia AP5"
    ])

    # ---------------------------------------------------------
    # TAB 1: RESUMEN UNIFICADO
    # ---------------------------------------------------------
    with tab_global:
        st.header("Vista Macro de Mediciones")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Respuestas NPS Relacional", len(df_nps))
        c2.metric("Respuestas Auditoría", len(df_auditoria))
        c3.metric("Respuestas Atención Cliente", len(df_atencion))
        c4.metric("Respuestas Exp. AP5", len(df_ap5))
        
        st.markdown("---")
        
        # NPS Relacional Quick Metric
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("NPS Relacional General")
            if 'p3. NPS' in df_nps.columns:
                val_nps, prom, pas, det = calcular_nps(df_nps['p3. NPS'])
                st.metric("NPS Score", f"{val_nps}%")
                st.write(f"**Promotores:** {prom} | **Pasivos:** {pas} | **Detractores:** {det}")
            else:
                st.warning("Columna 'p3. NPS' no encontrada en la base Relacional.")
                
        with col_b:
            st.subheader("Solicitudes de Contacto Pendientes")
            # Conteo de personas que quieren ser contactadas
            contact_nps = len(df_nps[df_nps['p35 ¿Te gustaría ser contactado por un representante?'].astype(str).str.lower().str.contains("sí|si", na=False)]) if 'p35 ¿Te gustaría ser contactado por un representante?' in df_nps.columns else 0
            contact_ap5 = len(df_ap5[df_ap5['quiere ser contactado'].astype(str).str.lower().str.contains("sí|si", na=False)]) if 'quiere ser contactado' in df_ap5.columns else 0
            
            st.metric("Solicitudes de Contacto (Total)", contact_nps + contact_ap5)
            st.caption(f"NPS Relacional: {contact_nps} | Exp. AP5: {contact_ap5}")

    # ---------------------------------------------------------
    # TAB 2: NPS RELACIONAL
    # ---------------------------------------------------------
    with tab_nps:
        st.header("🏢 Encuesta NPS Relacional")
        
        if 'p1. En qué área trabajás' in df_nps.columns:
            area_filter = st.multiselect("Filtrar por Área de trabajo:", options=df_nps['p1. En qué área trabajás'].dropna().unique(), default=df_nps['p1. En qué área trabajás'].dropna().unique())
            df_nps_filtered = df_nps[df_nps['p1. En qué área trabajás'].isin(area_filter)]
        else:
            df_nps_filtered = df_nps

        st.dataframe(df_nps_filtered, use_container_width=True, hide_index=True)

    # ---------------------------------------------------------
    # TAB 3: AUDITORÍA
    # ---------------------------------------------------------
    with tab_auditoria:
        st.header("📋 Medición de Proceso de Auditoría")
        
        if 'Tipo de Agente' in df_auditoria.columns:
            agente_filter = st.multiselect("Filtrar por Tipo de Agente:", options=df_auditoria['Tipo de Agente'].dropna().unique(), default=df_auditoria['Tipo de Agente'].dropna().unique())
            df_aud_filtered = df_auditoria[df_auditoria['Tipo de Agente'].isin(agente_filter)]
        else:
            df_aud_filtered = df_auditoria

        st.dataframe(df_aud_filtered, use_container_width=True, hide_index=True)

    # ---------------------------------------------------------
    # TAB 4: ATENCIÓN AL CLIENTE
    # ---------------------------------------------------------
    with tab_atencion:
        st.header("🎧 Encuesta de Atención al Cliente")
        
        if 'Cod. Suc.Sucursales' in df_atencion.columns:
            suc_filter = st.multiselect("Filtrar por Sucursal:", options=df_atencion['Cod. Suc.Sucursales'].dropna().unique(), default=df_atencion['Cod. Suc.Sucursales'].dropna().unique())
            df_atencion_filtered = df_atencion[df_atencion['Cod. Suc.Sucursales'].isin(suc_filter)]
        else:
            df_atencion_filtered = df_atencion

        st.dataframe(df_atencion_filtered, use_container_width=True, hide_index=True)

    # ---------------------------------------------------------
    # TAB 5: EXPERIENCIA AP5
    # ---------------------------------------------------------
    with tab_ap5:
        st.header("💻 Evaluación de Experiencia AP5")
        
        st.dataframe(df_ap5, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error al conectar o procesar las bases de datos: {e}")
