import streamlit as st
import pandas as pd

# 1. Configuración general
st.set_page_config(page_title="Tablero Unificado de Experiencia (VoC)", layout="wide")
st.title("📊 Tablero Unificado de Voz del Cliente & Experiencia")

# 2. URLs de tus 5 bases de datos en formato CSV
URL_NPS_RELACIONAL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQkRId_MTUvXjEoeQoB5DRTVBy5LZSBwFJLnCD9tIkXu5mLLUWKuMfZYli95RWhZQBVhD0DiLqcr9fY/pub?output=csv"
URL_AUDITORIA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSqX6kWb9zVRCqouqL9yE-gkhcODTU-rNKGHs4uaGBXKIvAZv8I4xc2a3yoi1jrBJmXhSP1HSbsnLFD/pub?output=csv"
URL_ATENCION = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1I2VSwaUgunJRLpWFwFGor26ckwmHTPtN6H6alVnOx_tOshcvbzjMaA4h_-zPGJS-NC9KQWqTSNHp/pub?output=csv"
URL_AP5 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTbFTv5ei5f-lzMBdRGx3nCnT8RZw3va6OPQN2s_wmZjmpcoSWG82scnWt2hcjjEF-LB0VIJ1cQYmVN/pub?output=csv"
URL_ENTREVISTAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRvvHxl-4IdjWueWBr-rYnplVQUB5tOrLTjG0HS81zwjDqmHJ1Bn_NsbB0egePmOR8u3OadKPnR_1bW/pub?output=csv"

# Carga de datos con caché
@st.cache_data(ttl=15)
def load_data():
    df_nps = pd.read_csv(URL_NPS_RELACIONAL)
    df_auditoria = pd.read_csv(URL_AUDITORIA)
    df_atencion = pd.read_csv(URL_ATENCION)
    df_ap5 = pd.read_csv(URL_AP5)
    df_entrevistas = pd.read_csv(URL_ENTREVISTAS)
    return df_nps, df_auditoria, df_atencion, df_ap5, df_entrevistas

try:
    df_nps, df_auditoria, df_atencion, df_ap5, df_entrevistas = load_data()

    # Auxiliar para calcular NPS
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
    tab_global, tab_nps, tab_auditoria, tab_atencion, tab_ap5, tab_entrevistas = st.tabs([
        "🌐 Resumen Unificado", 
        "🏢 NPS Relacional", 
        "📋 Auditoría", 
        "🎧 Atención al Cliente", 
        "💻 Experiencia AP5",
        "🗣️ Entrevistas a Clientes"
    ])

    # ---------------------------------------------------------
    # TAB 1: RESUMEN UNIFICADO (CON MOTIVOS DE PROMOTORES Y VERBATIMS)
    # ---------------------------------------------------------
    with tab_global:
        st.header("Vista Macro de Mediciones & Voz del Cliente")
        
        # Tarjetas de Métricas de Volumen
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("NPS Relacional", len(df_nps))
        c2.metric("Auditorías", len(df_auditoria))
        c3.metric("Atención Cliente", len(df_atencion))
        c4.metric("Exp. AP5", len(df_ap5))
        c5.metric("Entrevistas", len(df_entrevistas))
        
        st.markdown("---")
        
        # Fila 1: Métricas NPS y Contactos Solicitados
        col_nps_box, col_contact_box = st.columns(2)
        with col_nps_box:
            st.subheader("NPS Relacional General")
            if 'p3. NPS' in df_nps.columns:
                val_nps, prom, pas, det = calcular_nps(df_nps['p3. NPS'])
                st.metric("NPS Score", f"{val_nps}%")
                st.write(f"🟢 **Promotores (9-10):** {prom} | 🟡 **Pasivos (7-8):** {pas} | 🔴 **Detractores (0-6):** {det}")
            else:
                st.warning("Columna 'p3. NPS' no encontrada.")

        with col_contact_box:
            st.subheader("Solicitudes de Contacto Pendientes")
            contact_nps = len(df_nps[df_nps['p35 ¿Te gustaría ser contactado por un representante?'].astype(str).str.lower().str.contains("sí|si", na=False)]) if 'p35 ¿Te gustaría ser contactado por un representante?' in df_nps.columns else 0
            contact_ap5 = len(df_ap5[df_ap5['quiere ser contactado'].astype(str).str.lower().str.contains("sí|si", na=False)]) if 'quiere ser contactado' in df_ap5.columns else 0
            st.metric("Total Solicitudes de Contacto", contact_nps + contact_ap5)
            st.caption(f"NPS Relacional: {contact_nps} | Exp. AP5: {contact_ap5}")

        st.markdown("---")
        
        # Fila 2: Motivos de Promotores (NPS 9 y 10) y Verbatims de Entrevistas
        col_promotores, col_verbatims = st.columns(2)
        
        with col_promotores:
            st.subheader("⭐ Principales Motivos de Promotores (NPS 9-10)")
            if 'p3. NPS' in df_nps.columns and 'p4. Motivo principal' in df_nps.columns:
                # Filtrar solo notas 9 y 10
                df_promotores = df_nps[pd.to_numeric(df_nps['p3. NPS'], errors='coerce') >= 9]
                motivos_prom = df_promotores['p4. Motivo principal'].value_counts().reset_index()
                motivos_prom.columns = ['Motivo Principal', 'Cantidad']
                
                if not motivos_prom.empty:
                    st.bar_chart(motivos_prom.set_index('Motivo Principal'))
                    st.dataframe(motivos_prom, use_container_width=True, hide_index=True)
                else:
                    st.info("No hay suficientes datos de promotores aún.")
            else:
                st.info("No se hallaron las columnas 'p3. NPS' o 'p4. Motivo principal'.")

        with col_verbatims:
            st.subheader("🗣️ Verbatims Destacados de Entrevistas")
            if 'verbating' in df_entrevistas.columns:
                # Mostrar los verbatims en tarjetas interactivas
                df_verbatims_clean = df_entrevistas.dropna(subset=['verbating'])
                if not df_verbatims_clean.empty:
                    st.caption("Extractos directos de conversaciones profundas con clientes:")
                    # Mostrar las últimas 4 citas destacadas
                    for idx, row in df_verbatims_clean.tail(4).iterrows():
                        cliente_str = f" - **{row['cliente']}**" if 'cliente' in row and pd.notna(row['cliente']) else ""
                        st.info(f"💬 \"{row['verbating']}\"{cliente_str}")
                else:
                    st.info("No hay verbatims cargados en la base de entrevistas.")
            else:
                st.warning("Columna 'verbating' no encontrada en la base de entrevistas.")

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

    # ---------------------------------------------------------
    # TAB 6: ENTREVISTAS A CLIENTES (NUEVA PESTAÑA)
    # ---------------------------------------------------------
    with tab_entrevistas:
        st.header("🗣️ Entrevistas Profundas a Clientes")
        
        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            if 'cliente' in df_entrevistas.columns:
                clientes_opt = ["Todos"] + list(df_entrevistas['cliente'].dropna().unique())
                cli_sel = st.selectbox("Filtrar por Cliente:", options=clientes_opt)
            else:
                cli_sel = "Todos"
                
        with col_filtro2:
            if 'colaborador' in df_entrevistas.columns:
                colab_opt = ["Todos"] + list(df_entrevistas['colaborador'].dropna().unique())
                colab_sel = st.selectbox("Filtrar por Colaborador/Entrevistador:", options=colab_opt)
            else:
                colab_sel = "Todos"

        # Aplicar Filtros
        df_ent_filtered = df_entrevistas
        if cli_sel != "Todos":
            df_ent_filtered = df_ent_filtered[df_ent_filtered['cliente'] == cli_sel]
        if colab_sel != "Todos":
            df_ent_filtered = df_ent_filtered[df_ent_filtered['colaborador'] == colab_sel]

        st.dataframe(
            df_ent_filtered[['entrevista', 'cliente', 'colaborador', 'verbating']], 
            use_container_width=True, 
            hide_index=True
        )

except Exception as e:
    st.error(f"Error al conectar o procesar las bases de datos: {e}")
