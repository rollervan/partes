# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE ÍNDICES
# -----------------------------------------------------------------------------

# Columnas Comunes (Identificación + Encuesta)
IDX_COMUNES = list(range(0, 6)) + list(range(65, 94))

# Mapa Granular: Clave -> { Raíz (Col 5), Indices [Aprobados, Matriculados] }
MAPA_TITULACIONES = {
    # --- GDDV ---
    'GDDV_QUINTANA':     {'raiz': 'Grado en Diseño y Desarrollo de Videojuegos', 'cols': [6, 8, 9], 'filtro_campus': {'col': 7, 'valor': 'Quintana'}},
    'GDDV_MOSTOLES':     {'raiz': 'Grado en Diseño y Desarrollo de Videojuegos', 'cols': [6, 10, 11], 'filtro_campus': {'col': 7, 'valor': 'Móstoles'}},
    'GDDV_GIC_MOST':     {'raiz': 'Grado en Diseño y Desarrollo de Videojuegos', 'cols': [6, 12, 13]},
    
    # --- GICIB ---
    'GICIB':             {'raiz': 'Grado en Ingeniería de la Ciberseguridad',   'cols': [14, 15, 16]},
    
    # --- GIC ---
    'GIC':               {'raiz': 'Grado en Ingeniería de Computadores',        'cols': [17, 18, 19]},
    'GIC_GII_MOST':      {'raiz': 'Grado en Ingeniería de Computadores',        'cols': [17, 20, 21]},
    'GIC_GDDV_MOST':     {'raiz': 'Grado en Ingeniería de Computadores',        'cols': [17, 22, 23]},
    
    # --- GII ---
    'GII_VIC':           {'raiz': 'Grado en Ingeniería Informática',            'cols': [24, 26, 27], 'filtro_campus': {'col': 25, 'valor': 'Vicálvaro'}},
    'GII_ADE_ON_VIC':    {'raiz': 'Grado en Ingeniería Informática',            'cols': [24, 28, 29]},
    'GII_ADE_PRE_VIC':   {'raiz': 'Grado en Ingeniería Informática',            'cols': [24, 30, 31]},
    'GII_CRIM_VIC':      {'raiz': 'Grado en Ingeniería Informática',            'cols': [24, 32, 33]},
    'GII_MOST':          {'raiz': 'Grado en Ingeniería Informática',            'cols': [24, 34, 35], 'filtro_campus': {'col': 25, 'valor': 'Móstoles'}},
    'GII_ADE_MOST':      {'raiz': 'Grado en Ingeniería Informática',            'cols': [24, 36, 37]},
    'GII_GIC':           {'raiz': 'Grado en Ingeniería Informática',            'cols': [24, 38, 39]},
    'GII_GIS':           {'raiz': 'Grado en Ingeniería Informática',            'cols': [24, 40, 41]},
    'GII_GMAT':          {'raiz': 'Grado en Ingeniería Informática',            'cols': [24, 42, 43]},
    
    # --- GIS ---
    'GIS':               {'raiz': 'Grado en Ingeniería del Software',           'cols': [44, 45, 46]},
    'GIS_GMAT':          {'raiz': 'Grado en Ingeniería del Software',           'cols': [44, 47, 48]},
    'GIS_GII':           {'raiz': 'Grado en Ingeniería del Software',           'cols': [44, 49, 50]},
    
    # --- GIA ---
    'GIA':               {'raiz': 'Grado en Inteligencia Artificial',           'cols': [51, 52, 53]},
    
    # --- GMAT ---
    'GMAT':              {'raiz': 'Grado en Matemáticas',                       'cols': [54, 55, 56]},
    'GMAT_GIS':          {'raiz': 'Grado en Matemáticas',                       'cols': [54, 57, 58]},
    'GMAT_GII':          {'raiz': 'Grado en Matemáticas',                       'cols': [54, 59, 60]},
    'GMAT_ECO':          {'raiz': 'Grado en Matemáticas',                       'cols': [54, 61, 62]},
    'GMAT_PRIM':         {'raiz': 'Grado en Matemáticas',                       'cols': [54, 63, 64]}
}
