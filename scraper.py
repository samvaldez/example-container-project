print("Iniciando scraper...")
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from azure.storage.filedatalake import DataLakeServiceClient
from io import BytesIO
import os

# Configurar Selenium para entorno headless
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.binary_location = "/usr/bin/chromium"
driver = webdriver.Chrome(options=options)

# Diccionario con nombre de archivo y URL
urls = {
    "ttf_prices": "https://www.cmegroup.com/markets/energy/natural-gas/dutch-ttf-natural-gas-usd-mmbtu-icis-heren-front-month.settlements.html",
    "henryhub_prices": "https://www.cmegroup.com/markets/energy/natural-gas/nymex-natural-gas-settlements.html",
    "brent_prices": "https://www.cmegroup.com/markets/energy/crude-oil/brent-crude-oil.quotes.html",
    "wti_prices": "https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html#tradeDate=06%2F04%2F2025",
    "coal_prices": "https://www.cmegroup.com/markets/energy/coal/coal-api-2-cif-ara-argus-mccloskey.settlements.html",
    "gulfcoast_ulsd_prices": "https://www.cmegroup.com/markets/energy/coal/coal-api-2-cif-ara-argus-mccloskey.settlements.html",
    "gulfcoast_hsfo_prices": "https://www.cmegroup.com/markets/energy/refined-products/gulf-coast-no-6-fuel-oil-30pct-sulfur-platts-swap.settlements.html",
}

# Conexión al Data Lake
conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
print("Obtuve la cadena de conexión.")
file_system_name = "raw"
directory_name = "commodities"

service_client = DataLakeServiceClient.from_connection_string(conn_str)
file_system = service_client.get_file_system_client(file_system_name)
directory = file_system.get_directory_client(directory_name)
try:
    directory.create_directory()
    print("Directorio creado.")
except:
    print("Directorio ya existía.")

# Recorrer cada URL
for name, url in urls.items():
    try:
        print(f"Procesando: {url}")
        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.market-table"))
        )
        print("Tabla localizada.")

        html = driver.find_element(By.CSS_SELECTOR, "table.market-table").get_attribute("outerHTML")
        df = pd.read_html(html)[0]
        print(f"Tabla cargada con {len(df)} filas.")

        if df.empty:
            print(f"La tabla en {name} está vacía.")
            continue

        # Guardar a Parquet en memoria
        buffer = BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)

        # Subir a Data Lake
        file_name = f"{name}.parquet"
        file_client = directory.create_file(file_name)
        file_client.append_data(data=buffer.read(), offset=0, length=buffer.tell())
        file_client.flush_data(buffer.tell())

        print(f"{file_name} guardado exitosamente.")
        
    except Exception as e:
        print(f"Error procesando {name}: {e}")

driver.quit()
print("Scraper finalizado.")
