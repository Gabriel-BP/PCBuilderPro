import os
import pandas as pd

# Función para determinar si un enlace es específico de un producto
def is_product_link(link):
    # Un enlace de producto debe tener al menos un segmento adicional después de la categoría
    parts = link.split('/')
    return len(parts) > 5 and parts[-1] != ""

# Obtener la ruta de la carpeta actual
folder_path = os.getcwd()

# Iterar sobre todos los archivos en la carpeta actual
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):  # Procesar solo archivos CSV
        file_path = os.path.join(folder_path, filename)
        
        # Leer el archivo CSV
        df = pd.read_csv(file_path)
        
        # Asumimos que la columna con los enlaces se llama "Product Link"
        if "Product Link" in df.columns:
            links = df["Product Link"].dropna().tolist()  # Obtener los enlaces y eliminar valores nulos
            
            # Filtrar enlaces para mantener solo los que son específicos de productos
            product_links = [link for link in links if is_product_link(link)]
            
            # Eliminar duplicados usando un conjunto
            unique_links = list(set(product_links))
            
            # Crear el nombre del nuevo archivo CSV
            base_name = filename.replace("_links.csv", "")  # Extraer el nombre base (e.g., "case")
            output_file = f"unique_{base_name}_links.csv"
            output_path = os.path.join(folder_path, output_file)
            
            # Guardar los enlaces únicos en un nuevo archivo CSV
            pd.DataFrame({"Unique Product Links": unique_links}).to_csv(output_path, index=False)
            
            print(f"Se han guardado {len(unique_links)} enlaces únicos en '{output_file}'.")

print("Proceso completado.")