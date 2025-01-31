import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class FootballTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Football Tracking Visualization")

        # Botón para cargar archivo
        self.load_button = tk.Button(root, text="Cargar Datos", command=self.load_file)
        self.load_button.pack(pady=10)

        # Desplegable GameId
        self.game_id_label = tk.Label(root, text="Selecciona Game ID:")
        self.game_id_label.pack()
        self.game_id_dropdown = ttk.Combobox(root, state="disabled")
        self.game_id_dropdown.pack(pady=5)
        self.game_id_dropdown.bind("<<ComboboxSelected>>", self.update_play_ids)

        # Desplegable PlayId
        self.play_id_label = tk.Label(root, text="Selecciona Play ID:")
        self.play_id_label.pack()
        self.play_id_dropdown = ttk.Combobox(root, state="disabled")
        self.play_id_dropdown.pack(pady=5)

        # Botón para animar la jugada
        self.plot_button = tk.Button(root, text="Animar Jugada", command=self.animate_play)
        self.plot_button.pack(pady=20)

        # Variables para almacenar los datos
        self.tracking_df = None
        self.players_df = None

    def load_file(self):
        """Permite al usuario cargar un archivo CSV."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.tracking_df = pd.read_csv(file_path)
            print("Archivo de tracking cargado con éxito")

            # Cargar los datos de jugadores (players.csv)
            players_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")], title="Cargar jugadores CSV")
            if players_path:
                self.players_df = pd.read_csv(players_path)
                self.players_df = self.players_df[['nflId', 'displayName']]

            # Obtener GameId únicos y cargar en el desplegable
            game_ids = self.tracking_df['gameId'].unique().tolist()
            self.game_id_dropdown['values'] = game_ids
            self.game_id_dropdown.state(["!disabled"])
            self.play_id_dropdown.state(["disabled"])

    def update_play_ids(self, event):
        """Actualiza el desplegable de Play ID cuando se selecciona un Game ID."""
        selected_game_id = int(self.game_id_dropdown.get())
        play_ids = self.tracking_df[self.tracking_df['gameId'] == selected_game_id]['playId'].unique().tolist()
        self.play_id_dropdown['values'] = play_ids
        self.play_id_dropdown.state(["!disabled"])

    def animate_play(self):
        """Genera una animación de la jugada con los datos de tracking."""
        if self.tracking_df is None or self.players_df is None:
            print("Por favor, carga los archivos primero")
            return

        game_id = int(self.game_id_dropdown.get())
        play_id = int(self.play_id_dropdown.get())

        # Filtrar los datos según el gameId y playId
        play_data = self.tracking_df[(self.tracking_df['gameId'] == game_id) & (self.tracking_df['playId'] == play_id)]

        # Obtener los frames únicos (tiempos en la jugada)
        frames = sorted(play_data['frameId'].unique())

        # Crear la figura
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.set_xlim(0, 120)  # Dimensiones del campo
        ax.set_ylim(0, 53.3)
        ax.set_xlabel("Longitud del campo (yardas)")
        ax.set_ylabel("Ancho del campo (yardas)")
        ax.set_title(f"Animación - Juego {game_id}, Jugada {play_id}")

        # Crear diccionario para guardar los gráficos de cada jugador
        players = {}
        player_names = {}  # Para almacenar los nombres de los jugadores
        for nfl_id in play_data['nflId'].dropna().unique():
            # Obtener el nombre del jugador del DataFrame de jugadores
            player_name = self.players_df[self.players_df['nflId'] == nfl_id]['displayName'].iloc[0]
            player_names[nfl_id] = player_name
            players[nfl_id], = ax.plot([], [], 'o', label=f"Jugador {int(nfl_id)}")

        # Agregar el balón
        ball, = ax.plot([], [], 'ko', markersize=8, label="Balón")

        def update(frame):
            """Actualiza la posición de los jugadores en cada frame."""
            frame_data = play_data[play_data['frameId'] == frame]

            for nfl_id in players.keys():
                player_data = frame_data[frame_data['nflId'] == nfl_id]
                if not player_data.empty:
                    players[nfl_id].set_data(player_data['x'], player_data['y'])
                    # Añadir el nombre del jugador junto al marcador
                    ax.text(player_data['x'].values[0], player_data['y'].values[0], player_names[nfl_id], 
                            fontsize=8, ha='center', color=players[nfl_id].get_color())

            # Actualizar balón
            ball_data = frame_data[frame_data['nflId'].isna()]
            if not ball_data.empty:
                ball.set_data(ball_data['x'], ball_data['y'])

            return list(players.values()) + [ball]

        ani = animation.FuncAnimation(fig, update, frames=frames, interval=100, blit=True)

        plt.legend(loc="upper left", fontsize=8)
        plt.show()

# Crear la ventana principal
root = tk.Tk()
app = FootballTrackingApp(root)
root.mainloop()
