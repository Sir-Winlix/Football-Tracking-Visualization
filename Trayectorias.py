import pandas as pd
import matplotlib.pyplot as plt
import os

# Cargar los archivos de juegos
games_df = pd.read_csv('games.csv')

# Crear un diccionario para convertir los códigos de los equipos en nombres
team_name_dict = {
    'BUF': 'Buffalo Bills', 'MIA': 'Miami Dolphins', 'NE': 'New England Patriots', 'NYJ': 'New York Jets',
    'BAL': 'Baltimore Ravens', 'CIN': 'Cincinnati Bengals', 'CLE': 'Cleveland Browns', 'PIT': 'Pittsburgh Steelers',
    'JAC': 'Jacksonville Jaguars', 'TEN': 'Tennessee Titans', 'IND': 'Indianapolis Colts', 'HOU': 'Houston Texans',
    'KC': 'Kansas City Chiefs', 'LV': 'Las Vegas Raiders', 'LA': 'Los Angeles Chargers', 'DEN': 'Denver Broncos',
    'DAL': 'Dallas Cowboys', 'NYG': 'New York Giants', 'PHI': 'Philadelphia Eagles', 'WAS': 'Washington Commanders',
    'CHI': 'Chicago Bears', 'DET': 'Detroit Lions', 'GB': 'Green Bay Packers', 'MIN': 'Minnesota Vikings',
    'ARI': 'Arizona Cardinals', 'LA': 'Los Angeles Rams', 'SF': 'San Francisco 49ers', 'SEA': 'Seattle Seahawks',
    'CAR': 'Carolina Panthers', 'ATL': 'Atlanta Falcons', 'NO': 'New Orleans Saints', 'TB': 'Tampa Bay Buccaneers'
}

# Función para obtener los nombres de los equipos con base en gameId
def get_team_names(game_id):
    game_data = games_df[games_df['gameId'] == game_id]
    home_team_abbr = game_data['homeTeamAbbr'].values[0]
    visitor_team_abbr = game_data['visitorTeamAbbr'].values[0]
    
    home_team_name = team_name_dict.get(home_team_abbr, 'Unknown Team')
    visitor_team_name = team_name_dict.get(visitor_team_abbr, 'Unknown Team')
    
    return home_team_name, visitor_team_name

# Función para obtener los nombres de los equipos para una lista de gameIds
def get_game_team_names(game_ids):
    game_info = []
    for game_id in game_ids:
        home_team, visitor_team = get_team_names(game_id)
        game_info.append(f"{home_team} vs {visitor_team}")
    return game_info

# Solicitar al usuario que ingrese el número de la semana
week = int(input("Introduce el número de la semana (1-9) que deseas cargar: "))

# Cargar los datos de tracking para la semana seleccionada
file_path = f'tracking_week_{week}.csv'
tracking_df = pd.read_csv(file_path)

# Mostrar los gameId disponibles, pero en lugar de gameId mostrar los nombres de los equipos
game_ids = tracking_df['gameId'].unique()
game_names = get_game_team_names(game_ids)
for idx, game_name in enumerate(game_names):
    print(f"{game_ids[idx]}: {game_name}")

# Solicitar al usuario que seleccione un gameId
game_id = int(input("Introduce el gameId que deseas analizar: "))

# Obtener los nombres de los equipos
home_team, visitor_team = get_team_names(game_id)
print(f"Equipos: {home_team} vs {visitor_team}")

# Mostrar los playId disponibles para el gameId seleccionado
play_ids = tracking_df[tracking_df['gameId'] == game_id]['playId'].unique()
print(f"Play IDs disponibles para el gameId {game_id}:", play_ids)

# Solicitar al usuario que seleccione un playId
play_id = int(input(f"Introduce el playId que deseas analizar para el gameId {game_id}: "))

# Filtrar los datos por gameId y playId seleccionados
play_data = tracking_df[(tracking_df['gameId'] == game_id) & (tracking_df['playId'] == play_id)]

# Eliminar filas donde el jugador sea 'NA' (representa la pelota)
ball_data = play_data[play_data['nflId'].isna()]

# Filtrar los jugadores (sin el balón)
play_data = play_data[play_data['nflId'].notna()]

# Filtrar jugadores por equipo si se desea ver solo un equipo
team = 'DEN'  # Cambiar a tu equipo de interés
play_data = play_data[play_data['club'] == team]

# Crear la visualización
plt.figure(figsize=(12, 7))

# Cambiar color de fondo del gráfico para mejorar la visibilidad
plt.gcf().set_facecolor('lightgrey')

# Mostrar la ruta del balón (con x, y)
plt.plot(ball_data['x'], ball_data['y'], color='black', label="Ruta del balón", linestyle='--', alpha=0.6)

# Mostrar las rutas de los jugadores
for player_id in play_data['nflId'].unique():
    player_data = play_data[play_data['nflId'] == player_id]
    
    # Obtener el nombre del jugador
    player_name = str(player_data['displayName'].iloc[0])  # Tomamos el nombre del jugador
    
    # Dibujar la ruta del jugador
    plt.plot(player_data['x'], player_data['y'], label=f"Jugador {player_name}")
    
    # Anotaciones de nombre solo en el primer punto de la ruta
    plt.text(player_data['x'].iloc[0], player_data['y'].iloc[0], 
             f"{player_name}", fontsize=8, ha='right', color='black', weight='bold', 
             bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.3'))

# Ajustar título y etiquetas
plt.title(f"Rutas de Jugadores y Balón - Juego {game_id}, Jugada {play_id}", fontsize=14, weight='bold')
plt.xlabel("Longitud del campo (Yardas)", fontsize=12)
plt.ylabel("Ancho del campo (Yardas)", fontsize=12)
plt.legend(loc="upper left", fontsize=8)
plt.grid(True)

# Mostrar el gráfico
plt.show()
