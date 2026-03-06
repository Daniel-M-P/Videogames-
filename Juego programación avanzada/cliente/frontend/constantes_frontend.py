import os
TAMANO_HORIZONTAL = 1200
TAMANO_VERTICAL = 700
TAMANO_CUADRADOS = 30

# Tiempos Pepa
TIEMPO_DESPLAZAMIENTO = 500
TIEMPO_ANIMACION = TIEMPO_DESPLAZAMIENTO // 4

# Tiempo Caca
TIEMPO_TRANSICION = 1000 * 3

# Rutas
RUTA_PRINCIPAL = os.path.dirname(__file__)
RUTA_SPRITES = os.path.join(RUTA_PRINCIPAL, 'assets', 'sprites')
RUTA_SONIDOS = os.path.join(RUTA_PRINCIPAL, 'assets', 'sonidos')
RUTA_PUZZLES = os.path.join(RUTA_PRINCIPAL, 'assets', 'base_puzzles')
RUTA_PEPA = os.path.join(RUTA_PRINCIPAL, 'assets', 'sprites', 'pepa')


# Colores
COLOR_FONDO = '#90c8f7'
COLOR_LETRAS = '#4890b1'
COLOR_BOTONES = '#4CAF50'
