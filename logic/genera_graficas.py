import matplotlib.pyplot as plt
import seaborn as sns

def genera_graficas(df):
    """
    Genera gráficas de análisis utilizando Matplotlib/Seaborn.
    Retorna una lista de tuplas: [(Titulo, Figura), ...]
    """
    
    # Lista para almacenar las figuras generadas y devolverlas a la app
    figuras_output = []

    # Limpieza de nombres y espacios
    rename_map = {
        'Seleccione la asignatura (Grado en Inteligencia Artificial)': 'Asignatura',
        'Curso:': 'Curso',
        'Cuatrimestre:': 'Cuatrimestre'
    }
    df = df.rename(columns=rename_map)
    df.columns = df.columns.str.strip()

    sns.set_theme(style="whitegrid")

    # --- CONFIGURACIÓN DE COLORES Y RANGOS ---
    cursos_unicos = sorted(df['Curso'].unique())
    colores = sns.color_palette("Set2", n_colors=len(cursos_unicos))
    mapa_colores = dict(zip(cursos_unicos, colores))

    config_graficas = [
        {"col": "% Aprobados", "titulo": "Porcentaje de Aprobados", "ylabel": "% Aprobados", "ylim": (0, 100)},
        {"col": "Valoración Resultados", "titulo": "Valoración Resultados", "ylabel": "Puntuación (0-5)", "ylim": (0, 5)},
        {"col": "Valoración Grupo", "titulo": "Valoración Grupo", "ylabel": "Puntuación (0-5)", "ylim": (0, 5)}
    ]

    # --- 1. GRÁFICAS GLOBALES ---
    for cfg in config_graficas:
        if cfg["col"] not in df.columns: continue

        # Capturamos la figura en una variable 'fig'
        fig = plt.figure(figsize=(14, 8))
        
        df_sorted = df.sort_values(by=['Curso', 'Asignatura'])
        
        sns.barplot(
            data=df_sorted,
            x='Asignatura',
            y=cfg["col"],
            hue='Curso',
            palette=mapa_colores,
            dodge=False
        )
        
        plt.ylim(cfg["ylim"])
        
        # Línea de media
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
        plt.legend(title="Curso", bbox_to_anchor=(1.01, 1), loc='upper left')
        plt.tight_layout()
        
        # Guardamos en la lista en lugar de en disco
        figuras_output.append((f"Global: {cfg['titulo']}", fig))

    # --- 2. GRÁFICAS POR CURSO ---
    for curso in cursos_unicos:
        color_del_curso = mapa_colores[curso]
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
                color=color_del_curso
            )
            
            plt.ylim(cfg["ylim"])
            plt.title(f"CURSO {curso} - {cfg['titulo']}", fontsize=16)
            plt.ylabel(cfg["ylabel"])
            plt.xlabel("Asignatura")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            figuras_output.append((f"Curso {curso}: {cfg['titulo']}", fig))

    return figuras_output
