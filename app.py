import streamlit as st
import pandas as pd
import io

# --- IMPORTS DE TU LÓGICA ---
import logic.utils as utils 
from logic.config import MAPA_TITULACIONES
from logic.obtener_datos_subgrupo import obtener_datos_subgrupo
from logic.generar_resumen_datos import generar_resumen_datos
from logic.generar_partes_docentes import generar_partes_docentes
from logic.genera_graficas import genera_graficas
# NUEVO IMPORT PARA EL POWERPOINT
from logic.generar_ppt import generar_ppt 

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Dashboard Calidad Docente",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Generador de Informes de Calidad Docente")
st.markdown("""
Esta aplicación procesa las encuestas docentes, genera visualizaciones y permite descargar 
el informe final en formato Word y la presentación en PowerPoint.
""")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("Configuración")
    
    # 1. Subida de Archivo de Datos
    uploaded_file = st.file_uploader("1. Cargar Excel de Encuestas", type=["xlsx", "xls"])
    
    # NUEVO: Subida de Plantilla PPT
    plantilla_ppt = st.file_uploader("2. Cargar Plantilla PPTX (Opcional)", type=["pptx"])
    
    st.markdown("---")
    
    # 2. Selectores
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
            
            # Preparar fechas 
            f_inicio_str = fecha_inicio.strftime('%d-%m-%Y')
            f_fin_str = fecha_fin.strftime('%d-%m-%Y') if fecha_fin else None
            
            # Filtramos el DataFrame completo
            df_filtrado = utils.filtrar_por_fechas(df_raw, f_inicio_str, f_fin_str)
            
            # Obtenemos solo los datos de la titulación seleccionada
            df_subgrupo = obtener_datos_subgrupo(df_filtrado, titulacion_seleccionada)
        
        # Verificación de resultados
        if df_subgrupo is not None and not df_subgrupo.empty:
            
            # Generación de Resumen Numérico
            df_resumen = generar_resumen_datos(df_subgrupo)
            
            # --- TABS DE RESULTADOS ---
            tab1, tab2, tab3 = st.tabs(["📋 Datos y KPIs", "📈 Gráficas", "📥 Exportar Informes"])
            
            # TAB 1: DATOS
            with tab1:
                st.subheader(f"Datos: {titulacion_seleccionada}")
                
                # Métricas rápidas (KPIs)
                col1, col2 = st.columns(2)
                total_asignaturas = len(df_resumen)
                media_aprobados = df_resumen['% Aprobados'].mean() if not df_resumen.empty else 0
                
                col1.metric("Asignaturas Procesadas", total_asignaturas)
                col2.metric("Media % Aprobados", f"{media_aprobados:.2f}%")
                
                # Tabla Interactiva
                st.dataframe(df_resumen) 

            # TAB 2: GRÁFICAS
            with tab2:
                st.subheader("Visualización de Resultados")
                
                if st.button("Generar Gráficas de Análisis"):
                    with st.spinner("Generando gráficas..."):
                        lista_figuras = genera_graficas(df_resumen)
                        
                        if lista_figuras:
                            for titulo, fig in lista_figuras:
                                st.markdown(f"### {titulo}")
                                st.pyplot(fig)
                        else:
                            st.warning("No hay datos suficientes para generar las gráficas.")

            # TAB 3: EXPORTAR (WORD Y PPT)
            with tab3:
                st.subheader("Generación de Documentos")
                
                # Dividimos en dos columnas para Word y PPT
                col_word, col_ppt = st.columns(2)
                
                # --- COLUMNA 1: WORD ---
                with col_word:
                    st.markdown("### 📄 Informe Word")
                    st.info("Informe detallado con tablas y comentarios.")
                    
                    # Generamos el Word en memoria
                    buffer_word = generar_partes_docentes(df_subgrupo)
                    
                    st.download_button(
                        label="Descargar Informe .DOCX",
                        data=buffer_word,
                        file_name=f"Informe_Calidad_{titulacion_seleccionada}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="btn_word" # Clave única
                    )
                
                # --- COLUMNA 2: POWERPOINT ---
                with col_ppt:
                    st.markdown("### 📊 Presentación PowerPoint")
                    st.info("Presentación ejecutiva con gráficas y resumen.")
                    
                    # Botón para generar el PPT (consume recursos, así que lo hacemos bajo demanda)
                    if st.button("Preparar PowerPoint", key="btn_prep_ppt"):
                        with st.spinner("Generando diapositivas y gráficas..."):
                            # 1. Necesitamos las figuras para el PPT (las regeneramos para asegurar que estén frescas)
                            figs_para_ppt = genera_graficas(df_resumen)
                            
                            # 2. Generamos el archivo PPT
                            buffer_ppt = generar_ppt(df_resumen, figs_para_ppt, plantilla_ppt)
                            
                            # 3. Botón de descarga (aparece tras generarse)
                            st.success("✅ Presentación lista")
                            st.download_button(
                                label="Descargar Presentación .PPTX",
                                data=buffer_ppt,
                                file_name=f"Presentacion_{titulacion_seleccionada}.pptx",
                                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                key="btn_down_ppt"
                            )
                
        else:
            st.error("❌ No se encontraron datos.")
            st.warning(f"Revisa que la titulación '{titulacion_seleccionada}' tenga datos en el rango de fechas seleccionado.")

    except Exception as e:
        st.error("Ocurrió un error inesperado:")
        st.exception(e)
else:
    st.info("👋 Por favor, carga un archivo Excel en la barra lateral para comenzar.")
