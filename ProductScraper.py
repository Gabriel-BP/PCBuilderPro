import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup
import os
import time

# Configuración inicial
scraper = cloudscraper.create_scraper()
MAX_RETRIES = 3
DELAY_BETWEEN_REQUESTS = 5  # Segundos

# Crear directorio de salida si no existe
output_dir = "productos_procesados"
os.makedirs(output_dir, exist_ok=True)

def scrape_product(url):
    """Extrae datos de un producto con manejo de errores"""
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = scraper.get(url)
            
            if response.status_code == 429:
                print(f"Error 429: Esperando {DELAY_BETWEEN_REQUESTS*2} segundos...")
                time.sleep(DELAY_BETWEEN_REQUESTS * 2)
                retries += 1
                continue
                
            if response.status_code != 200:
                print(f"Error {response.status_code} en {url}")
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extracción de datos
            data = {}
            
            # Nombre del producto
            name_tag = soup.find('h2', class_='h4 product-title text-center text-sm-left mb-2')
            data['Nombre'] = name_tag.text.strip() if name_tag else 'N/A'
            
            # Características
            features = {}
            features_div = soup.find('div', class_='mb-2 ml-n1 text-center text-sm-left')
            if features_div:
                for span in features_div.find_all('span', class_='font-size badge badge-info m-1'):
                    text = span.get_text(strip=True).split(':', 1)
                    if len(text) == 2:
                        features[text[0].strip()] = text[1].strip()
            data['Características'] = features or 'N/A'
            
            # Descripción
            desc_tag = soup.find('p', class_='mb-2')
            data['Descripción'] = desc_tag.text.strip() if desc_tag else 'N/A'
            
            # Imagen
            img_tag = soup.find('img', class_='rounded-lg float-sm-right d-block mx-auto')
            if img_tag and 'src' in img_tag.attrs:
                data['Imagen'] = img_tag['src']
            else:
                data['Imagen'] = 'N/A'
            
            # Precios
            prices = {}
            price_table = soup.find('div', class_='table-responsive')
            if price_table:
                product_links = price_table.find_all('p', class_='font-size-xs m-0')
                for product_link in product_links:
                    text = product_link.get_text(strip=True)
                    lines = text.splitlines()
                    for line in lines:
                        parts = line.split()
                        unidades = None
                        
                        # Buscar monedas
                        for i, part in enumerate(parts):
                            monedas = ["$", "€", "£"]
                            
                            if part.isdigit():  # Si es número, probablemente sean unidades
                                unidades = int(part)

                            # Asignar precio nuevo
                            if "nuevo" in part.lower() and unidades is not None:
                                if "€" in line:  # Priorizar euros
                                    prices["Nuevo Precio"] = parts[i - 1]
                                    prices["Nuevo Unidades"] = unidades
                                    unidades = None  # Reiniciar para evitar mezclar unidades con otras líneas

                            # Asignar precio utilizado
                            elif "utilizado" in part.lower() and unidades is not None:
                                if "€" in line:  # Priorizar euros
                                    prices["Utilizado Precio"] = parts[i - 1]
                                    prices["Utilizado Unidades"] = unidades
                                    unidades = None  # Reiniciar para evitar mezclar unidades con otras líneas

            data['Precios'] = prices or 'N/A'
            
            return data
            
        except Exception as e:
            print(f"Error al procesar {url}: {str(e)}")
            retries += 1
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    print(f"Falló después de {MAX_RETRIES} intentos: {url}")
    return None


def process_category(category):
    """Procesa todos los enlaces de una categoría"""
    input_path = f"links_procesados/unique_{category}_links.csv"
    output_path = f"{output_dir}/{category}_productos.csv"
    
    try:
        df = pd.read_csv(input_path)
        links = df["Unique Product Links"].tolist()
        
        # Crear lista para almacenar datos
        products_data = []
        
        for i, link in enumerate(links, 1):
            print(f"Procesando {category} {i}/{len(links)}: {link}")
            product_data = scrape_product(link)
            if product_data:
                products_data.append({
                    'URL': link,
                    'Nombre': product_data['Nombre'],
                    'Características': str(product_data['Características']),
                    'Descripción': product_data['Descripción'],
                    'Imagen': product_data['Imagen'],
                    'Precios': str(product_data['Precios'])
                })
                time.sleep(DELAY_BETWEEN_REQUESTS)  # Esperar entre solicitudes
            
            # Guardar datos cada 10 productos o al final
            if i % 10 == 0 or i == len(links):
                pd.DataFrame(products_data).to_csv(output_path, index=False, mode='a', header=not os.path.exists(output_path))
                products_data = []  # Reiniciar buffer
        
        print(f"Datos guardados en {output_path}")
        
    except Exception as e:
        print(f"Error procesando categoría {category}: {str(e)}")


if __name__ == "__main__":
    categories = [
        "processor",
        "case",
        "cooler",
        "graphic-card",
        "memory",
        "motherboard",
        "power-supply",
        "storage"
    ]
    
    for category in categories:
        print(f"\n=== Procesando categoría: {category} ===")
        process_category(category)