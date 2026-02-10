import matplotlib.pyplot as plt
import seaborn as sns

def genera_graficas(df):
    """
    Genera gráficas de análisis utilizando Matplotlib/Seaborn.
    Retorna una lista de tuplas: [(Titulo, Figura), ...]
    Adaptado para detectar dinámicamente las columnas de cualquier titulación.
    """
    
    figuras_output = []

    # --- 1. RENOMBRADO DINÁMICO (LA SOLUCIÓN AL ERROR) ---
    # En lugar de usar nombres fijos, buscamos las columnas por palabras clave
    
    # Buscar columna que parezca la Asignatura
    col_asig = next((c for c in df.columns if "Seleccione" in str(c) or "Asignatura" in str(c)), None)
    # Buscar columna que parezca el Curso
    col_curso = next((c for c in df.columns if "Curso" in str(c)), None)
    # Buscar columna que parezca el Cuatrimestre
    col_cuatri = next((c for c in df.columns if "Cuatrimestre" in str(c)), None)

    rename_map = {}
    if col_asig: rename_map[col_asig] = 'Asignatura'
    if col_curso: rename_map[col_curso] = 'Curso'
    if col_cuatri: rename_map[col_cuatri] = 'Cuatrimestre'

    # Aplicamos el renombrado
    df = df.rename(columns=rename_map)
    df.columns = df.columns.str.strip()

    # Validación de seguridad: Si no encontramos las columnas clave, salimos
    if 'Asignatura' not in df.columns:
        print("⚠️ No se encontró la columna de Asignatura.")
        return []

    sns.set_theme(style="whitegrid")

    # --- 2. PREPARACIÓN DE DATOS ---
    # Convertimos curso a string para evitar errores de ordenación con tipos mixtos
    if 'Curso' in df.columns:
        df['Curso'] = df['Curso'].astype(str)
        cursos_unicos = sorted(df['Curso'].unique())
    else:
        cursos_unicos = []

    # Configuración de colores
    if cursos_unicos:
        colores = sns.color_palette("Set2", n_colors=len(cursos_unicos))
        mapa_colores = dict(zip(cursos_unicos, colores))
    else:
        mapa_colores = {}

    config_graficas = [
        {"col": "% Aprobados", "titulo": "Porcentaje de Aprobados", "ylabel": "% Aprobados", "ylim": (0, 100)},
        {"col": "Valoración Resultados", "titulo": "Valoración Resultados", "ylabel": "Puntuación (0-5)", "ylim": (0, 5)},
        {"col": "Valoración Grupo", "titulo": "Valoración Grupo", "ylabel": "Puntuación (0-5)", "ylim": (0, 5)}
    ]

    # --- 3. GRÁFICAS GLOBALES ---
    for cfg in config_graficas:
        if cfg["col"] not in df.columns: continue

        fig = plt.figure(figsize=(14, 8))
        
        # Intentamos ordenar, si falla (ej. curso no existe), usamos el df tal cual
        try:
            sort_cols = ['Curso', 'Asignatura'] if 'Curso' in df.columns else ['Asignatura']
            df_sorted = df.sort_values(by=sort_cols)
        except:
            df_sorted = df

        # Gráfica
        kwargs_plot = {
            'data': df_sorted,
            'x': 'Asignatura',
            'y': cfg["col"]
        }
        # Solo añadimos hue si tenemos cursos identificados
        if 'Curso' in df.columns and mapa_colores:
            kwargs_plot['hue'] = 'Curso'
            kwargs_plot['palette'] = mapa_colores
            kwargs_plot['dodge'] = False
        
        sns.barplot(**kwargs_plot)
        
        plt.ylim(cfg["ylim"])
        
        # Línea de media (solo si hay datos numéricos válidos)
        if not df[cfg["col"]].isnull().all():
            media_valor = df[cfg["col"]].mean()
            plt.axhline(y=media_valor, color='red', linestyle='--', linewidth=2, alpha=0.8)
            
            plt.text(
                x=len(df_sorted) - 0.5,
                y=media_valor + (cfg["ylim"][1] * 0.02),
                s=f'Media: {media_valor:.2f}', 
                color='red', 
                fontweight='bold', 
                ha='right'
            )
        
        plt.title(f"GLOBAL - {cfg['titulo']}", fontsize=16)
        plt.ylabel(cfg["ylabel"])
        plt.xlabel("Asignatura")
        plt.xticks(rotation=45, ha='right')
        
        if 'Curso' in df.columns and mapa_colores:
            plt.legend(title="Curso", bbox_to_anchor=(1.01, 1), loc='upper left')
            
        plt.tight_layout()
        figuras_output.append((f"Global: {cfg['titulo']}", fig))

    # --- 4. GRÁFICAS POR CURSO ---
    for curso in cursos_unicos:
        if curso not in mapa_colores: continue
        
        df_curso = df[df['Curso'] == curso].copy()
        if df_curso.empty: continue

        for cfg in config_graficas:
            if cfg["col"] not in df_curso.columns: continue

            fig = plt.figure(figsize=(10, 6))
            
            df_curso_sorted = df_curso.sort_values(by=cfg["col"], ascending=False)
            
            sns.barplot(
                data=df_curso_sorted,
                x='Asignatura',
                y=cfg["col"],
                color=mapa_colores[curso]
            )
            
            plt.ylim(cfg["ylim"])
            plt.title(f"CURSO {curso} - {cfg['titulo']}", fontsize=16)
            plt.ylabel(cfg["ylabel"])
            plt.xlabel("Asignatura")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            figuras_output.append((f"Curso {curso}: {cfg['titulo']}", fig))

    return figuras_output
