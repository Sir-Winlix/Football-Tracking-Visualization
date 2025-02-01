import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
from tqdm import tqdm  # Usaremos tqdm para mostrar el progreso de la carga de archivos

# Define el nflId de Patrick Mahomes
nflId_mahones = 44822

# Cargar los datos de seguimiento de las semanas 1 a 9
tracking_files = glob.glob('tracking_week_*.csv')  # Asegúrate de que los archivos estén en el directorio correcto

# Crear un dataframe vacío donde se cargarán todos los datos
tracking_data = pd.DataFrame()

# Usamos tqdm para mostrar el progreso
print("Cargando los archivos de seguimiento...")

# Leer cada archivo de tracking y concatenarlo
for file in tqdm(tracking_files, desc="Cargando archivos", unit="archivo"):
    try:
        week_data = pd.read_csv(file)
        tracking_data = pd.concat([tracking_data, week_data], ignore_index=True)
    except Exception as e:
        print(f"Error al leer el archivo {file}: {e}")

# Mostrar el tamaño del dataframe cargado
print(f"Datos cargados: {tracking_data.shape[0]} filas y {tracking_data.shape[1]} columnas.")

# Filtrar los datos para obtener solo los de Mahomes
print(f"Filtrando los datos para Patrick Mahomes (nflId: {nflId_mahones})...")
mahomes_data = tracking_data[tracking_data['nflId'] == nflId_mahones]

# Mostrar los primeros datos de Mahomes para confirmar que se ha hecho correctamente
print(mahomes_data.head())

# Crear el mapa de calor basado en las posiciones x, y de Mahomes
plt.figure(figsize=(10, 6))

# Usar seaborn para crear un mapa de calor de las posiciones (x, y) de Mahomes
heatmap_data = mahomes_data[['x', 'y']]

# Crear un mapa de calor en un gráfico de dispersión
sns.kdeplot(x=heatmap_data['x'], y=heatmap_data['y'], cmap='Blues', fill=True, thresh=0, levels=20)

plt.title('Mapa de Calor de los Movimientos de Patrick Mahomes')
plt.xlabel('Posición X (Yardas)')
plt.ylabel('Posición Y (Yardas)')
plt.show()

print("Proceso completado.")
