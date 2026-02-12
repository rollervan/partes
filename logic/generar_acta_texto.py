import pandas as pd

def safe_get_text(row, idx):
    """
    Función auxiliar para obtener texto limpio del DataFrame por índice de columna.
    Maneja valores nulos (NaN) y vacíos.
    """
    try:
        val = row.iloc[idx]
        if pd.isna(val) or val == "" or str(val).lower() == "nan":
            return "No indicado / No aplica"
        return str(val).strip()
    except IndexError:
        return "N/A"

def generar_acta_texto(df):
    """
    Toma el DataFrame filtrado y genera un string largo con toda la información
    de las asignaturas, formateado para ser leído por una IA.
    """
    
    # 1. ORDENAR DATOS (Misma lógica que en el Word)
    try:
        df_sorted = df.copy()
        # Intentamos convertir la columna curso (índice 9) a número
        df_sorted['Curso_Num'] = pd.to_numeric(df_sorted.iloc[:, 9], errors='coerce').fillna(999)
        # Ordenar por Curso -> Semestre (idx 10) -> Asignatura (idx 6)
        df_sorted = df_sorted.sort_values(by=['Curso_Num', df.columns[10], df.columns[6]])
    except Exception:
        # Si falla, ordenamos por nombre de curso
        df_sorted = df.sort_values(by=[df.columns[9], df.columns[6]])

    # 2. CONSTRUCCIÓN DEL TEXTO
    texto_acumulado = []
    
    texto_acumulado.append(f"INFORME DE DATOS DE LA TITULACIÓN")
    texto_acumulado.append(f"Total de asignaturas procesadas: {len(df)}")
    texto_acumulado.append("=" * 60 + "\n")

    for index, row in df_sorted.iterrows():
        # --- EXTRACCIÓN DE VARIABLES (Índices basados en tu script original) ---
        asignatura = safe_get_text(row, 6)
        profesor = safe_get_text(row, 4)
        titulacion = safe_get_text(row, 5)
        curso = safe_get_text(row, 9)
        semestre = safe_get_text(row, 10)
        
        matriculados = safe_get_text(row, 8)
        aprobados = safe_get_text(row, 7)
        
        # Cálculo de tasa de éxito
        tasa_exito = "N/A"
        try:
            m = float(matriculados)
            a = float(aprobados)
            if m > 0:
                tasa_exito = f"{(a/m)*100:.1f}%"
        except:
            pass

        # --- BLOQUE DE TEXTO POR ASIGNATURA ---
        bloque = f"""
### ASIGNATURA: {asignatura}
- Profesor/a: {profesor}
- Curso: {curso} | Semestre: {semestre}
- Titulación: {titulacion}

1. DATOS CUANTITATIVOS:
   - Matriculados: {matriculados}
   - Aprobados: {aprobados}
   - Tasa de Éxito: {tasa_exito}

2. ANÁLISIS DE RESULTADOS:
   - Valoración Docente (1-5): {safe_get_text(row, 12)}
   - Justificación / Acciones de mejora: {safe_get_text(row, 13)}
   - ¿Existen deficiencias de formación previas?: {safe_get_text(row, 14)}
   - Detalles de deficiencias: {safe_get_text(row, 15)}

3. DOCENCIA E INCIDENCIAS:
   - ¿Temario completo?: {safe_get_text(row, 18)}
   - Causa si no se completó: {safe_get_text(row, 19)}
   - Incidencias generales: {safe_get_text(row, 20)}
   - Problemas detectados: {safe_get_text(row, 21)}
   - Detalles adicionales: {safe_get_text(row, 22)}

4. GRUPO Y COORDINACIÓN:
   - Características del grupo: {safe_get_text(row, 23)}
   - Satisfacción con el grupo: {safe_get_text(row, 24)}
   - Coordinación con otras asignaturas: {safe_get_text(row, 30)}

5. CIERRE:
   - Otras incidencias: {safe_get_text(row, 33)}
   - Sugerencias: {safe_get_text(row, 34)}

------------------------------------------------------------
"""
        texto_acumulado.append(bloque)

    # Unimos todo en un solo string
    return "\n".join(texto_acumulado)
