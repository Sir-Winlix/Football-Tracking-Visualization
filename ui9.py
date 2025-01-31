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

        # Deslizador para ajustar la velocidad
        self.speed_label = tk.Label(root, text="Velocidad de la animación (ms):")
        self.speed_label.pack()
        self.speed_slider = tk.Scale(root, from_=50, to=500, orient="horizontal", length=300)
        self.speed_slider.set(100)  # Valor predeterminado
        self.speed_slider.pack(pady=5)

        # Botón para animar la jugada
        self.plot_button = tk.Button(root, text="Animar Jugada", command=self.animate_play)
        self.plot_button.pack(pady=20)

        # Botón para pausar la animación
        self.pause_button = tk.Button(root, text="Pausar", command=self.pause_animation, state="disabled")
        self.pause_button.pack(pady=10)

        # Variable para almacenar los datos
        self.tracking_df = None
        self.ani = None

    def load_file(self):
        """Permite al usuario cargar un archivo CSV."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                # Indicador de carga
                self.load_button.config(state="disabled", text="Cargando...")
                self.root.update()  # Refresca la interfaz
                self.tracking_df = pd.read_csv(file_path)
                
                required_columns = ['gameId', 'playId', 'nflId', 'displayName', 'x', 'y']
                missing_columns = [col for col in required_columns if col not in self.tracking_df.columns]
                if missing_columns:
                    messagebox.showerror("Error", f"Faltan las siguientes columnas: {', '.join(missing_columns)}")
                    return
                
                print("Archivo cargado con éxito")
                self.update_game_ids()  # Refrescar GameId en caso de que haya un nuevo archivo
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo: {str(e)}")
            finally:
                self.load_button.config(state="normal", text="Cargar Datos")  # Restaurar estado del botón

    def update_game_ids(self):
        """Actualiza el desplegable de Game ID."""
        if self.tracking_df is not None:
            game_ids = self.tracking_df['gameId'].unique().tolist()
            self.game_id_dropdown['values'] = game_ids
            self.game_id_dropdown.state(["!disabled"])
            self.play_id_dropdown.state(["disabled"])

    def update_play_ids(self, event):
        """Actualiza el desplegable de Play ID cuando se selecciona un Game ID."""
        try:
            selected_game_id = int(self.game_id_dropdown.get())
            play_ids = self.tracking_df[self.tracking_df['gameId'] == selected_game_id]['playId'].unique().tolist()
            self.play_id_dropdown['values'] = play_ids
            self.play_id_dropdown.state(["!disabled"])
        except ValueError:
            messagebox.showerror("Error", "Selecciona un Game ID válido")

    def animate_play(self):
        """Genera una animación de la jugada con los datos de tracking."""
        if self.tracking_df is None:
            messagebox.showerror("Error", "Por favor, carga un archivo primero")
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

        # Dibujar las líneas del campo
        self.draw_field(ax)

        # Crear diccionario para guardar los gráficos de cada jugador
        players = {}
        for nfl_id in play_data['nflId'].dropna().unique():
            player_info = play_data[play_data['nflId'] == nfl_id].iloc[0]
            # Formato: "Nombre del Jugador [Dorsal] - Posición"
            label = f"{player_info['displayName']} [{int(player_info['jerseyNumber'])}]"
            if 'position' in player_info.index:
                label += f" - {player_info['position']}"
            if 'teamAbbr' in player_info.index:
                label += f" ({player_info['teamAbbr']})"
            players[nfl_id], = ax.plot([], [], 'o', label=label)

        # Agregar el balón
        ball, = ax.plot([], [], 'ko', markersize=8, label="Balón")

        def update(frame):
            """Actualiza la posición de los jugadores en cada frame."""
            frame_data = play_data[play_data['frameId'] == frame]

            for nfl_id in players.keys():
                player_data = frame_data[frame_data['nflId'] == nfl_id]
                if not player_data.empty:
                    players[nfl_id].set_data(player_data['x'], player_data['y'])

            # Actualizar balón
            ball_data = frame_data[frame_data['nflId'].isna()]
            if not ball_data.empty:
                ball.set_data(ball_data['x'], ball_data['y'])

            return list(players.values()) + [ball]

        # Obtener la velocidad de la animación desde el deslizador
        speed = self.speed_slider.get()

        self.ani = animation.FuncAnimation(fig, update, frames=frames, interval=speed, blit=True)

        # Habilitar el botón de pausa
        self.pause_button.config(state="normal")

        plt.legend(loc="upper left", fontsize=8)
        plt.show()

    def pause_animation(self):
        """Función para pausar la animación"""
        if self.ani:
            self.ani.event_source.stop()  # Detiene la animación

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

# Crear la ventana principal
root = tk.Tk()
app = FootballTrackingApp(root)
root.mainloop()
