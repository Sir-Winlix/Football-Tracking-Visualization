import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Cargar los archivos de juegos y tracking
games_df = pd.read_csv('games.csv')

# Solicitar al usuario que ingrese la semana
week_input = input("Introduce el número de la semana (1-9) que deseas cargar o '*' para todas: ")

# Si se selecciona '*', cargar todos los datos
if week_input == '*':
    tracking_df = pd.concat([pd.read_csv(f'tracking_week_{week}.csv') for week in range(1, 10)])
else:
    week = int(week_input)
    file_path = f'tracking_week_{week}.csv'
    tracking_df = pd.read_csv(file_path)

# Función para obtener los nombres de los equipos con base en gameId
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

def get_team_names(game_id):
    game_data = games_df[games_df['gameId'] == game_id]
    home_team_abbr = game_data['homeTeamAbbr'].values[0]
    visitor_team_abbr = game_data['visitorTeamAbbr'].values[0]
    
    home_team_name = team_name_dict.get(home_team_abbr, 'Unknown Team')
    visitor_team_name = team_name_dict.get(visitor_team_abbr, 'Unknown Team')
    
    return home_team_name, visitor_team_name

# Mostrar los gameId disponibles para la semana seleccionada
game_ids = tracking_df['gameId'].unique()
game_names = [f"{game_id}: {get_team_names(game_id)[0]} vs {get_team_names(game_id)[1]}" for game_id in game_ids]
print("\nPartidos disponibles para la semana seleccionada:")
for game_name in game_names:
    print(game_name)

# Solicitar al usuario que seleccione un gameId
game_id_input = int(input("\nIntroduce el gameId que deseas analizar: "))
home_team, visitor_team = get_team_names(game_id_input)
print(f"\nEquipos: {home_team} vs {visitor_team}")

# Obtener los playId disponibles para el gameId seleccionado
play_ids = tracking_df[tracking_df['gameId'] == game_id_input]['playId'].unique()
print(f"\nPlay IDs disponibles para el gameId {game_id_input}:")
for play_id in play_ids:
    print(play_id)

# Solicitar al usuario que seleccione un playId
play_id_input = int(input(f"\nIntroduce el playId que deseas analizar para el gameId {game_id_input}: "))

# Filtrar datos de tracking
play_data = tracking_df[(tracking_df['gameId'] == game_id_input) & (tracking_df['playId'] == play_id_input)]
ball_data = play_data[play_data['nflId'].isna()]
play_data = play_data[play_data['nflId'].notna()]

# Crear la visualización del campo
fig, ax = plt.subplots(figsize=(12, 7))

# Dibujar el campo
def draw_field():
    # Colores de fondo
    ax.set_facecolor('lightgreen')
    
    # Líneas de 10 yardas
    for i in range(0, 121, 10):
        ax.axvline(x=i, color='white', linewidth=1)
    
    # Líneas de zona de touchdown
    ax.fill_betweenx([0, 53.3], 0, 10, color='blue', alpha=0.1)  # Zona de touchdown izquierda
    ax.fill_betweenx([0, 53.3], 110, 120, color='red', alpha=0.1)  # Zona de touchdown derecha
    
    # Línea central
    ax.axvline(x=60, color='white', linewidth=3)
    
    # Líneas de la zona de las 50 yardas
    ax.axvline(x=50, color='white', linewidth=2)
    ax.axvline(x=70, color='white', linewidth=2)
    
    # Líneas de las 25 yardas
    ax.axvline(x=25, color='white', linewidth=2)
    ax.axvline(x=95, color='white', linewidth=2)
    
    # Líneas horizontales de las 5 yardas
    for i in range(1, 11):
        ax.axhline(y=i*5, color='white', linewidth=1)

    # Anotaciones
    ax.text(5, 53, 'Touchdown', color='white', fontsize=12, ha='center', va='center')
    ax.text(115, 53, 'Touchdown', color='white', fontsize=12, ha='center', va='center')
    
    # Limitar la vista del campo
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 53.3)
    ax.set_xlabel("Longitud del campo (Yardas)", fontsize=12)
    ax.set_ylabel("Ancho del campo (Yardas)", fontsize=12)
    ax.set_title(f"Rutas de Jugadores y Balón - Juego {game_id_input}, Jugada {play_id_input}", fontsize=14, weight='bold')

# Llamar a la función para dibujar el campo
draw_field()

# Mostrar la ruta del balón (con x, y)
ball_line, = ax.plot([], [], color='black', label="Ruta del balón", linestyle='--', alpha=0.6)

# Inicialización de las rutas de los jugadores
player_lines = {}

for player_id in play_data['nflId'].unique():
    player_data = play_data[play_data['nflId'] == player_id]
    player_lines[player_id], = ax.plot([], [], label=f"Jugador {player_data['displayName'].iloc[0]}")

# Función de inicialización
def init():
    ball_line.set_data([], [])
    for line in player_lines.values():
        line.set_data([], [])
    return [ball_line] + list(player_lines.values())

# Función de actualización para la animación
def update(frame):
    ball_x = ball_data['x'][:frame]
    ball_y = ball_data['y'][:frame]
    ball_line.set_data(ball_x, ball_y)

    for player_id, line in player_lines.items():
        player_data = play_data[play_data['nflId'] == player_id]
        player_x = player_data['x'][:frame]
        player_y = player_data['y'][:frame]
        line.set_data(player_x, player_y)

    return [ball_line] + list(player_lines.values())

# Crear la animación
ani = FuncAnimation(fig, update, frames=len(ball_data), init_func=init, blit=True, interval=50)

# Mostrar la animación
plt.show()
