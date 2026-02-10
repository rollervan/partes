import io
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

def limpiar_texto(texto):
    """Ayuda a normalizar textos para comparaciones"""
    if not texto: return ""
    return texto.strip().lower()

def buscar_diapositiva(prs, titulo_buscado):
    """Busca una slide que contenga el texto del título buscado."""
    titulo_buscado = limpiar_texto(titulo_buscado)
    
    for slide in prs.slides:
        if slide.shapes.title and slide.shapes.title.text:
            titulo_slide = limpiar_texto(slide.shapes.title.text)
            if titulo_buscado in titulo_slide:
                return slide
    return None

def df_to_ppt_table(slide, df, left, top, width, height):
    """Dibuja la tabla en la slide indicada."""
    # Limitamos filas para que no se salga de la diapo
    df_to_print = df.head(12) 
    rows, cols = df_to_print.shape
    
    table_shape = slide.shapes.add_table(rows + 1, cols, left, top, width, height)
    table = table_shape.table

    # Estilos básicos
    for col_idx, col_name in enumerate(df_to_print.columns):
        cell = table.cell(0, col_idx)
        cell.text = str(col_name)
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(9)
        p.alignment = PP_ALIGN.CENTER
        # Fondo gris claro para cabecera
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(220, 220, 220)

    for row_idx, row in df_to_print.iterrows():
        for col_idx, value in enumerate(row):
            cell = table.cell(row_idx + 1, col_idx)
            val_str = f"{value:.2f}" if isinstance(value, float) else str(value)
            cell.text = val_str
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(8)
            p.alignment = PP_ALIGN.CENTER

def agregar_placeholder_ia(slide, texto_marcador):
    """Añade un cuadro de texto visual indicando dónde irá la IA."""
    left = Inches(1)
    top = Inches(2.5)
    width = Inches(8)
    height = Inches(2)
    
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.text = f"[{texto_marcador}]"
    p = tf.paragraphs[0]
    p.font.color.rgb = RGBColor(255, 0, 0) # Rojo para que destaque
    p.font.italic = True
    p.alignment = PP_ALIGN.CENTER

def generar_ppt(df, lista_figuras):
    """
    Carga la plantilla fija y rellena datos en slides específicas.
    """
    # 1. Cargar plantilla desde la carpeta assets
    ruta_plantilla = "assets/Plantilla_ReunionesCoordinacionFinCuatrimestre.pptx"
    try:
        prs = Presentation(ruta_plantilla)
    except Exception as e:
        # Si falla, creamos una en blanco para no romper la app, pero avisamos
        print(f"Error cargando plantilla: {e}")
        prs = Presentation()

    # --- 1. INSERTAR TABLA EN "RESUMEN DEL CUATRIMESTRE" ---
    slide_resumen = buscar_diapositiva(prs, "Resumen del cuatrimestre")
    if slide_resumen:
        # Insertamos la tabla debajo del título
        df_to_ppt_table(slide_resumen, df, Inches(0.5), Inches(2), Inches(9), Inches(4))
    
    # --- 2. PLACEHOLDERS PARA FUNCIONES FUTURAS (IA) ---
    
    # Slide: Informe sobre los partes de asignatura (Docentes)
    # Nota: Tu plantilla tiene dos diapos con títulos parecidos, buscamos la específica
    slide_partes_docentes = buscar_diapositiva(prs, "Informe sobre los partes de asignatura de docentes")
    if slide_partes_docentes:
        agregar_placeholder_ia(slide_partes_docentes, "AQUÍ SE GENERARÁ EL RESUMEN IA DE DOCENTES")

    # Slide: Informe sobre los partes de asignatura de delegados
    slide_partes_delegados = buscar_diapositiva(prs, "Informe sobre los partes de asignatura de delegados")
    if slide_partes_delegados:
        agregar_placeholder_ia(slide_partes_delegados, "AQUÍ SE GENERARÁ EL RESUMEN IA DE DELEGADOS")

    # Slide: Coordinación entre asignaturas
    slide_coordinacion = buscar_diapositiva(prs, "Coordinación entre asignaturas")
    if slide_coordinacion:
        agregar_placeholder_ia(slide_coordinacion, "AQUÍ IRÁ LA INFO DE COORDINACIÓN")

    # --- 3. AÑADIR GRÁFICAS ---
    # Las añadimos al final porque python-pptx no permite insertar en medio fácilmente.
    # Usamos el layout 5 (Title Only) o el que tenga la plantilla.
    layout_grafica = prs.slide_layouts[1] # Título y objeto
    
    if len(prs.slide_layouts) > 5:
        layout_grafica = prs.slide_layouts[5] # Intentamos usar Solo Título

    for titulo_grafica, figura in lista_figuras:
        slide = prs.slides.add_slide(layout_grafica)
        
        # Título
        if slide.shapes.title:
            slide.shapes.title.text = titulo_grafica
        
        # Imagen
        image_stream = io.BytesIO()
        figura.savefig(image_stream, format='png', bbox_inches='tight', dpi=150)
        image_stream.seek(0)
        
        slide.shapes.add_picture(image_stream, Inches(1), Inches(1.5), width=Inches(8))

    # --- GUARDAR ---
    output = io.BytesIO()
    prs.save(output)
    output.seek(0)
    
    return output
