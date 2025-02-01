import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

# Cargar los datos
tracking_data = pd.read_csv('tracking_week_1.csv')  # Cambia el nombre del archivo según sea necesario
players_data = pd.read_csv('players.csv')  # Asegúrate de tener el archivo players.csv
player_play_data = pd.read_csv('player_play.csv')  # Asegúrate de tener el archivo player_play.csv

# Parámetros del partido y jugada
game_id = 2022091200  # Ajustar con un gameId real
play_id = 64  # Ajustar con un playId real

# Filtrar los datos para obtener la jugada específica
jugada_tracking = tracking_data[(tracking_data['gameId'] == game_id) & (tracking_data['playId'] == play_id)]

# Filtrar los datos de player_play para obtener el equipo de cada jugador
jugada_players = player_play_data[(player_play_data['gameId'] == game_id) & (player_play_data['playId'] == play_id)]

# Crear un diccionario para obtener el equipo de cada jugador
equipo_dict = jugada_players.set_index('nflId')['teamAbbr'].to_dict()

# Crear un diccionario para obtener los nombres de los jugadores
jugadores = players_data.set_index('nflId')['displayName'].to_dict()

# Configuración del campo de fútbol
fig, ax = plt.subplots(figsize=(12, 7))

# Definir las dimensiones del campo de fútbol
campo_longitud = 120  # Longitud total del campo en yardas
campo_ancho = 53.3  # Ancho del campo en yardas

# Dibujar el campo de fútbol
ax.set_xlim(0, campo_longitud)
ax.set_ylim(0, campo_ancho)

# Eliminar el fondo verde (ahora es blanco)
ax.set_facecolor('white')

# Añadir líneas para las zonas de anotación con color azul
ax.fill_between([0, 10], 0, campo_ancho, color='blue', alpha=0.2)  # Zona de anotación de un equipo
ax.fill_between([110, 120], 0, campo_ancho, color='blue', alpha=0.2)  # Zona de anotación del otro equipo

# Añadir las líneas de las yardas (cada 10 yardas) en color negro
for x in range(0, campo_longitud + 1, 10):
    ax.axvline(x=x, color='black', linestyle='-', linewidth=1)

# Dibujar el área del campo
ax.set_xticks(np.arange(0, campo_longitud + 1, 10))  # Líneas de cada 10 yardas
ax.set_yticks(np.arange(0, campo_ancho + 1, 10))  # Líneas de cada 10 yardas
ax.grid(True, color='black', linestyle='-', linewidth=0.5)

# Añadir marcas para las yardas
ax.set_xlabel('Yardas')
ax.set_ylabel('Ancho del campo')

# Colores para los equipos (usando abreviaturas de equipos reales)
equipo_colores = {
    'BAL': 'blue',  # Baltimore Ravens
    'BUF': 'blue',  # Buffalo Bills
    'CIN': 'orange',  # Cincinnati Bengals
    'CLE': 'brown',  # Cleveland Browns
    'DAL': 'blue',  # Dallas Cowboys
    'DEN': 'orange',  # Denver Broncos
    'GB': 'green',  # Green Bay Packers
    'HOU': 'navy',  # Houston Texans
    'IND': 'blue',  # Indianapolis Colts
    'JAX': 'teal',  # Jacksonville Jaguars
    'KC': 'red',  # Kansas City Chiefs
    'LAC': 'powderblue',  # Los Angeles Chargers
    'LV': 'silver',  # Las Vegas Raiders
    'MIA': 'aqua',  # Miami Dolphins
    'MIN': 'purple',  # Minnesota Vikings
    'NE': 'navy',  # New England Patriots
    'NO': 'gold',  # New Orleans Saints
    'NYG': 'blue',  # New York Giants
    'NYJ': 'green',  # New York Jets
    'PHI': 'green',  # Philadelphia Eagles
    'PIT': 'gold',  # Pittsburgh Steelers
    'SF': 'red',  # San Francisco 49ers
    'SEA': 'navy',  # Seattle Seahawks
    'TB': 'red',  # Tampa Bay Buccaneers
    'TEN': 'navy',  # Tennessee Titans
    'WAS': 'burgundy'  # Washington Football Team
}

# Crear un diccionario con las rutas de los jugadores
jugadores_rutas = {}
for nfl_id in jugada_tracking['nflId'].unique():
    receptor = jugada_tracking[jugada_tracking['nflId'] == nfl_id]
    
    if not receptor.empty:
        jugadores_rutas[nfl_id] = receptor

# Función de actualización para la animación
def actualizar(frame):
    ax.clear()
    
    # Eliminar el fondo verde (ahora es blanco)
    ax.set_facecolor('white')

    # Añadir las zonas de anotación con color azul
    ax.fill_between([0, 10], 0, campo_ancho, color='blue', alpha=0.2)  # Zona de anotación de un equipo
    ax.fill_between([110, 120], 0, campo_ancho, color='blue', alpha=0.2)  # Zona de anotación del otro equipo

    # Añadir las líneas de las yardas en color negro
    for x in range(0, campo_longitud + 1, 10):
        ax.axvline(x=x, color='black', linestyle='-', linewidth=1)

    ax.set_xticks(np.arange(0, campo_longitud + 1, 10))  # Líneas de cada 10 yardas
    ax.set_yticks(np.arange(0, campo_ancho + 1, 10))  # Líneas de cada 10 yardas
    ax.grid(True, color='black', linestyle='-', linewidth=0.5)

    # Dibujar las rutas de los jugadores hasta el frame actual
    for nfl_id, receptor in jugadores_rutas.items():
        equipo = equipo_dict.get(nfl_id, 'Desconocido')
        color_equipo = equipo_colores.get(equipo, 'gray')
        
        # Tomamos los datos hasta el fotograma actual
        receptor_frame = receptor.iloc[:frame+1]
        
        # Trazar la ruta hasta el fotograma actual
        ax.plot(receptor_frame['x'], receptor_frame['y'], color=color_equipo, linewidth=2)
        
        # Añadir el nombre del jugador al final de la ruta
        nombre_receptor = jugadores.get(nfl_id, 'Desconocido')
        ax.text(receptor_frame['x'].iloc[-1], receptor_frame['y'].iloc[-1], nombre_receptor, color='black', fontsize=9, ha='center')

    # Dibujar el balón
    balon = jugada_tracking[jugada_tracking['nflId'].isna()]
    balon_frame = balon.iloc[frame]
    
    ax.scatter(balon_frame['x'], balon_frame['y'], color='brown', s=100, label='Balón')

# Crear la animación
ani = FuncAnimation(fig, actualizar, frames=len(jugada_tracking), interval=100, repeat=False)

# Mostrar la animación
plt.title(f'Rutas de los Receptores en el Partido {game_id}, Jugada {play_id}')
plt.show()
