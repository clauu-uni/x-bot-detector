import streamlit as st
import pandas as pd
import requests
import time
from fpdf import FPDF

def generar_pdf_informe(metricas):
    # 1. Extraer datos y calcular porcentajes
    total = metricas['total']
    bots = metricas['bots']
    humanos = metricas['humanos']
    
    pct_bots = (bots / total * 100) if total > 0 else 0
    pct_humanos = (humanos / total * 100) if total > 0 else 0

    # 2. Lógica de recomendaciones según el nivel de amenaza
    if pct_bots < 10:
        nivel_riesgo = "BAJO"
        recomendacion = "Tu audiencia parece muy saludable y orgánica. Sigue manteniendo tus estrategias actuales de interacción. No se requieren acciones urgentes."
    elif pct_bots < 30:
        nivel_riesgo = "MEDIO"
        recomendacion = "Se ha detectado una presencia moderada de tráfico sintetico. Sería recomendable auditar a los seguidores más recientes y limpiar cuentas inactivas para mejorar el engagement."
    else:
        nivel_riesgo = "ALTO"
        recomendacion = "¡ALERTA! Tu base de datos tiene una alta concentración de bots. Te recomendamos urgentemente pausar campanas de captación pagadas y realizar una purga de seguidores para no dañar la reputación de la cuenta."

    # 3. Dibujar el PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Título principal
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="INFORME DE AUDITORIA - AUTENTIX", ln=True, align='C')
    pdf.ln(10) # Salto de línea
    
    # Bloque de Métricas
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="1. Resumen de Metricas", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"- Total de perfiles analizados: {total}", ln=True)
    pdf.cell(200, 10, txt=f"- Humanos detectados: {humanos} ({pct_humanos:.1f}%)", ln=True)
    pdf.cell(200, 10, txt=f"- Bots detectados: {bots} ({pct_bots:.1f}%)", ln=True)
    pdf.ln(10)
    
    # Bloque de Recomendaciones
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"2. Diagnostico (Nivel de Riesgo: {nivel_riesgo})", ln=True)
    pdf.set_font("Arial", '', 12)
    # multi_cell permite que el texto largo salte de línea automáticamente
    pdf.multi_cell(0, 10, txt=f"Recomendacion corporativa: {recomendacion}") 

    # 4. Empaquetar el PDF en bytes para que Streamlit lo pueda descargar
    return pdf.output(dest='S').encode('latin-1')


# Configuración de la página
st.set_page_config(page_title="AutentiX B2B - Panel Corporativo", page_icon="icon.png", layout="wide")

# URL de tu API local (oculta de la interfaz para mantener el diseño limpio)
URL_API = "http://localhost:8000/predict"

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    /* Encabezado Principal */
    .main-header {
        background-color: #E8F6FE;
        padding: 40px;
        border-radius: 20px;
        margin-bottom: 40px;
    }
    .main-title {
        color: #38BDF8;
        font-size: 3.5rem;
        font-weight: 900;
        font-style: italic;
        margin-bottom: 0px;
        line-height: 1.1;
    }
    .main-subtitle {
        color: #38BDF8;
        font-size: 1.5rem;
        font-weight: 700;
        font-style: italic;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .main-text {
        color: #475569;
        font-size: 1.1rem;
        max-width: 800px;
    }
    
    /* Separadores de Pasos */
    .step-header {
        color: #94A3B8;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }
    .step-header::before {
        content: "";
        display: inline-block;
        width: 30px;
        height: 2px;
        background-color: #38BDF8;
        margin-right: 10px;
    }

    /* Tarjetas de Sensibilidad y Métricas */
    .custom-card {
        background-color: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 15px 20px;
        height: 100%;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .metric-title {
        color: #94A3B8;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0F172A;
    }
    .alert-text { 
        color: #EF4444; 
        font-size: 1rem;
        font-weight: 900; 
        font-style: italic;
    }
    
    /* Estilos para teñir el desplegable (Expander) */
    [data-testid="stExpander"] details summary {
        background-color: #E8F6FE;
        color: #38BDF8;
        font-weight: 800;
        border-radius: 10px;
        padding: 10px 15px;
        border: none;
    }
    [data-testid="stExpander"] {
        border: none;
        box-shadow: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DEL ESTADO DE LA SESIÓN ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
if 'df_resultados' not in st.session_state:
    st.session_state.df_resultados = None
if 'csv_descarga' not in st.session_state:
    st.session_state.csv_descarga = None
if 'metricas' not in st.session_state:
    st.session_state.metricas = {}

# --- ENCABEZADO COMÚN ---
st.markdown("""
    <div class="main-header">
        <div class="main-title">AUTENTIX</div>
        <div class="main-subtitle">Análisis masivo de audiencias y detección de tráfico sintético</div>
        <div class="main-text">Esta herramienta permite a las empresas analizar bases de datos completas de usuarios de X (Twitter). Sube tu archivo CSV o Excel con los datos de los perfiles para obtener un informe de autenticidad.</div>
    </div>
""", unsafe_allow_html=True)


# ==========================================
# PASO 1: CARGA DE DATOS Y CONFIGURACIÓN
# ==========================================
if st.session_state.paso == 1:
    st.markdown('<div class="step-header">PASO 1: CARGA DE DATOS</div>', unsafe_allow_html=True)
    
    col_upload, col_settings = st.columns([1.5, 1], gap="large")
    
    with col_upload:
        archivo_subido = st.file_uploader("Haz clic para subir o arrastra y suelta (CSV O EXCEL)", type=["csv", "xlsx"])
        
    with col_settings:
        
        # 1. Título de la sección
        st.markdown(
            "<br><span style='color:#94A3B8; font-weight:bold; letter-spacing:1px; font-size:0.9rem;'>SENSIBILIDAD</span>",
            unsafe_allow_html=True
        )
            
        # 2. Texto descriptivo
        st.markdown(
            "<p style='color:#64748B; font-size:0.8rem; font-style:italic; margin-top:-10px;'>DEFINE EL NIVEL DE EXIGENCIA PARA MARCAR UN PERFIL COMO BOT.</p>",
            unsafe_allow_html=True
        )

        # 3. Control deslizante (slider)
        umbral_bot = st.slider(
            "Sensibilidad",
            0,
            100,
            st.session_state.get("umbral_bot", 50),
            label_visibility="collapsed"
        )

        st.session_state.umbral_bot = umbral_bot


    st.write("") # Espaciador
    
    # Lógica de procesamiento
    if archivo_subido is not None:
        if archivo_subido.name.endswith('.csv'):
            df = pd.read_csv(archivo_subido)
        else:
            df = pd.read_excel(archivo_subido)
            
        if st.button("🚀 Iniciar Análisis Masivo", use_container_width=True):
            resultados = []
            barra_progreso = st.progress(0)
            texto_estado = st.empty()

            for index, fila in df.iterrows():
                porcentaje = (index + 1) / len(df)
                barra_progreso.progress(porcentaje)
                texto_estado.text(f"Analizando perfil {index + 1} de {len(df)}...")

                # Preparar datos
                payload = {
                    "screen_name": str(fila.get('screen_name', 'unknown')),
                    "followers_count": int(fila.get('followers_count', 0)),
                    "following_count": int(fila.get('following_count', 0)),
                    "favourites_count": int(fila.get('favourites_count', 0)),
                    "created_at": str(fila.get('created_at', 'Desconocida')),
                    "account_age_days": 1000,
                    "default_profile_image": bool(fila.get('default_profile_image', False)),
                    "default_profile": bool(fila.get('default_profile', False)),
                    "has_description": True if str(fila.get('description', '')).strip() else False,
                    "description": str(fila.get('description', '')),
                    "verified": bool(fila.get('verified', False)),
                    "has_lang": True,
                    "lang": "es",
                    "location": str(fila.get('location', '')),
                    "statuses_count": int(fila.get('statuses_count', 0)),
                    "average_tweets_per_day": 1.5,
                    "geo_enabled": True if str(fila.get('location', '')).strip() else False,
                    "id": int(fila.get('id', 0))
                }

                try:
                    r = requests.post(URL_API, json=payload)
                    res = r.json()
                    prob = round(res['bot_probability'] * 100, 1)
                    resultados.append({
                        "USUARIO": f"@{payload['screen_name']}",
                        "SEGUIDORES": payload['followers_count'],
                        "SEGUIDOS": payload['following_count'], # <--- NUEVO
                        "LIKES DADOS": payload['favourites_count'], # <--- NUEVO
                        "VERIFICADO": "✅" if payload['verified'] else "❌", # <--- NUEVO
                        "PROB. BOT (%)": prob,
                        "VEREDICTO": "🤖 BOT" if prob > umbral_bot else "👤 HUMANO"
                    })
                except Exception as e:
                    resultados.append({
                        "USUARIO": f"@{payload['screen_name']}",
                        "SEGUIDORES": payload['followers_count'],
                        "SEGUIDOS": payload['following_count'],
                        "LIKES DADOS": payload['favourites_count'],
                        "VERIFICADO": "❓",
                        "PROB. BOT (%)": 0.0,
                        "VEREDICTO": "❌ ERROR API"
                    })

            # Guardar resultados y cambiar al Paso 2
            df_final = pd.DataFrame(resultados)
            st.session_state.df_resultados = df_final
            st.session_state.csv_descarga = df_final.to_csv(index=False).encode('utf-8')
            
            bots_count = len(df_final[df_final['VEREDICTO'] == "🤖 BOT"])
            st.session_state.metricas = {
                "total": len(df_final),
                "bots": bots_count,
                "humanos": len(df_final) - bots_count
            }
            
            st.session_state.paso = 2
            st.rerun()

# ==========================================
# PASO 2: INFORME DE AUDITORÍA
# ==========================================
elif st.session_state.paso == 2:

    # --- DEFINICIÓN DEL POP-UP (MODAL DE DESCARGA) ---
    @st.dialog("📥 Opciones de Descarga")
    def modal_descarga():
        st.write("Selecciona qué perfiles quieres incluir en tu archivo CSV:")
        opcion = st.radio(
            "Filtro de descarga", 
            ["Todos los perfiles (Ambos)", "Solo Bots 🤖", "Solo Humanos 👤"],
            label_visibility="collapsed"
        )
        
        # Recuperar el DataFrame completo de la memoria
        df = st.session_state.df_resultados
        
        # Filtrar según la opción elegida
        if "Bots" in opcion:
            df_descarga = df[df['VEREDICTO'] == "🤖 BOT"]
            nombre_archivo = "autentix_solo_bots.csv"
        elif "Humanos" in opcion:
            df_descarga = df[df['VEREDICTO'] == "👤 HUMANO"]
            nombre_archivo = "autentix_solo_humanos.csv"
        else:
            df_descarga = df
            nombre_archivo = "autentix_completo.csv"
            
        # Generar el nuevo CSV al vuelo
        csv_generado = df_descarga.to_csv(index=False).encode('utf-8')
        
        st.markdown(f"<span style='color: #64748B; font-size: 0.9rem;'><i>Se exportarán {len(df_descarga)} filas.</i></span>", unsafe_allow_html=True)
        st.write("")
        
        # Botón definitivo de descarga
        st.download_button(
            label="✅ Confirmar y Descargar",
            data=csv_generado,
            file_name=nombre_archivo,
            mime='text/csv',
            use_container_width=True
        )

    # --- CABECERA Y BOTONES SUPERIORES ---
    col_title, col_btns = st.columns([1, 1.5])
    with col_title:
        st.markdown('<div class="step-header">PASO 2: INFORME DE AUDITORÍA</div>', unsafe_allow_html=True)
    with col_btns:
        b1, b2, b3 = st.columns([1, 1.3, 1.5])
        with b1:
            if st.button("ANTERIOR", use_container_width=True):
                st.session_state.paso = 1
                st.rerun()
        with b2:
            # Ahora este botón abre la ventana emergente en lugar de descargar directamente
            if st.button("📥 DESCARGAR CSV", use_container_width=True):
                modal_descarga()
        with b3:
            # 1. Generamos el PDF usando los datos que guardamos en la memoria al analizar
            pdf_bytes = generar_pdf_informe(st.session_state.metricas)
            
            # 2. Creamos el botón nativo de descarga
            st.download_button(
                label="📄 DESCARGAR INFORME (PDF)",
                data=pdf_bytes,
                file_name='informe_ejecutivo_autentix.pdf',
                mime='application/pdf',
                use_container_width=True
            )

    st.write("") # Espaciador

    # --- DISTRIBUCIÓN: Izquierda (Métricas) y Derecha (Tabla) ---
    col_izq, col_der = st.columns([1, 2.5], gap="large")
    
    with col_izq:
        # Envolvemos todo dentro del desplegable y lo dejamos abierto por defecto
        with st.expander("MÉTRICAS", expanded=True):
            st.write("") # Pequeño espacio inicial
            
            # Tarjeta 1: Total
            st.markdown(f"""
                <div class="custom-card" style="margin-bottom: 10px;">
                    <div class="metric-title">👥 TOTAL ANALIZADOS</div>
                    <div class="metric-value">{st.session_state.metricas['total']}</div>
                </div>
            """, unsafe_allow_html=True)
                
            # Tarjeta 2: Bots
            st.markdown(f"""
                <div class="custom-card" style="margin-bottom: 10px;">
                    <div class="metric-title" style="display:flex; justify-content:space-between;">
                        <span>🤖 BOTS DETECTADOS</span>
                        <span class="alert-text">ALERTA</span>
                    </div>
                    <div class="metric-value">{st.session_state.metricas['bots']}</div>
                </div>
            """, unsafe_allow_html=True)
                
            # Tarjeta 3: Humanos
            st.markdown(f"""
                <div class="custom-card" style="margin-bottom: 5px;">
                    <div class="metric-title">👤 HUMANO SEGURO</div>
                    <div class="metric-value">{st.session_state.metricas['humanos']}</div>
                </div>
            """, unsafe_allow_html=True)

    with col_der:
        t_col1, t_col2 = st.columns([2, 1])
        with t_col1:
            st.markdown("### Resultados del Análisis")
        with t_col2:
            busqueda = st.text_input("🔍 Filtrar por usuario...", label_visibility="collapsed", placeholder="🔍 Filtrar por usuario...")

        # Filtrar DataFrame para la vista
        df_mostrar = st.session_state.df_resultados
        if busqueda:
            df_mostrar = df_mostrar[df_mostrar["USUARIO"].str.contains(busqueda, case=False, na=False)]

        # Mostrar tabla con la barra de progreso integrada y nuevas columnas
        st.dataframe(
            df_mostrar,
            column_config={
                "USUARIO": st.column_config.TextColumn("USUARIO", width="medium"),
                "SEGUIDORES": st.column_config.NumberColumn("SEGUIDORES", format="%d"),
                "SEGUIDOS": st.column_config.NumberColumn("SEGUIDOS", format="%d"),
                "VERIFICADO": st.column_config.TextColumn("VERIFICADO", width="small"),
                "PROB. BOT (%)": st.column_config.ProgressColumn(
                    "PROB. BOT (%)",
                    help="Probabilidad de que el perfil sea tráfico sintético",
                    format="%f%%",
                    min_value=0,
                    max_value=100,
                ),
                "VEREDICTO": st.column_config.TextColumn("VEREDICTO"),
            },
            hide_index=True,
            use_container_width=True
        )