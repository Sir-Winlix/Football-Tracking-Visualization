import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos de tracking de la semana 1
tracking_df = pd.read_csv('tracking_week_1.csv')  # Asegúrate de usar el archivo correcto

# Especificar gameId y playId de la jugada de interés
game_id = 2022091200
play_id = 64

# Filtrar los datos por gameId y playId
play_data = tracking_df[(tracking_df['gameId'] == game_id) & (tracking_df['playId'] == play_id)]

# Eliminar filas donde el jugador sea 'NA' (representa la pelota)
play_data = play_data[play_data['nflId'].notna()]

# Filtrar jugadores por equipo si se desea ver solo un equipo
team = 'DEN'  # Para Cincinnati, por ejemplo
play_data = play_data[play_data['club'] == team]

# Crear la visualización
plt.figure(figsize=(10, 6))
for player_id in play_data['nflId'].unique():
    player_data = play_data[play_data['nflId'] == player_id]
    plt.plot(player_data['x'], player_data['y'], label=f"Jugador {player_id}")

plt.title(f"Rutas de Jugadores - Juego {game_id}, Jugada {play_id}")
plt.xlabel("Longitud del campo (Yardas)")
plt.ylabel("Ancho del campo (Yardas)")
plt.legend(loc="upper left")
plt.grid(True)
plt.show()
