import streamlit as st
import pandas as pd
import io

# --- IMPORTS DE TU LÓGICA ---
# Usamos el alias 'utils' para evitar el error 'name utils is not defined'
import logic.utils as utils 
from logic.config import MAPA_TITULACIONES
from logic.obtener_datos_subgrupo import obtener_datos_subgrupo
from logic.generar_resumen_datos import generar_resumen_datos
from logic.generar_partes_docentes import generar_partes_docentes
from logic.genera_graficas import genera_graficas

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Dashboard Calidad Docente",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Generador de Informes de Calidad Docente")
st.markdown("""
Esta aplicación procesa las encuestas docentes, genera visualizaciones y permite descargar 
el informe final en formato Word.
""")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("Configuración")
    
    # 1. Subida de Archivo
    uploaded_file = st.file_uploader("Cargar Excel de Encuestas", type=["xlsx", "xls"])
    
    st.markdown("---")
    
    # 2. Selectores
    # Obtenemos las claves del diccionario config.py
    titulaciones_disponibles = list(MAPA_TITULACIONES.keys())
    titulacion_seleccionada = st.selectbox("Seleccionar Titulación/Grupo", titulaciones_disponibles)
    
    # 3. Filtro Fechas
    fecha_inicio = st.date_input("Fecha Inicio Filtro", value=pd.to_datetime("2024-01-01"))
    fecha_fin = st.date_input("Fecha Fin Filtro (Opcional)", value=None)

# --- LÓGICA PRINCIPAL ---
if uploaded_file is not None:
    try:
        # Carga de datos con spinner visual
        with st.spinner('Cargando y procesando archivo...'):
            df_raw = pd.read_excel(uploaded_file)
            
            # Preparar fechas (utils espera strings DD-MM-YYYY)
            f_inicio_str = fecha_inicio.strftime('%d-%m-%Y')
            f_fin_str = fecha_fin.strftime('%d-%m-%Y') if fecha_fin else None
            
            # Filtramos el DataFrame completo
            df_filtrado = utils.filtrar_por_fechas(df_raw, f_inicio_str, f_fin_str)
            
            # Obtenemos solo los datos de la titulación seleccionada
            df_subgrupo = obtener_datos_subgrupo(df_filtrado, titulacion_seleccionada)
        
        # Verificación de resultados
        if df_subgrupo is not None and not df_subgrupo.empty:
            
            # Generación de Resumen Numérico (Tabla limpia)
            df_resumen = generar_resumen_datos(df_subgrupo)
            
            # --- TABS DE RESULTADOS ---
            tab1, tab2, tab3 = st.tabs(["📋 Datos y KPIs", "📈 Gráficas", "📥 Exportar Informe"])
            
            # TAB 1: DATOS
            with tab1:
                st.subheader(f"Datos: {titulacion_seleccionada}")
                
                # Métricas rápidas (KPIs)
                col1, col2 = st.columns(2)
                total_asignaturas = len(df_resumen)
                # Calculamos media evitando errores si está vacío
                media_aprobados = df_resumen['% Aprobados'].mean() if not df_resumen.empty else 0
                
                col1.metric("Asignaturas Procesadas", total_asignaturas)
                col2.metric("Media % Aprobados", f"{media_aprobados:.2f}%")
                
                # Tabla Interactiva
                # CORRECCIÓN: Quitamos use_container_width para evitar el warning
                st.dataframe(df_resumen) 

            # TAB 2: GRÁFICAS
            with tab2:
                st.subheader("Visualización de Resultados")
                
                # Botón para generar gráficas solo si se pide (ahorra recursos)
                if st.button("Generar Gráficas de Análisis"):
                    with st.spinner("Generando gráficas..."):
                        # Llamamos a genera_graficas (que ahora devuelve una lista de figuras)
                        lista_figuras = genera_graficas(df_resumen)
                        
                        if lista_figuras:
                            # Mostramos las gráficas una tras otra
                            for titulo, fig in lista_figuras:
                                st.markdown(f"### {titulo}")
                                st.pyplot(fig)
                        else:
                            st.warning("No hay datos suficientes para generar las gráficas.")

            # TAB 3: EXPORTAR WORD
            with tab3:
                st.subheader("Generación de Documentos")
                st.info("Genera un informe Word completo con portada, tablas de datos y comentarios.")
                
                # Generamos el Word en memoria (RAM)
                buffer_word = generar_partes_docentes(df_subgrupo)
                
                # Botón de descarga
                st.download_button(
                    label="📄 Descargar Informe .DOCX",
                    data=buffer_word,
                    file_name=f"Informe_Calidad_{titulacion_seleccionada}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
        else:
            st.error("❌ No se encontraron datos.")
            st.warning(f"Revisa que la titulación '{titulacion_seleccionada}' tenga datos en el rango de fechas seleccionado.")

    except Exception as e:
        st.error("Ocurrió un error inesperado:")
        st.exception(e) # Muestra el error técnico de forma más clara
else:
    # Mensaje inicial
    st.info("👋 Por favor, carga un archivo Excel en la barra lateral para comenzar.")
