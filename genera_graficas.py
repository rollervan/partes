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
