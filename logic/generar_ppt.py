import io
import json
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

def df_to_ppt_table(slide, df, left, top, width, height):
    """Dibuja la tabla en la slide indicada."""
    # Limitamos filas para que no se salga de la diapo
    df_to_print = df.head(12) 
    rows, cols = df_to_print.shape
    
    table_shape = slide.shapes.add_table(rows + 1, cols, left, top, width, height)
    table = table_shape.table

    # Estilos básicos cabecera
    for col_idx, col_name in enumerate(df_to_print.columns):
        cell = table.cell(0, col_idx)
        cell.text = str(col_name)
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(9)
        p.alignment = PP_ALIGN.CENTER
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(220, 220, 220)

    # Cuerpo de la tabla
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

def reemplazar_marcadores(prs, diccionario_datos):
    """
    Recorre TODA la presentación sustituyendo las claves del diccionario 
    por sus valores, manteniendo el estilo original.
    """
    if not diccionario_datos:
        return

    def sustituir_en_parrafo(paragraph, datos):
        for run in paragraph.runs:
            texto_run = run.text
            for marcador, valor in datos.items():
                if marcador in texto_run:
                    run.text = texto_run.replace(marcador, str(valor))

    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    sustituir_en_parrafo(paragraph, diccionario_datos)
            
            if shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        for paragraph in cell.text_frame.paragraphs:
                            sustituir_en_parrafo(paragraph, diccionario_datos)

def generar_ppt(df, lista_figuras, ruta_json=None):
    """
    Genera el PPT:
    1. Carga plantilla.
    2. Sustituye marcadores (si hay JSON).
    3. Añade NUEVAS slides para tablas, placeholders y gráficas.
    """
    
    # 1. CARGAR PLANTILLA
    ruta_plantilla = "assets/Plantilla_ReunionesCoordinacionFinCuatrimestre.pptx"
    try:
        prs = Presentation(ruta_plantilla)
    except Exception as e:
        print(f"Error cargando plantilla: {e}")
        prs = Presentation()

    # 2. SUSTITUCIÓN DE TEXTO (PRIORIDAD MÁXIMA)
    if ruta_json:
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                datos_diccionario = json.load(f)
            reemplazar_marcadores(prs, datos_diccionario)
        except Exception as e:
            print(f"Error cargando o procesando el archivo JSON: {e}")

    # Definimos el layout para nuevas diapositivas (5 = Title Only, suele ser estándar)
    # Si la plantilla no tiene 6 layouts, usamos el último disponible
    layout_index = 5 if len(prs.slide_layouts) > 5 else len(prs.slide_layouts) - 1
    layout_solo_titulo = prs.slide_layouts[layout_index]

    # 3. AÑADIR NUEVA SLIDE PARA LA TABLA DATAFRAME
    slide_tabla = prs.slides.add_slide(layout_solo_titulo)
    if slide_tabla.shapes.title:
        slide_tabla.shapes.title.text = "Resumen de Datos (Tabla)"
    
    df_to_ppt_table(slide_tabla, df, Inches(0.5), Inches(2), Inches(9), Inches(4))
    
    # 4. AÑADIR NUEVAS SLIDES PARA PLACEHOLDERS IA
    # Docentes
    slide_ia_doc = prs.slides.add_slide(layout_solo_titulo)
    if slide_ia_doc.shapes.title:
        slide_ia_doc.shapes.title.text = "Informe Docentes (IA)"
    agregar_placeholder_ia(slide_ia_doc, "AQUÍ SE GENERARÁ EL RESUMEN IA DE DOCENTES")

    # Delegados
    slide_ia_del = prs.slides.add_slide(layout_solo_titulo)
    if slide_ia_del.shapes.title:
        slide_ia_del.shapes.title.text = "Informe Delegados (IA)"
    agregar_placeholder_ia(slide_ia_del, "AQUÍ SE GENERARÁ EL RESUMEN IA DE DELEGADOS")

    # Coordinación
    slide_ia_coord = prs.slides.add_slide(layout_solo_titulo)
    if slide_ia_coord.shapes.title:
        slide_ia_coord.shapes.title.text = "Coordinación (IA)"
    agregar_placeholder_ia(slide_ia_coord, "AQUÍ IRÁ LA INFO DE COORDINACIÓN")

    # 5. AÑADIR NUEVAS SLIDES PARA GRÁFICAS
    for titulo_grafica, figura in lista_figuras:
        slide_grafica = prs.slides.add_slide(layout_solo_titulo)
        
        # Título
        if slide_grafica.shapes.title:
            slide_grafica.shapes.title.text = titulo_grafica
        
        # Imagen
        image_stream = io.BytesIO()
        figura.savefig(image_stream, format='png', bbox_inches='tight', dpi=150)
        image_stream.seek(0)
        
        slide_grafica.shapes.add_picture(image_stream, Inches(1), Inches(1.5), width=Inches(8))

    # GUARDAR
    output = io.BytesIO()
    prs.save(output)
    output.seek(0)
    
    return output
