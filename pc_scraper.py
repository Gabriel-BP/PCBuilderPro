import cloudscraper
from bs4 import BeautifulSoup
import sys
import time

# Configurar la codificación de salida para manejar caracteres UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# URL base de la página
base_url = "https://pc-builds.com/es/parts/processor/"

# Crear una instancia de CloudScraper
scraper = cloudscraper.create_scraper()

# Realizar la solicitud GET a la primera página para obtener el número total de páginas
response = scraper.get(base_url)

if response.status_code == 200:
    print("Solicitud exitosa!")
    
    # Analizar el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Encontrar el elemento que contiene el número total de páginas
    pagination_element = soup.find('li', class_='page-item d-sm-none')
    if pagination_element:
        total_pages_text = pagination_element.find('span', class_='page-link-static').text.strip()
        current_page, total_pages = map(int, total_pages_text.split('/'))
        print(f"Total de páginas: {total_pages}")
    else:
        print("No se encontró el elemento de paginación.")
        total_pages = 1  # Asumir una sola página si no se encuentra el elemento
    
    # Lista para almacenar todos los enlaces de productos
    all_product_links = []
    failed_pages = []  # Para registrar páginas que fallen
    
    # Iterar a través de todas las páginas
    for page in range(1, total_pages + 1):
        retries = 3  # Número máximo de reintentos para errores 429
        while retries > 0:
            print(f"Procesando página {page} de {total_pages}...")
            
            # Construir la URL de la página actual
            page_url = f"{base_url}?page={page}?countryCode=ES"
            
            # Realizar la solicitud GET a la página actual
            page_response = scraper.get(page_url)
            
            # Manejar errores HTTP
            if page_response.status_code == 429:
                print(f"Error 429: Demasiadas solicitudes. Esperando 10 segundos antes de intentar nuevamente... ({retries} intentos restantes)")
                time.sleep(10)  # Esperar 10 segundos antes de intentar nuevamente
                retries -= 1
                continue  # Volver al inicio del bucle para reintentar
            
            if page_response.status_code == 200:
                # Analizar el contenido HTML de la página actual
                page_soup = BeautifulSoup(page_response.content, "html.parser")
                
                # Encontrar todos los enlaces de productos en la página actual
                product_links = page_soup.find_all('a', href=lambda href: href and href.startswith('/es/parts/processor/'))
                
                # Agregar los enlaces completos a la lista
                for link in product_links:
                    full_url = f"https://pc-builds.com{link['href']}"
                    all_product_links.append(full_url)
                
                # Salir del bucle de reintentos si la solicitud fue exitosa
                break
            else:
                print(f"Error al procesar la página {page}: {page_response.status_code}")
                failed_pages.append(page)
                break
        
        # Agregar un retraso entre solicitudes para evitar el error 429
        time.sleep(5)  # Incrementar el tiempo de espera a 5 segundos
    
    # Imprimir todos los enlaces de productos encontrados
    print(f"Se encontraron {len(all_product_links)} enlaces de productos:")
    for link in all_product_links:
        print(link)
    
    # Imprimir páginas fallidas
    if failed_pages:
        print(f"No se pudieron procesar las siguientes páginas: {failed_pages}")

else:
    print(f"Error en la solicitud inicial: {response.status_code}")