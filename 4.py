import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class FootballTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Football Tracking Visualization")

        # Botón para cargar archivos
        self.load_button = tk.Button(root, text="Cargar Datos", command=self.load_files)
        self.load_button.pack(pady=10)

        # Desplegable de selección de partido
        self.game_label = tk.Label(root, text="Selecciona un partido:")
        self.game_label.pack()
        self.game_dropdown = ttk.Combobox(root, state="disabled")
        self.game_dropdown.pack(pady=5)
        self.game_dropdown.bind("<<ComboboxSelected>>", self.update_game_data)

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

        # Deslizador para ajustar la velocidad
        self.speed_label = tk.Label(root, text="Velocidad de la animación (ms):")
        self.speed_label.pack()
        self.speed_slider = tk.Scale(root, from_=50, to=500, orient="horizontal", length=300)
        self.speed_slider.set(100)  # Valor predeterminado
        self.speed_slider.pack(pady=5)

        # Botón para animar la jugada
        self.plot_button = tk.Button(root, text="Animar Jugada", command=self.animate_play)
        self.plot_button.pack(pady=20)

        # Botón de pausa
        self.pause_button = tk.Button(root, text="Pausar", state="disabled", command=self.pause_animation)
        self.pause_button.pack(pady=5)

        # Variables para almacenar los datos
        self.tracking_data = {}
        self.animation = None  # Asegurarse de que la animación esté inicialmente como None
        self.paused = False

    def load_files(self):
        """Permite al usuario cargar múltiples archivos CSV."""
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        if file_paths:
            try:
                # Cargar cada archivo y agregarlo al diccionario de tracking_data
                for file_path in file_paths:
                    df = pd.read_csv(file_path)
                    game_id = df['gameId'].iloc[0]  # Suponemos que todos los registros en un archivo tienen el mismo gameId
                    self.tracking_data[file_path] = df
                    print(f"Archivo {file_path} cargado con éxito")

                # Agregar los nombres de los archivos al desplegable de selección de partido
                self.game_dropdown['values'] = list(self.tracking_data.keys())
                self.game_dropdown.state(["!disabled"])

            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar los archivos: {str(e)}")

    def update_game_data(self, event):
        """Actualiza los desplegables de Game ID y Play ID según el archivo seleccionado."""
        selected_file = self.game_dropdown.get()
        if selected_file in self.tracking_data:
            self.selected_data = self.tracking_data[selected_file]

            # Obtener GameIds únicos y cargar en el desplegable
            game_ids = self.selected_data['gameId'].unique().tolist()
            self.game_id_dropdown['values'] = game_ids
            self.game_id_dropdown.state(["!disabled"])

    def update_play_ids(self, event):
        """Actualiza el desplegable de Play ID cuando se selecciona un Game ID."""
        try:
            selected_game_id = int(self.game_id_dropdown.get())
            play_ids = self.selected_data[self.selected_data['gameId'] == selected_game_id]['playId'].unique().tolist()
            self.play_id_dropdown['values'] = play_ids
            self.play_id_dropdown.state(["!disabled"])
        except ValueError:
            messagebox.showerror("Error", "Selecciona un Game ID válido")

    def animate_play(self):
        """Genera una animación de la jugada con los datos de tracking."""
        if not hasattr(self, 'selected_data'):
            messagebox.showerror("Error", "Por favor, selecciona un partido primero")
            return

        game_id = int(self.game_id_dropdown.get())
        play_id = int(self.play_id_dropdown.get())

        # Filtrar los datos según el gameId y playId
        play_data = self.selected_data[(self.selected_data['gameId'] == game_id) & (self.selected_data['playId'] == play_id)]

        # Obtener los frames únicos (tiempos en la jugada)
        frames = sorted(play_data['frameId'].unique())

        # Crear la figura
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.set_xlim(0, 120)  # Dimensiones del campo
        ax.set_ylim(0, 53.3)
        ax.set_xlabel("Longitud del campo (yardas)")
        ax.set_ylabel("Ancho del campo (yardas)")
        ax.set_title(f"Animación - Juego {game_id}, Jugada {play_id}")

        # Dibujar las líneas del campo
        self.draw_field(ax)

        # Crear diccionario para guardar los gráficos de cada jugador
        players = {}
        player_trails = {}
        for nfl_id in play_data['nflId'].dropna().unique():
            player_info = play_data[play_data['nflId'] == nfl_id].iloc[0]
            # Formato: "Nombre del Jugador [Dorsal] - Posición"
            label = f"{player_info['displayName']} [{int(player_info['jerseyNumber'])}]"
            if 'position' in player_info.index:
                label += f" - {player_info['position']}"
            if 'teamAbbr' in player_info.index:
                label += f" ({player_info['teamAbbr']})"
            players[nfl_id], = ax.plot([], [], 'o', label=label)
            player_trails[nfl_id], = ax.plot([], [], '-', lw=1)

        # Agregar el balón
        ball, = ax.plot([], [], 'ko', markersize=8, label="Balón")
        ball_trail, = ax.plot([], [], 'k-', lw=1)

        def update(frame):
            """Actualiza la posición de los jugadores en cada frame."""
            frame_data = play_data[play_data['frameId'] == frame]

            for nfl_id in players.keys():
                player_data = frame_data[frame_data['nflId'] == nfl_id]
                if not player_data.empty:
                    players[nfl_id].set_data(player_data['x'], player_data['y'])
                    
                    # Actualizar el trazado de jugadores
                    prev_x, prev_y = player_trails[nfl_id].get_data()
                    
                    # Si no hay datos previos (primera vez), inicializa como listas vacías
                    if prev_x is None or prev_y is None:
                        prev_x, prev_y = [], []

                    # Añadir las nuevas coordenadas al trazado
                    new_x = prev_x + [player_data['x'].iloc[0]]
                    new_y = prev_y + [player_data['y'].iloc[0]]
                    player_trails[nfl_id].set_data(new_x, new_y)

            # Actualizar balón
            ball_data = frame_data[frame_data['nflId'].isna()]
            if not ball_data.empty:
                ball.set_data(ball_data['x'], ball_data['y'])
                
                # Actualizar el trazado del balón
                prev_x, prev_y = ball_trail.get_data()
                if prev_x is None or prev_y is None:
                    prev_x, prev_y = [], []

                new_x = prev_x + [ball_data['x'].iloc[0]]
                new_y = prev_y + [ball_data['y'].iloc[0]]
                ball_trail.set_data(new_x, new_y)

            return list(players.values()) + list(player_trails.values()) + [ball, ball_trail]

        # Obtener la velocidad de la animación desde el deslizador
        speed = self.speed_slider.get()

        self.animation = animation.FuncAnimation(fig, update, frames=frames, interval=speed, blit=True)

        # Habilitar el botón de pausa
        self.pause_button.config(state="normal")

        plt.legend(loc="upper left", fontsize=8)
        plt.show()

    def draw_field(self, ax):
        """Dibuja el campo de fútbol con líneas de yardas y zonas de anotación."""
        # Líneas de las zonas de anotación
        ax.axvline(x=0, color="black", lw=2)
        ax.axvline(x=120, color="black", lw=2)

        # Líneas de las 50 yardas y los límites del campo
        for x in range(10, 120, 10):
            ax.axvline(x=x, color="black", lw=1, ls="--")
        
        # Líneas de las 5 yardas
        for x in range(5, 120, 5):
            ax.axvline(x=x, color="gray", lw=0.5, ls="--")

        # Líneas de las 10 yardas
        for x in range(10, 120, 10):
            ax.text(x, 53.3, f"{x}", ha="center", va="top", fontsize=8, color="black")

        # Línea central
        ax.axvline(x=60, color="black", lw=2)

        # Marcar el medio campo
        ax.text(60, 53.3, "Medio Campo", ha="center", va="top", fontsize=10, color="black")

        # Zonas de los equipos (si es necesario)
        ax.fill_betweenx([0, 53.3], 0, 10, color="lightgreen", alpha=0.3)  # Zona 1
        ax.fill_betweenx([0, 53.3], 110, 120, color="lightgreen", alpha=0.3)  # Zona 2

    def pause_animation(self):
        """Pausar la animación."""
        if self.animation:  # Verificar si la animación ha sido creada
            if self.paused:
                self.animation.event_source.start()
                self.pause_button.config(text="Pausar")
                self.paused = False
            else:
                self.animation.event_source.stop()
                self.pause_button.config(text="Reanudar")
                self.paused = True
        else:
            messagebox.showwarning("Advertencia", "La animación no se ha iniciado aún.")

# Crear la ventana principal
root = tk.Tk()
app = FootballTrackingApp(root)
root.mainloop()
