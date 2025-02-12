import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar los datos (ajusta las rutas según tu estructura de archivos)
def load_data():
    try:
        games = pd.read_csv('games.csv')
        plays = pd.read_csv('plays.csv')
        players = pd.read_csv('players.csv')
        player_play = pd.read_csv('player_play.csv')
        return games, plays, players, player_play
    except FileNotFoundError as e:
        st.error(f"Error al cargar los archivos: {e}")
        st.stop()

games, plays, players, player_play = load_data()

# Sidebar para selección de semana y partido
st.sidebar.title("Opciones de visualización")
week_number = st.sidebar.selectbox("Selecciona la semana de seguimiento:", range(1, 10))

# Cargar los datos de seguimiento para la semana seleccionada
tracking_week_file = f'tracking_week_{week_number}.csv'  
try:
    tracking_week = pd.read_csv(tracking_week_file)
except FileNotFoundError:
    st.sidebar.error(f"No se encontraron datos de seguimiento para la semana {week_number}.")
    st.stop()

# Filtrar los partidos por semana seleccionada
games_filtered = games[games['week'] == week_number]  

if games_filtered.empty:
    st.sidebar.warning(f"No se encontraron partidos para la semana {week_number}.")
    st.stop()

# Mostrar los partidos disponibles con el nombre de los equipos
games_filtered['matchup'] = games_filtered['homeTeamAbbr'] + " vs " + games_filtered['visitorTeamAbbr']
selected_game = st.sidebar.selectbox("Selecciona un partido:", games_filtered['matchup'].unique())

# Obtener el gameId basado en el partido seleccionado
selected_game_id = games_filtered[games_filtered['matchup'] == selected_game]['gameId'].values[0]

# Verificar si el gameId existe en los datos de juegos
if selected_game_id not in games['gameId'].values:
    st.error(f"El gameId {selected_game_id} no se encuentra en el conjunto de datos.")
    st.stop()

# Filtrar los detalles del partido
game_details = games[games['gameId'] == selected_game_id]
home_team = game_details['homeTeamAbbr'].values[0]
visitor_team = game_details['visitorTeamAbbr'].values[0]
home_score = game_details['homeFinalScore'].values[0]
visitor_score = game_details['visitorFinalScore'].values[0]
st.write(f"**Partido**: {home_team} vs {visitor_team}")
st.write(f"**Marcador Final**: {home_team} {home_score} - {visitor_team} {visitor_score}")

# Filtrar jugadas del partido seleccionado
plays_filtered = plays[plays['gameId'] == selected_game_id]
if plays_filtered.empty:
    st.sidebar.warning("No se encontraron jugadas para este partido.")
    st.stop()

selected_play = st.sidebar.selectbox("Selecciona una jugada:", plays_filtered['playId'].unique())

# Mostrar descripción de la jugada seleccionada
play_desc = plays_filtered[plays_filtered['playId'] == selected_play]['playDescription'].values[0]
st.write(f"**Descripción de la jugada:** {play_desc}")

# Extraer estadísticas de la jugada seleccionada
play_stats = plays_filtered[plays_filtered['playId'] == selected_play].iloc[0]
play_type = play_stats['playType'] if 'playType' in play_stats else 'Desconocido'
yards_gained = play_stats['yardsGained'] if 'yardsGained' in play_stats else 'Desconocido'
st.write(f"**Tipo de Jugada:** {play_type}")
st.write(f"**Yardas Ganadas:** {yards_gained}")

# Filtrar datos de jugadores en la jugada seleccionada
player_data = player_play[(player_play['gameId'] == selected_game_id) & (player_play['playId'] == selected_play)]

# Mostrar estadísticas de los jugadores involucrados en la jugada
if not player_data.empty:
    st.write("**Estadísticas de Jugadores Involucrados en la Jugada:**")
    for index, row in player_data.iterrows():
        player_name = players[players['nflId'] == row['nflId']]['displayName'].values[0]
        rushing_yards = row['rushingYards'] if 'rushingYards' in row and row['rushingYards'] > 0 else None
        passing_yards = row['passingYards'] if 'passingYards' in row and row['passingYards'] > 0 else None
        if rushing_yards or passing_yards:
            st.write(f"- {player_name}: Carreras: {rushing_yards if rushing_yards else 0} yardas, Pases: {passing_yards if passing_yards else 0} yardas")

# Filtrar los datos de seguimiento para la jugada y el partido seleccionados
tracking_filtered = tracking_week[(tracking_week['gameId'] == selected_game_id) & (tracking_week['playId'] == selected_play)]

if tracking_filtered.empty:
    st.warning("No se encontraron datos de seguimiento para esta jugada.")
    st.stop()

# Unir los datos de seguimiento con los datos de jugador
player_tracking_data = pd.merge(player_data, tracking_filtered, on=['gameId', 'playId', 'nflId'])

# Filtrar los datos de la pelota (donde nflId es NA)
ball_data = tracking_filtered[tracking_filtered['nflId'].isna()]
ball_data['nflId'] = 'Ball'  
ball_data['displayName'] = 'Pelota'
ball_data['club'] = 'Ball'

# Combinar los datos de jugadores y la pelota en un solo DataFrame
combined_data = pd.concat([player_tracking_data, ball_data])

# Verificar si 'club' está presente como columna en el DataFrame
color_column = 'club' if 'club' in combined_data.columns else 'displayName'

# Verificar si 'frameId' está presente en los datos
if 'frameId' not in combined_data.columns:
    st.warning("No se encontraron datos de 'frameId'. No se podrá realizar la animación.")
    st.stop()

# Crear el gráfico de seguimiento de jugadores y pelota
fig = px.scatter(combined_data, x='x', y='y', color=color_column, hover_data=['nflId'],
                 animation_frame='frameId', 
                 title="Movimiento de jugadores y pelota durante la jugada")

# Mostrar el gráfico interactivo
st.plotly_chart(fig)

# Adicionalmente, incluir un slider para explorar las jugadas con diferentes intervalos de tiempo
time_slider = st.slider("Selecciona el intervalo de tiempo para la animación", 
                        min_value=combined_data['frameId'].min(), 
                        max_value=combined_data['frameId'].max(), 
                        value=(combined_data['frameId'].min(), combined_data['frameId'].max()))
