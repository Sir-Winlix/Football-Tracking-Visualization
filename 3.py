import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import glob

def load_games_data():
    """Load games data from CSV file."""
    return pd.read_csv('games.csv')

def load_tracking_data(week_input):
    """Load tracking data based on user input."""
    if week_input == '*':
        all_files = glob.glob('tracking_week_*.csv')
        return pd.concat([pd.read_csv(f) for f in all_files])
    else:
        week = int(week_input)
        file_path = f'tracking_week_{week}.csv'
        return pd.read_csv(file_path)

def get_team_names(game_id, games_df, team_name_dict):
    """Get home and visitor team names based on gameId."""
    game_data = games_df[games_df['gameId'] == game_id]
    home_team_abbr = game_data['homeTeamAbbr'].values[0]
    visitor_team_abbr = game_data['visitorTeamAbbr'].values[0]
    
    home_team_name = team_name_dict.get(home_team_abbr, 'Unknown Team')
    visitor_team_name = team_name_dict.get(visitor_team_abbr, 'Unknown Team')
    
    return home_team_name, visitor_team_name

def draw_field(ax, game_id_input, play_id_input):
    """Draw the football field."""
    ax.set_facecolor('lightgreen')
    for i in range(0, 121, 10):
        ax.axvline(x=i, color='white', linewidth=1)
    ax.fill_betweenx([0, 53.3], 0, 10, color='blue', alpha=0.1)
    ax.fill_betweenx([0, 53.3], 110, 120, color='red', alpha=0.1)
    ax.axvline(x=60, color='white', linewidth=3)
    ax.axvline(x=50, color='white', linewidth=2)
    ax.axvline(x=70, color='white', linewidth=2)
    ax.axvline(x=25, color='white', linewidth=2)
    ax.axvline(x=95, color='white', linewidth=2)
    for i in range(1, 11):
        ax.axhline(y=i*5, color='white', linewidth=1)
    ax.text(5, 53, 'Touchdown', color='white', fontsize=12, ha='center', va='center')
    ax.text(115, 53, 'Touchdown', color='white', fontsize=12, ha='center', va='center')
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 53.3)
    ax.set_xlabel("Longitud del campo (Yardas)", fontsize=12)
    ax.set_ylabel("Ancho del campo (Yardas)", fontsize=12)
    ax.set_title(f"Rutas de Jugadores y Balón - Juego {game_id_input}, Jugada {play_id_input}", fontsize=14, weight='bold')

def main():
    games_df = load_games_data()
    week_input = input("Introduce el número de la semana (1-9) que deseas cargar o '*' para todas: ")
    tracking_df = load_tracking_data(week_input)

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

    game_ids = tracking_df['gameId'].unique()
    game_names = [f"{game_id}: {get_team_names(game_id, games_df, team_name_dict)[0]} vs {get_team_names(game_id, games_df, team_name_dict)[1]}" for game_id in game_ids]
    print("\nPartidos disponibles para la semana seleccionada:")
    for game_name in game_names:
        print(game_name)

    game_id_input = int(input("\nIntroduce el gameId que deseas analizar: "))
    home_team, visitor_team = get_team_names(game_id_input, games_df, team_name_dict)
    print(f"\nEquipos: {home_team} vs {visitor_team}")

    play_ids = tracking_df[tracking_df['gameId'] == game_id_input]['playId'].unique()
    print(f"\nPlay IDs disponibles para el gameId {game_id_input}:")
    for play_id in play_ids:
        print(play_id)

    play_id_input = int(input(f"\nIntroduce el playId que deseas analizar para el gameId {game_id_input}: "))

    play_data = tracking_df[(tracking_df['gameId'] == game_id_input) & (tracking_df['playId'] == play_id_input)]
    ball_data = play_data[play_data['nflId'].isna()]
    play_data = play_data[play_data['nflId'].notna()]

    fig, ax = plt.subplots(figsize=(12, 7))
    draw_field(ax, game_id_input, play_id_input)

    ball_line, = ax.plot([], [], color='black', label="Ruta del balón", linestyle='--', alpha=0.6)
    player_lines = {player_id: ax.plot([], [], label=f"{play_data[play_data['nflId'] == player_id]['displayName'].iloc[0]}")[0] for player_id in play_data['nflId'].unique()}

    def init():
        ball_line.set_data([], [])
        for line in player_lines.values():
            line.set_data([], [])
        return [ball_line] + list(player_lines.values())

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

    ani = FuncAnimation(fig, update, frames=len(ball_data), init_func=init, blit=True, interval=50)
    ax.legend()
    plt.show()

if __name__ == "__main__":
    main()