import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt

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
        self.game_id_dropdown.bind("<<ComboboxSelected>>", self.update_play_ids)  # Evento de selección
        
        # Desplegable PlayId
        self.play_id_label = tk.Label(root, text="Selecciona Play ID:")
        self.play_id_label.pack()
        self.play_id_dropdown = ttk.Combobox(root, state="disabled")
        self.play_id_dropdown.pack(pady=5)
        
        # Botón para generar el gráfico
        self.plot_button = tk.Button(root, text="Generar Gráfico", command=self.plot_data)
        self.plot_button.pack(pady=20)
        
        # Variable para almacenar los datos
        self.tracking_df = None
    
    def load_file(self):
        """Permite al usuario cargar un archivo CSV."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.tracking_df = pd.read_csv(file_path)
            print("Archivo cargado con éxito")
            
            # Obtener GameId únicos y cargar en el desplegable
            game_ids = self.tracking_df['gameId'].unique().tolist()
            self.game_id_dropdown['values'] = game_ids
            self.game_id_dropdown.state(["!disabled"])  # Habilitar el desplegable
            self.play_id_dropdown.state(["disabled"])  # Deshabilitar PlayId hasta que se seleccione un GameId

    def update_play_ids(self, event):
        """Actualiza el desplegable de Play ID cuando se selecciona un Game ID."""
        selected_game_id = int(self.game_id_dropdown.get())
        play_ids = self.tracking_df[self.tracking_df['gameId'] == selected_game_id]['playId'].unique().tolist()
        self.play_id_dropdown['values'] = play_ids
        self.play_id_dropdown.state(["!disabled"])  # Habilitar el desplegable

    def plot_data(self):
        """Genera y muestra el gráfico basado en los datos cargados."""
        if self.tracking_df is None:
            print("Por favor, carga un archivo primero")
            return
        
        game_id = int(self.game_id_dropdown.get())
        play_id = int(self.play_id_dropdown.get())
        
        # Filtrar los datos según el gameId y playId
        play_data = self.tracking_df[(self.tracking_df['gameId'] == game_id) & (self.tracking_df['playId'] == play_id)]
        
        # Filtrar balón y jugadores
        ball_data = play_data[play_data['nflId'].isna()]
        play_data = play_data[play_data['nflId'].notna()]
        
        # Crear el gráfico
        plt.figure(figsize=(12, 7))
        
        # Ruta del balón
        plt.plot(ball_data['x'], ball_data['y'], color='black', label="Ruta del balón", linestyle='--', alpha=0.6)
        
        # Rutas de los jugadores
        for player_id in play_data['nflId'].unique():
            player_data = play_data[play_data['nflId'] == player_id]
            player_jersey_number = str(player_data['jerseyNumber'].iloc[0])  # Número de camiseta
            
            # Dibujar la ruta del jugador
            plt.plot(player_data['x'], player_data['y'], label=f"Jugador {player_jersey_number}")
        
        plt.title(f"Rutas de Jugadores y Balón - Juego {game_id}, Jugada {play_id}")
        plt.xlabel("Longitud del campo (Yardas)")
        plt.ylabel("Ancho del campo (Yardas)")
        plt.legend(loc="upper left", fontsize=8)
        plt.grid(True)
        
        # Mostrar el gráfico
        plt.show()

# Crear la ventana principal
root = tk.Tk()
app = FootballTrackingApp(root)
root.mainloop()
