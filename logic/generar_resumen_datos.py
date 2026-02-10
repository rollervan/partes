import pandas as pd
import numpy as np


def generar_resumen_datos(df):
    """
    Genera una tabla resumen extendida con datos académicos, satisfacción y gestión de solicitudes.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    # 1. Identificar columnas clave (Asignatura, Curso, Cuatrimestre)
    col_asig = next((c for c in df.columns if str(c).strip().startswith("Seleccione")), None)
    col_curso = next((c for c in df.columns if "Curso" in str(c)), None)
    col_cuatri = next((c for c in df.columns if "Cuatrimestre" in str(c)), None)

    # 2. Identificar las 4 nuevas columnas por palabras clave (más seguro que por índice)
    col_sat_res = next((c for c in df.columns if "satisfacción" in str(c) and "resultados" in str(c)), None)
    col_sat_grup = next((c for c in df.columns if "satisfacción" in str(c) and "grupo" in str(c)), None)
    

    # Verificación básica
    if not all([col_asig, col_curso, col_cuatri]):
        print("Error: Faltan columnas estructurales (Asignatura/Curso/Cuatrimestre).")
        return df

    # 3. Crear lista de columnas a extraer
    cols_a_extraer = [
        col_asig, col_curso, col_cuatri, 
        'Aprobados_Subgrupo', 'Matriculados_Subgrupo'
    ]
    
    # Añadimos las extras solo si existen (para evitar errores)
    extras_map = {
        col_sat_res: 'Valoración Resultados',
        col_sat_grup: 'Valoración Grupo'
    }
    
    for c in [col_sat_res, col_sat_grup]:
        if c: cols_a_extraer.append(c)

    # 4. Crear DataFrame resumen
    df_res = df[cols_a_extraer].copy()

    # 5. Cálculos Numéricos (% Aprobados)
    df_res['Aprobados_Subgrupo'] = pd.to_numeric(df_res['Aprobados_Subgrupo'], errors='coerce').fillna(0)
    df_res['Matriculados_Subgrupo'] = pd.to_numeric(df_res['Matriculados_Subgrupo'], errors='coerce').fillna(0)

    df_res['% Aprobados'] = np.where(
        df_res['Matriculados_Subgrupo'] > 0,
        (df_res['Aprobados_Subgrupo'] / df_res['Matriculados_Subgrupo']) * 100,
        0
    )
    df_res['% Aprobados'] = df_res['% Aprobados'].round(2)

    # 6. Ordenación (Lógica de Curso texto a número)
    mapa_orden = {
        'Primero': 1, 'Segundo': 2, 'Tercero': 3, 'Cuarto': 4, 'Quinto': 5,
        '1': 1, '2': 2, '3': 3, '4': 4, '1º': 1, '2º': 2, '3º': 3, '4º': 4
    }
    
    # Columnas temporales para ordenar
    df_res['sort_curso'] = df_res[col_curso].astype(str).str.strip().map(mapa_orden).fillna(99)
    df_res['sort_cuatri'] = df_res[col_cuatri].astype(str).str.strip().map(mapa_orden).fillna(99)
    
    # Ordenamos
    df_res = df_res.sort_values(by=['sort_curso', 'sort_cuatri', col_asig])

    # 7. Limpieza y Renombrado Final
    # Definimos el orden final de columnas
    columnas_finales = [
        col_asig, col_curso, col_cuatri, 
        'Aprobados_Subgrupo', 'Matriculados_Subgrupo', '% Aprobados'
    ]
    
    # Añadimos las extras encontradas
    for col_original, nuevo_nombre in extras_map.items():
        if col_original in df_res.columns:
            df_res.rename(columns={col_original: nuevo_nombre}, inplace=True)
            columnas_finales.append(nuevo_nombre)

    # Devolvemos solo las columnas finales limpias
    return df_res[columnas_finales].reset_index(drop=True)
