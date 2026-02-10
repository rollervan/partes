import io
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

def df_to_ppt_table(slide, df, left, top, width, height):
    """
    Función auxiliar para dibujar una tabla de pandas dentro de una slide.
    """
    rows, cols = df.shape
    # Crear la forma de la tabla
    table_shape = slide.shapes.add_table(rows + 1, cols, left, top, width, height)
    table = table_shape.table

    # --- 1. CABECERAS ---
    for col_idx, col_name in enumerate(df.columns):
        cell = table.cell(0, col_idx)
        cell.text = str(col_name)
        # Formato básico de cabecera
        cell.text_frame.paragraphs[0].font.bold = True
        cell.text_frame.paragraphs[0].font.size = Pt(10)
        cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    # --- 2. DATOS ---
    for row_idx, row in df.iterrows():
        for col_idx, value in enumerate(row):
            cell = table.cell(row_idx + 1, col_idx)
            val_str = str(value)
            
            # Formateo si es float
            if isinstance(value, float):
                val_str = f"{value:.2f}"
            
            cell.text = val_str
            cell.text_frame.paragraphs[0].font.size = Pt(9)
            cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

def generar_ppt(df, lista_figuras, ruta_plantilla=None):
    """
    Genera una presentación PPTX.
    df: DataFrame resumen con los datos.
    lista_figuras: Lista [(titulo, fig), ...] que viene de genera_graficas.
    ruta_plantilla: Ruta al archivo .pptx base. Si es None, usa una en blanco.
    """
    
    # 1. Cargar presentación (Plantilla o Nueva)
    if ruta_plantilla:
        try:
            prs = Presentation(ruta_plantilla)
        except:
            prs = Presentation() # Fallback si no encuentra la plantilla
    else:
        prs = Presentation()

    # --- DATOS PARA PORTADA ---
    # Intentamos sacar el título de la titulación del propio DF (columna 5 o similar, o la que usamos para filtrar)
    # Como el DF resumen ya está procesado, asumimos que viene del df_raw o usamos un título genérico
    # Si 'df' es el resumen, buscamos columnas clave.
    titulo_informe = "Informe de Calidad Docente"
    subtitulo = "Análisis de Resultados"
    
    # Intentamos obtener información de la primera fila si existe
    if not df.empty:
        # Buscamos si hay columna 'Titulación' o 'Asignatura' para usar de contexto
        cols_str = " ".join(df.columns)
        if "Asignatura" in df.columns:
            # Si es un resumen de varias asignaturas, ponemos el nombre de la primera como ejemplo o genérico
            subtitulo = f"Análisis de {len(df)} asignaturas procesadas"

    # --- SLIDE 1: PORTADA ---
    # Layout 0 suele ser "Title Slide"
    slide_layout = prs.slide_layouts[0] 
    slide = prs.slides.add_slide(slide_layout)
    
    # Rellenar marcadores (Placeholders)
    # Normalmente: placeholder[0] = Título, placeholder[1] = Subtítulo
    try:
        slide.placeholders[0].text = titulo_informe
        slide.placeholders[1].text = subtitulo
    except:
        pass # Si la plantilla no tiene placeholders estándar, no fallamos

    # --- SLIDE 2: TABLA DE DATOS ---
    # Layout 5 suele ser "Title Only" (perfecto para poner una tabla grande)
    slide_layout = prs.slide_layouts[5] 
    slide = prs.slides.add_slide(slide_layout)
    
    try:
        slide.shapes.title.text = "Resumen de Datos Académicos"
    except:
        pass

    # Insertar tabla (ajustar dimensiones según necesidad)
    # Left, Top, Width, Height
    df_to_ppt_table(slide, df.head(15), Inches(0.5), Inches(1.5), Inches(9), Inches(5))
    # Nota: Solo ponemos las primeras 15 filas para que no se salga de la slide.

    # --- SLIDES 3+: GRÁFICAS ---
    # Usamos layout 5 (Title Only) o 1 (Title and Content)
    # Aquí es donde ocurre la MAGIA de convertir matplotlib a PPT
    for titulo_grafica, figura in lista_figuras:
        slide_layout = prs.slide_layouts[5] # Solo título
        slide = prs.slides.add_slide(slide_layout)
        
        # Poner título
        try:
            slide.shapes.title.text = titulo_grafica
        except:
            pass
        
        # Convertir figura de Matplotlib a imagen en memoria
        image_stream = io.BytesIO()
        figura.savefig(image_stream, format='png', bbox_inches='tight', dpi=150)
        image_stream.seek(0)
        
        # Insertar imagen en la slide
        # Ajustamos posición y tamaño (Left=1pulgada, Top=1.5pulgadas)
        slide.shapes.add_picture(image_stream, Inches(1), Inches(1.5), width=Inches(8))

    # --- GUARDAR Y RETORNAR ---
    output = io.BytesIO()
    prs.save(output)
    output.seek(0)
    
    return output
