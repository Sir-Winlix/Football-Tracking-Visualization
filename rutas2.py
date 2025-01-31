import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Cargar los datos de tracking de la semana 1
tracking_df = pd.read_csv('tracking_week_1.csv')  # Asegúrate de usar el archivo correcto

game_id = 2022091200
play_id = 64

# Filtrar los datos por gameId y playId
play_data = tracking_df[(tracking_df['gameId'] == game_id) & (tracking_df['playId'] == play_id)]

# Eliminar filas donde el jugador sea 'NA' (representa la pelota)
ball_data = play_data[play_data['nflId'].isna()]

# Filtrar los jugadores (sin el balón)
play_data = play_data[play_data['nflId'].notna()]

# Filtrar jugadores por equipo si se desea ver solo un equipo
team = 'DEN'  # Para Cincinnati, por ejemplo
play_data = play_data[play_data['club'] == team]

# Crear la visualización
plt.figure(figsize=(12, 7))

# Mostrar la ruta del balón (con x, y)
plt.plot(ball_data['x'], ball_data['y'], color='black', label="Ruta del balón", linestyle='--', alpha=0.6)

# Mostrar las rutas de los jugadores
for player_id in play_data['nflId'].unique():
    player_data = play_data[play_data['nflId'] == player_id]
    
    # Obtener el dorsal del jugador
    player_jersey_number = str(player_data['jerseyNumber'].iloc[0])  # Tomamos el número de camiseta

    # Dibujar la ruta del jugador
    plt.plot(player_data['x'], player_data['y'], label=f"Jugador {player_jersey_number}")
    
    # Anotaciones de dorsales
    for i in range(0, len(player_data), int(len(player_data) / 5)):  # Anotar en 5 puntos de la ruta
        plt.text(player_data['x'].iloc[i], player_data['y'].iloc[i], 
                 f"{player_jersey_number}", fontsize=8, ha='right')

# Ajustar título y etiquetas
plt.title(f"Rutas de Jugadores y Balón - Juego {game_id}, Jugada {play_id}")
plt.xlabel("Longitud del campo (Yardas)")
plt.ylabel("Ancho del campo (Yardas)")
plt.legend(loc="upper left", fontsize=8)
plt.grid(True)

# Mostrar el gráfico
plt.show()
