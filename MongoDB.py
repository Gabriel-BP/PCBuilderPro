import pandas as pd
import re
from pymongo import MongoClient

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["componentes_pc"]

def parse_precios(precios_str):
    # Extrae precios usando expresiones regulares
    precios = re.findall(r'(\d+,\d+|\d+|\d+\.\d+|\d+,\d+€)', precios_str)
    nuevo = None
    usado = None
    
    if 'Nuevo' in precios_str and 'Usado' in precios_str:
        split_idx = precios_str.index('Usado')
        nuevo = precios_str[:split_idx].strip()
        usado = precios_str[split_idx:].strip()
    elif 'Nuevo' in precios_str:
        nuevo = precios_str.strip()
    elif 'Usado' in precios_str:
        usado = precios_str.strip()
    
    return {
        'nuevo': float(nuevo.replace('€', '').replace(',', '.')) if nuevo else None,
        'usado': float(usado.replace('€', '').replace(',', '.')) if usado else None
    }

def parse_caracteristicas(caracteristicas_str):
    # Convierte la cadena de características en un diccionario
    caracteristicas = {}
    for item in caracteristicas_str.split(','):
        if ':' in item:
            key, value = item.split(':', 1)
            caracteristicas[key.strip()] = value.strip()
    return caracteristicas

def procesar_archivo(nombre_archivo, coleccion):
    df = pd.read_csv(nombre_archivo)
    
    for _, row in df.iterrows():
        documento = {
            'url': row['URL'],
            'nombre': row['Nombre'],
            'descripcion': row['Descripción'],
            'imagen': row['Imagen'],
            'precios': parse_precios(row['Precios']),
            'caracteristicas': parse_caracteristicas(row['Características'])
        }
        db[coleccion].insert_one(documento)

# Procesar cada archivo CSV
archivos = [
    ('productos_procesados/case_productos.csv', 'cases'),
    ('productos_procesados/cooler_productos.csv', 'coolers'),
    ('productos_procesados/graphic-card_productos.csv', 'tarjetas_graficas'),
    ('productos_procesados/memory_productos.csv', 'memorias'),
    ('productos_procesados/motherboard_productos.csv', 'placas_base'),
    ('productos_procesados/power-supply_productos.csv', 'fuentes_poder'),
    ('productos_procesados/processor_productos.csv', 'procesadores'),
    ('productos_procesados/storage_productos.csv', 'almacenamiento')
]

for archivo, coleccion in archivos:
    print(f"Procesando {archivo} en colección {coleccion}...")
    procesar_archivo(archivo, coleccion)