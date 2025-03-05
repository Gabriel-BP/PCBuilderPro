import cloudscraper
from bs4 import BeautifulSoup
import sys
import time
import csv

# Configurar la codificación de salida para manejar caracteres UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def get_total_pages(scraper, base_url):
    """
    Obtiene el número total de páginas de la URL base con reintentos en caso de error 429.
    """
    retries = 3
    while retries > 0:
        response = scraper.get(base_url)
        
        if response.status_code == 429:
            print(f"Error 429: Demasiadas solicitudes al obtener el número total de páginas. Esperando 10 segundos antes de intentar nuevamente... ({retries} intentos restantes)")
            time.sleep(10)
            retries -= 1
            continue
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            pagination_element = soup.find('li', class_='page-item d-sm-none')
            if pagination_element:
                total_pages_text = pagination_element.find('span', class_='page-link-static').text.strip()
                _, total_pages = map(int, total_pages_text.split('/'))
                return total_pages
            else:
                print("No se encontró el elemento de paginación.")
                return 1  # Asumir una sola página si no se encuentra el elemento
        
        print(f"Error al obtener el número total de páginas: {response.status_code}")
        break
    
    print("No se pudo determinar el número total de páginas. Asumiendo una sola página.")
    return 1  # Asumir una sola página si hay un error persistente

def scrape_page(scraper, page_url):
    """
    Extrae los enlaces de productos de una página específica.
    """
    retries = 3
    while retries > 0:
        response = scraper.get(page_url)
        
        if response.status_code == 429:
            print(f"Error 429: Demasiadas solicitudes. Esperando 10 segundos antes de intentar nuevamente... ({retries} intentos restantes)")
            time.sleep(10)
            retries -= 1
            continue
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            product_links = soup.find_all('a', href=lambda href: href and href.startswith('/es/parts/'))
            return [f"https://pc-builds.com{link['href']}" for link in product_links]
        
        print(f"Error al procesar la página: {response.status_code}")
        break
    
    return []

def save_to_csv(category, product_links):
    """
    Guarda los enlaces de productos en un archivo CSV.
    """
    filename = f"links/{category}_links.csv"
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Product Link"])  # Escribir encabezado
        for link in product_links:
            writer.writerow([link])
    print(f"Enlaces guardados en '{filename}'.")

def scrape_product_links(scraper, base_url):
    """
    Extrae todos los enlaces de productos de todas las páginas de una categoría.
    """
    total_pages = get_total_pages(scraper, base_url)
    all_product_links = []
    failed_pages = []
    
    for page in range(1, total_pages + 1):
        print(f"Procesando página {page} de {total_pages}...")
        # Construir la URL correctamente
        page_url = f"{base_url.rstrip('/')}/{page}?countryCode=ES"
        product_links = scrape_page(scraper, page_url)
        
        if product_links:
            all_product_links.extend(product_links)
        else:
            failed_pages.append(page)
        
        time.sleep(5)  # Retraso entre solicitudes para evitar errores 429
    
    return all_product_links, failed_pages

def main():
    """
    Función principal que ejecuta el scraping para varias categorías.
    """
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
    
    base_url_template = "https://pc-builds.com/es/parts/{}/"
    scraper = cloudscraper.create_scraper()
    
    for category in categories:
        print(f"\n=== Procesando categoría: {category} ===")
        base_url = base_url_template.format(category)
        product_links, failed_pages = scrape_product_links(scraper, base_url)
        
        # Guardar los enlaces en un archivo CSV
        save_to_csv(category, product_links)
        
        if failed_pages:
            print(f"No se pudieron procesar las siguientes páginas en la categoría '{category}': {failed_pages}")

if __name__ == "__main__":
    main()