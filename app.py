import streamlit as st
import pandas as pd
import io

# Importación de módulos locales
# Asegúrate de que todos los archivos .py estén en la misma carpeta o ajusta los imports
from logic.config import MAPA_TITULACIONES
import logic.utils
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
    titulaciones_disponibles = list(MAPA_TITULACIONES.keys())
    titulacion_seleccionada = st.selectbox("Seleccionar Titulación/Grupo", titulaciones_disponibles)
    
    # 3. Filtro Fechas
    fecha_inicio = st.date_input("Fecha Inicio Filtro", value=pd.to_datetime("2024-01-01"))
    fecha_fin = st.date_input("Fecha Fin Filtro (Opcional)", value=None)

# --- LÓGICA PRINCIPAL ---
if uploaded_file is not None:
    try:
        # Carga de datos
        with st.spinner('Cargando y procesando archivo...'):
            df_raw = pd.read_excel(uploaded_file)
            
            # Filtro por fechas (utils.py)
            # Convertimos fechas de Streamlit a string si tu utils lo requiere, 
            # o pasamos objeto datetime si lo adaptaste. 
            # Asumiendo tu utils espera string 'DD-MM-AAAA':
            f_inicio_str = fecha_inicio.strftime('%d-%m-%Y')
            f_fin_str = fecha_fin.strftime('%d-%m-%Y') if fecha_fin else None
            
            df_filtrado = utils.filtrar_por_fechas(df_raw, f_inicio_str, f_fin_str)
            
            # Obtención del Subgrupo
            df_subgrupo = obtener_datos_subgrupo(df_filtrado, titulacion_seleccionada)
        
        # Verificación de resultados
        if df_subgrupo is not None and not df_subgrupo.empty:
            
            # Generación de Resumen Numérico
            df_resumen = generar_resumen_datos(df_subgrupo)
            
            # --- TABS DE RESULTADOS ---
            tab1, tab2, tab3 = st.tabs(["📋 Datos y KPIs", "📈 Gráficas", "📥 Exportar Informe"])
            
            # TAB 1: DATOS
            with tab1:
                st.subheader(f"Datos: {titulacion_seleccionada}")
                
                # Métricas rápidas
                col1, col2, col3 = st.columns(3)
                total_asignaturas = len(df_resumen)
                media_aprobados = df_resumen['% Aprobados'].mean()
                
                col1.metric("Asignaturas", total_asignaturas)
                col2.metric("Media Aprobados", f"{media_aprobados:.2f}%")
                
                # Tabla Interactiva
                st.dataframe(df_resumen, use_container_width=True)

            # TAB 2: GRÁFICAS
            with tab2:
                st.subheader("Visualización de Resultados")
                
                if st.button("Generar Gráficas de Análisis"):
                    with st.spinner("Generando gráficas..."):
                        # Llamamos a la función modificada que devuelve lista de figuras
                        lista_figuras = genera_graficas(df_resumen)
                        
                        if lista_figuras:
                            # Mostramos las gráficas en grid
                            for titulo, fig in lista_figuras:
                                st.markdown(f"**{titulo}**")
                                st.pyplot(fig)
                        else:
                            st.warning("No se pudieron generar gráficas con los datos actuales.")

            # TAB 3: EXPORTAR
            with tab3:
                st.subheader("Generación de Documentos")
                st.info("Genera un informe Word completo con portada, tablas de datos y comentarios cualitativos.")
                
                # Botón de descarga
                # Procesamos el Word en memoria al momento de presionar, o lo preparamos antes
                buffer_word = generar_partes_docentes(df_subgrupo)
                
                st.download_button(
                    label="📄 Descargar Informe .DOCX",
                    data=buffer_word,
                    file_name=f"Informe_Calidad_{titulacion_seleccionada}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
        else:
            st.error("❌ No se encontraron datos para la titulación seleccionada en el rango de fechas indicado.")
            st.warning("Verifica que las columnas del Excel coincidan con las definidas en 'config.py'.")

    except Exception as e:
        st.error("Ocurrió un error inesperado:")
        st.code(e)
else:
    # Mensaje de bienvenida si no hay archivo
    st.info("👋 Por favor, carga un archivo Excel en la barra lateral para comenzar.")
