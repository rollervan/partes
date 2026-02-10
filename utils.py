import pandas as pd
import numpy as np

# -----------------------------------------------------------------------------
# 2. FUNCIÓN DE EXTRACCIÓN
# -----------------------------------------------------------------------------

import pandas as pd

def filtrar_por_fechas(df, fecha_inicio, fecha_fin=None):
    """
    Filtra el DataFrame por rango de fechas (DD-MM-AAAA).
    
    Args:
        df: DataFrame original.
        fecha_inicio: String 'DD-MM-AAAA' (ej: '25-01-2024').
        fecha_fin: (Opcional) String 'DD-MM-AAAA'.
    """
    df_res = df.copy()
    
    # 1. Convertir columna del Excel a datetime (asumiendo formato europeo)
    df_res.iloc[:, 1] = pd.to_datetime(df_res.iloc[:, 1], dayfirst=True, errors='coerce')
    
    try:
        # 2. Convertir fecha de inicio (Forzamos día primero)
        inicio_dt = pd.to_datetime(fecha_inicio, dayfirst=True)
        
        # 3. Definir la máscara de filtrado
        if fecha_fin:
            fin_dt = pd.to_datetime(fecha_fin, dayfirst=True)
            # Filtro: Entre inicio y fin (ambos inclusive)
            mask = (df_res.iloc[:, 1] >= inicio_dt) & (df_res.iloc[:, 1] <= fin_dt)
        else:
            # Filtro: Desde inicio en adelante
            mask = df_res.iloc[:, 1] >= inicio_dt
            
        return df_res[mask]

    except Exception as e:
        print(f"Error al procesar las fechas: {e}")
        return pd.DataFrame()

def obtener_datos_subgrupo(df, codigo):
    codigo = codigo.upper()
    config = MAPA_TITULACIONES.get(codigo)
    
    if not config:
        print(f"Error: Código '{codigo}' no encontrado.")
        return None

    # 1. Preparar DF
    df_temp = df.copy()
    df_temp.iloc[:, 5] = df_temp.iloc[:, 5].astype(str).str.strip()

    # 2. Filtro Nombre (Col 5)
    mask_nombre = df_temp.iloc[:, 5] == config['raiz']

    # 3. Filtro Campus (Si aplica)
    mask_campus = True
    col_campus_idx = -1 # Valor centinela
    
    if 'filtro_campus' in config:
        datos_campus = config['filtro_campus']
        col_campus_idx = datos_campus['col']
        valor_esperado = datos_campus['valor']
        
        # Convertimos a string y comparamos
        col_campus_vals = df_temp.iloc[:, col_campus_idx].fillna('').astype(str).str.strip()
        mask_campus = col_campus_vals == valor_esperado

    # 4. Filtro Datos Existentes (Buscamos datos en la columna de Aprobados)
    # Nota: config['cols'][1] es Aprobados (porque el 0 ahora es Asignatura)
    col_aprobados_idx = config['cols'][1] 
    mask_datos = pd.notna(df_temp.iloc[:, col_aprobados_idx])

    # Aplicar Filtros
    mask_final = mask_nombre & mask_campus & mask_datos

    if not mask_final.any():
        print(f"Aviso: No se encontraron registros para {codigo}.")
        return pd.DataFrame()

    # 5. Selección de Columnas (Eliminando explícitamente la de Campus)
    cols_seleccionadas = IDX_COMUNES + config['cols']
    
    # SEGURIDAD: Si la columna de campus está en la lista de selección, la quitamos
    if col_campus_idx != -1 and col_campus_idx in cols_seleccionadas:
        cols_seleccionadas.remove(col_campus_idx)
        
    cols_seleccionadas.sort()

    # 6. Crear DF Final y Renombrar
    df_resultado = df_temp.iloc[mask_final.values, cols_seleccionadas].copy()
    
    # Renombrado dinámico (Ahora Asignatura es el índice 0 de 'cols')
    col_aprobados_name = df.columns[config['cols'][1]]
    col_matriculados_name = df.columns[config['cols'][2]]
    
    rename_dict = {
        col_aprobados_name: 'Aprobados_Subgrupo',
        col_matriculados_name: 'Matriculados_Subgrupo'
    }
    df_resultado.rename(columns=rename_dict, inplace=True)
    
    print(f"Extracción exitosa: {codigo} -> {len(df_resultado)} registros.")
    return df_resultado
