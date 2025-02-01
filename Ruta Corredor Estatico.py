import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Cargar los datos (ajustar las rutas de los archivos CSV a tu sistema)
tracking_data = pd.read_csv('tracking_week_1.csv')  # Cambia el nombre del archivo según sea necesario

# Parámetros del partido y jugada
game_id = 2022091200  # Ajustar con un gameId real
play_id = 64  # Ajustar con un playId real

# Filtrar los datos para obtener la jugada específica
jugada_tracking = tracking_data[(tracking_data['gameId'] == game_id) & (tracking_data['playId'] == play_id)]

# Configuración del campo de fútbol
fig, ax = plt.subplots(figsize=(12, 7))

# Definir las dimensiones del campo de fútbol
campo_longitud = 120  # Longitud total del campo en yardas
campo_ancho = 53.3  # Ancho del campo en yardas

# Dibujar el campo de fútbol
ax.set_xlim(0, campo_longitud)
ax.set_ylim(0, campo_ancho)
ax.set_facecolor('green')

# Cambiar range por np.arange para aceptar flotantes
ax.set_xticks(np.arange(0, campo_longitud + 1, 10))
ax.set_yticks(np.arange(0, campo_ancho + 1, 10))

ax.grid(True, color='white', linestyle='-', linewidth=0.5)

# Añadir marcas para las yardas
ax.set_xlabel('Yardas')
ax.set_ylabel('Ancho del campo')

# Para cada receptor, trazar su ruta en el campo
for nfl_id in jugada_tracking['nflId'].unique():
    receptor = jugada_tracking[jugada_tracking['nflId'] == nfl_id]
    ax.plot(receptor['x'], receptor['y'], label=f'Receptor {nfl_id}', linewidth=2)

# Añadir leyenda
ax.legend()

# Mostrar la visualización
plt.title(f'Rutas de los Receptores en el Partido {game_id}, Jugada {play_id}')
plt.show()
