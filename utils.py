import pandas as pd
import numpy as np

# -----------------------------------------------------------------------------
# 2. FUNCIÓN DE EXTRACCIÓN
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

import matplotlib.pyplot as plt
import seaborn as sns
import os

def genera_graficas(df, carpeta_salida="graficas_output"):
    # --- 1. PREPARACIÓN ---
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    # Limpieza de nombres y espacios
    rename_map = {
        'Seleccione la asignatura (Grado en Inteligencia Artificial)': 'Asignatura',
        'Curso:': 'Curso',
        'Cuatrimestre:': 'Cuatrimestre'
    }
    df = df.rename(columns=rename_map)
    df.columns = df.columns.str.strip()

    sns.set_theme(style="whitegrid")

    # --- 2. CONFIGURACIÓN DE COLORES Y RANGOS ---
    cursos_unicos = sorted(df['Curso'].unique())
    # Usamos 'Set2' para colores distintivos
    colores = sns.color_palette("Set2", n_colors=len(cursos_unicos))
    mapa_colores = dict(zip(cursos_unicos, colores))

    # Aquí definimos los límites (ylim) para cada tipo de gráfica
    config_graficas = [
        {
            "col": "% Aprobados", 
            "titulo": "Porcentaje de Aprobados", 
            "ylabel": "% Aprobados",
            "ylim": (0, 100)  # Rango fijo 0-100
        },
        {
            "col": "Valoración Resultados", 
            "titulo": "Valoración Resultados", 
            "ylabel": "Puntuación (0-5)",
            "ylim": (0, 5)    # Rango fijo 0-5
        },
        {
            "col": "Valoración Grupo", 
            "titulo": "Valoración Grupo", 
            "ylabel": "Puntuación (0-5)",
            "ylim": (0, 5)    # Rango fijo 0-5
        }
    ]

    # --- 3. GRÁFICAS GLOBALES (Con línea de media y rango fijo) ---
    print("--- Generando gráficas GLOBALES ---")
    for cfg in config_graficas:
        if cfg["col"] not in df.columns: continue

        plt.figure(figsize=(14, 8))
        df_sorted = df.sort_values(by=['Curso', 'Asignatura'])
        
        # Gráfica
        sns.barplot(
            data=df_sorted,
            x='Asignatura',
            y=cfg["col"],
            hue='Curso',
            palette=mapa_colores,
            dodge=False
        )
        
        # APLICAR EL RANGO FIJO
        plt.ylim(cfg["ylim"])
        
        # Línea de media global
        media_valor = df[cfg["col"]].mean()
        plt.axhline(y=media_valor, color='red', linestyle='--', linewidth=2, alpha=0.8)
        
        # Texto de la media (ajustado para que no se salga si está cerca del borde)
        plt.text(
            x=len(df_sorted) - 0.5,
            y=media_valor + (cfg["ylim"][1] * 0.02), # Un pelín por encima de la línea
            s=f'Media: {media_valor:.2f}', 
            color='red', 
            fontweight='bold', 
            ha='right'
        )
        
        plt.title(f"GLOBAL - {cfg['titulo']}", fontsize=16)
        plt.ylabel(cfg["ylabel"])
        plt.xlabel("Asignatura")
        plt.xticks(rotation=45, ha='right')
        plt.legend(title="Curso", bbox_to_anchor=(1.01, 1), loc='upper left')
        
        plt.tight_layout()
        nombre = f"Global_{cfg['col'].replace(' ', '_').replace('%', 'Pct')}.png"
        plt.savefig(os.path.join(carpeta_salida, nombre), dpi=300, bbox_inches='tight')
        plt.close()

    # --- 4. GRÁFICAS POR CURSO (Con rango fijo, sin media global) ---
    print("--- Generando gráficas INDIVIDUALES por curso ---")
    for curso in cursos_unicos:
        color_del_curso = mapa_colores[curso]
        
        df_curso = df[df['Curso'] == curso].copy()
        if df_curso.empty: continue

        for cfg in config_graficas:
            if cfg["col"] not in df_curso.columns: continue

            plt.figure(figsize=(10, 6))
            df_curso_sorted = df_curso.sort_values(by=cfg["col"], ascending=False)
            
            sns.barplot(
                data=df_curso_sorted,
                x='Asignatura',
                y=cfg["col"],
                color=color_del_curso # Color forzado del curso
            )
            
            # APLICAR EL RANGO FIJO TAMBIÉN AQUÍ
            plt.ylim(cfg["ylim"])
            
            plt.title(f"CURSO {curso} - {cfg['titulo']}", fontsize=16)
            plt.ylabel(cfg["ylabel"])
            plt.xlabel("Asignatura")
            plt.xticks(rotation=45, ha='right')
            
            plt.tight_layout()
            nombre = f"Curso_{curso}_{cfg['col'].replace(' ', '_').replace('%', 'Pct')}.png"
            plt.savefig(os.path.join(carpeta_salida, nombre), dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Guardado Curso {curso}: {nombre}")
