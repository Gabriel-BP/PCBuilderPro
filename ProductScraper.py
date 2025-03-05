import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup

# Leer el primer enlace de procesadores procesado
df = pd.read_csv("links_procesados/unique_processor_links.csv")
sample_url = df["Unique Product Links"].iloc[0]  # Tomamos el primer enlace de ejemplo

# Configurar el scraper
scraper = cloudscraper.create_scraper()

# Obtener el HTML
print(f"Obteniendo HTML de: {sample_url}")
response = scraper.get(sample_url)

# Buscar el nombre del producto
soup = BeautifulSoup(response.text, "html.parser")
product_name = soup.find("h2", class_="h4 product-title text-center text-sm-left mb-2").text.strip()
print(f"Nombre del producto: {product_name}")

# Obtener características
features_div = soup.find("div", class_="mb-2 ml-n1 text-center text-sm-left")
features_dict = {}
if features_div:
    spans = features_div.find_all("span", class_="font-size badge badge-info m-1")
    for span in spans:
        text = span.get_text(strip=True)
        if ":" in text:
            key, value = map(str.strip, text.split(":", 1))
            features_dict[key] = value

# Obtener descripciones
description_div = soup.find_all("p", class_="mb-2")

# Obtener foto:
img = soup.find("img", class_="rounded-lg float-sm-right d-block mx-auto")

# Obtener precio
# Obtener precios nuevos y usados
prices_dict = {}
price_table = soup.find("div", class_="table-responsive")
if price_table:
    product_links = price_table.find_all("p", class_="font-size-xs m-0")
    for product_link in product_links:
        text = product_link.get_text(strip=True)
        if "nuevo" in text.lower():
            new_price = text.split("nuevo de")[-1].split("$")[0].strip()
            prices_dict["Precio Nuevo"] = f"{new_price} $"
        if "utilizado" in text.lower():
            used_price = text.split("utilizado desde")[-1].split("$")[0].strip()
            prices_dict["Precio Usado"] = f"{used_price} $"

