import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos (ajusta las rutas según tu estructura de archivos)
try:
    games = pd.read_csv('games.csv')
    plays = pd.read_csv('plays.csv')
    players = pd.read_csv('players.csv')
    player_play = pd.read_csv('player_play.csv')
except FileNotFoundError as e:
    st.error(f"Error al cargar los archivos: {e}")
    st.stop()

# Seleccionar semana de seguimiento
week_number = st.selectbox("Selecciona la semana de seguimiento:", range(1, 10))

# Cargar los datos de seguimiento de la semana seleccionada
tracking_week_file = f'tracking_week_{week_number}.csv'  # El archivo cambia según la semana
try:
    tracking_week = pd.read_csv(tracking_week_file)
except FileNotFoundError:
    st.error(f"No se encontraron datos de seguimiento para la semana {week_number}.")
    st.stop()

# Verificar si la columna 'week' existe en el DataFrame de juegos
if 'week' not in games.columns:
    st.error("No se encontró la columna 'week' en el archivo de partidos. Asegúrate de que los datos estén correctamente formateados.")
    st.stop()

# Filtrar los partidos por semana seleccionada
games_filtered = games[games['week'] == week_number]  # Usamos 'week' para filtrar los partidos

# Verificar si hay partidos en la semana seleccionada
if games_filtered.empty:
    st.warning(f"No se encontraron partidos para la semana {week_number}.")
    st.stop()

# Título de la aplicación
st.title("Football Tracking Visualization")

# Seleccionar partido de la semana filtrada
selected_game = st.selectbox("Selecciona un partido:", games_filtered['gameId'].unique())

# Filtrar jugadas del partido seleccionado
plays_filtered = plays[plays['gameId'] == selected_game]
if plays_filtered.empty:
    st.warning("No se encontraron jugadas para este partido.")
    st.stop()

selected_play = st.selectbox("Selecciona una jugada:", plays_filtered['playId'].unique())

# Mostrar descripción de la jugada seleccionada
play_desc = plays_filtered[plays_filtered['playId'] == selected_play]['playDescription'].values[0]
st.write(f"**Descripción de la jugada:** {play_desc}")

# Filtrar datos de jugadores en la jugada seleccionada
player_data = player_play[(player_play['gameId'] == selected_game) & (player_play['playId'] == selected_play)]

# Filtrar los datos de seguimiento para la jugada y el partido seleccionados
tracking_filtered = tracking_week[(tracking_week['gameId'] == selected_game) & (tracking_week['playId'] == selected_play)]

# Verificar si hay datos de seguimiento
if tracking_filtered.empty:
    st.warning("No se encontraron datos de seguimiento para esta jugada.")
    st.stop()

# Unir los datos de seguimiento con los datos de jugador
player_tracking_data = pd.merge(player_data, tracking_filtered, on=['gameId', 'playId', 'nflId'])

# Filtrar los datos de la pelota (donde nflId es NA)
ball_data = tracking_filtered[tracking_filtered['nflId'].isna()]

# Asegurarse de que la pelota siempre se agregue correctamente
ball_data['nflId'] = 'Ball'  
ball_data['displayName'] = 'Pelota'
ball_data['club'] = 'Ball'

# Combinar los datos de jugadores y la pelota en un solo DataFrame
combined_data = pd.concat([player_tracking_data, ball_data])

# Verificar si 'club' está presente como columna en el DataFrame
if 'club' in combined_data.columns:
    color_column = 'club'
else:
    st.warning("'club' no se encuentra, usando 'displayName' para los colores.")
    color_column = 'displayName'

# Asegurarse de que 'frameId' esté presente en los datos
if 'frameId' not in combined_data.columns:
    st.warning("No se encontraron datos de 'frameId'. No se podrá realizar la animación.")
    st.stop()

# Visualizar usando las columnas correctas para las coordenadas y colores
# Animar usando 'frameId' para mostrar el movimiento a lo largo del tiempo
fig = px.scatter(combined_data, x='x', y='y', color=color_column, hover_data=['nflId'],
                 animation_frame='frameId', 
                 title="Movimiento de jugadores y pelota durante la jugada")

# Mostrar el gráfico interactivo
st.plotly_chart(fig)
