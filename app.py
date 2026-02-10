import streamlit as st
import pandas as pd
import io

# Importamos tu lógica (asumiendo que moviste los archivos a la carpeta logic)
from logic import config, utils, obtener_datos_subgrupo, generar_resumen_datos, generar_partes_docentes, genera_graficas

st.set_page_config(page_title="Dashboard Docente", layout="wide")

st.title("📊 Generador de Informes Docentes")

# --- SIDEBAR: INPUTS ---
with st.sidebar:
    st.header("Configuración")
    uploaded_file = st.file_uploader("Cargar Excel de Encuestas", type=["xlsx", "xls"])
    
    # Selector dinámico basado en tu config.py
    opciones_titulacion = list(config.MAPA_TITULACIONES.keys())
    seleccion = st.selectbox("Seleccionar Titulación/Subgrupo", opciones_titulacion)
    
    fecha_inicio = st.date_input("Fecha Inicio Filtro")

# --- LOGIC ---
if uploaded_file is not None:
    try:
        # 1. Cargar DF
        df_raw = pd.read_excel(uploaded_file)
        
        # 2. Filtrar por fecha (utils.py)
        # Nota: Asegúrate de convertir el input de fecha al formato que espera tu utils
        df_filtrado = utils.filtrar_por_fechas(df_raw, fecha_inicio.strftime('%d-%m-%Y'))
        
        # 3. Obtener Subgrupo (obtener_datos_subgrupo.py)
        df_subgrupo = obtener_datos_subgrupo.obtener_datos_subgrupo(df_filtrado, seleccion)
        
        if df_subgrupo is not None and not df_subgrupo.empty:
            
            # 4. Generar Resumen (generar_resumen_datos.py)
            df_resumen = generar_resumen_datos.generar_resumen_datos(df_subgrupo)
            
            # --- TABS DE VISUALIZACIÓN ---
            tab1, tab2, tab3 = st.tabs(["📋 Datos", "📈 Gráficas", "📥 Descargas"])
            
            with tab1:
                st.subheader(f"Resumen: {seleccion}")
                st.dataframe(df_resumen, use_container_width=True)
                
            with tab2:
                st.subheader("Análisis Visual")
                if st.button("Generar Gráficas"):
                    # Aquí adaptaríamos tu script para mostrar las graficas
                    # Por ahora, simulamos que tu script guarda en carpeta 'output'
                    genera_graficas.genera_graficas(df_resumen, carpeta_salida="temp_img")
                    st.success("Gráficas generadas (adaptar lógica para mostrar aquí)")
                    # Aquí podrías cargar las imágenes de la carpeta temp y mostrarlas
            
            with tab3:
                st.subheader("Generar Informe Word")
                # Botón para procesar el Word en memoria
                buffer = io.BytesIO()
                # Nota: Requieres adaptar generar_partes_docentes para que guarde en buffer
                # generar_partes_docentes.generar_con_buffer(df_subgrupo, buffer)
                
                st.download_button(
                    label="📄 Descargar Informe DOCX",
                    data=buffer, # Esto requiere la adaptación mencionada
                    file_name=f"Informe_{seleccion}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        else:
            st.error("No se encontraron datos para la selección y filtros actuales.")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo Excel para comenzar.")
