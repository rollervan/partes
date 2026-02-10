import pandas as pd
import numpy as np

# -----------------------------------------------------------------------------
# Filtros de dataframes
# -----------------------------------------------------------------------------

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






