import requests
from bs4 import BeautifulSoup
from typing import Any, Dict, List
import json
from pymongo import MongoClient

base_url = "https://bva.cargotrack.net/default.asp"
#este codigo no esta terminado por falta de datos en la pagina de cargo track


def login(user: str, password: str, session: requests.Session) -> None:
    data = {"user": user, "password": password, "Submit": "Log In", "action": "login"}
    session.post(
        url=base_url, data=data, headers=headers, allow_redirects=True
    )


def extract_accounts_data(session: requests.Session) -> Dict[str, Any]:
    accounts_url = "https://bva.cargotrack.net/appl2.0/agent/accounts.asp"
    response = session.get(accounts_url)
    data: List[Dict[str, Any]] = []
    if response.status_code == 200:
        # ? Use bs4
        soup: BeautifulSoup = BeautifulSoup(response.content, "lxml")
        table = soup.select("div#search")[0].find_next_sibling("table")

        columns = ["Número", "Empresa", "Teléfono", "Móvil", "Email"]
        rows = table.find_all("tr")
        for row_number, row in enumerate(rows, start=0):
            row_data = {}
            # ? Ignore first row (header)
            if row_number == 0:
                continue
            # ? Extract data from all td elements
            columns_tds = row.find_all("td")
            for name, value in zip(columns, columns_tds):
                row_data[name] = value.text.strip()
            data.append(row_data)
    else:
        print(f"Error al acceder a la página, código de estado: {response.status_code}")
    return data

def extract_invoice_data(session: requests.Session) -> List[Dict[str, Any]]:
    accounts_url = "https://bva.cargotrack.net/appl2.0/agent/invoices.asp"
    response = session.get(accounts_url)
    data: List[Dict[str, Any]] = []
    
    if response.status_code == 200:
        # Usamos BeautifulSoup para analizar el contenido HTML
        soup: BeautifulSoup = BeautifulSoup(response.content, 'html.parser')
        table = soup.select("div#search")[0].find_next_sibling("table")

        # Columnas de la tabla
        columns = ["Fecha", "Numero", "cuenta", "Cantidad", "Pagado"]
        rows = table.find_all("tr")

        for row_number, row in enumerate(rows, start=0):
            row_data = {}
            # Ignoramos la primera fila (que es el encabezado)
            if row_number == 0:
                continue

            # Extraemos todos los elementos td de la fila
            columns_tds = row.find_all("td")
            
            # Aseguramos que haya suficientes celdas
            if len(columns_tds) >= 6:
                # Extraemos datos básicos
                row_data["Fecha"] = columns_tds[0].text.strip()
                row_data["Numero"] = columns_tds[1].text.strip()
                row_data["cuenta"] = columns_tds[2].text.strip()

                # Combinamos el valor de la moneda y la cantidad
                moneda = columns_tds[3].text.strip()  # Ejemplo: USD
                monto = columns_tds[4].text.strip()   # Ejemplo: 29.00
                row_data["Cantidad"] = f"{moneda} {monto}"

                # Extraemos el valor de "Pagado"
                pagado = columns_tds[5].text.strip()  # Ejemplo: 0 o 29.00
                row_data["Pagado"] = pagado
            
            # Añadimos los datos extraídos a la lista
            data.append(row_data)
    else:
        print(f"Error al acceder a la página, código de estado: {response.status_code}")
    
    return data

def extract_store_data(session: requests.Session) -> List[Dict[str, Any]]:
    accounts_url = "https://bva.cargotrack.net/appl2.0/agent/whs.asp"
    response = session.get(accounts_url)
    data: List[Dict[str, Any]] = []
    
    if response.status_code == 200:
        # Usamos BeautifulSoup para analizar el contenido HTML
        soup: BeautifulSoup = BeautifulSoup(response.content, 'html.parser')
        table = soup.select("div#search")[0].find_next_sibling("table").find_next_sibling("table")

         # Columnas de la tabla
        columns = ["Estatus", "Dest", "Almacen", "Fecha", "Remitente", "Destinatario", "Bultos Peso", "Volumen", "Valor"]
        rows = table.find_all("tr")

        for row_number, row in enumerate(rows, start=0):
            row_data = {}
            # Ignoramos la primera fila (que es el encabezado)
            if row_number == 0:
                continue

            # Extraemos todos los elementos td de la fila
            columns_tds = row.find_all("td")
            
            # Aseguramos que haya suficientes celdas
            if len(columns_tds) >= 12:
               # Extraemos solo el texto dentro de cada <td>, ignorando imágenes u otros elementos
                row_data["Estatus"] = columns_tds[1].get_text(strip=True)  # strip=True elimina espacios en blanco
                row_data["Dest"] = columns_tds[3].get_text(strip=True)
                row_data["Almacen"] = columns_tds[4].get_text(strip=True)
                row_data["Fecha"] = columns_tds[5].get_text(strip=True)

                row_data["Remitente"] = columns_tds[6].get_text(strip=True)
                row_data["Destinatario"] = columns_tds[7].get_text(strip=True)
                row_data["Bultos"] = columns_tds[8].get_text(strip=True)

                row_data["Peso"] = columns_tds[9].get_text(strip=True)
                row_data["Volumen"] = columns_tds[10].get_text(strip=True)
                row_data["Valor"] = columns_tds[11].get_text(strip=True)
                 # Añadimos los datos extraídos a la lista
            data.append(row_data)
    else:
        print(f"Error al acceder a la página, código de estado: {response.status_code}")
    
    return data

def extract_shipping_data(session: requests.Session) -> Dict[str, Any]:
    accounts_url = "https://bva.cargotrack.net/appl2.0/agent/default.asp"
    response = session.get(accounts_url)
    data: List[Dict[str, Any]] = []
    if response.status_code == 200:
        # ? Use bs4
        soup: BeautifulSoup = BeautifulSoup(response.content, "lxml")
        table = soup.select("div#search")[0].find_next_sibling("table")

        columns = ["Número", "Empresa", "Teléfono", "Móvil", "Email"]
        rows = table.find_all("tr")
        for row_number, row in enumerate(rows, start=0):
            row_data = {}
            # ? Ignore first row (header)
            if row_number == 0:
                continue
            # ? Extract data from all td elements
            columns_tds = row.find_all("td")
            for name, value in zip(columns, columns_tds):
                row_data[name] = value.text.strip()
            data.append(row_data)
    else:
        print(f"Error al acceder a la página, código de estado: {response.status_code}")
    return data

def save_data_to_mongodb(collection_name: str, data: List[Dict[str, Any]]) -> None:
    # Conectarse a MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    
    # Seleccionamos la base de datos 
    db = client["cargo_track_data"]
    
    # Seleccionamos la colección en la que queremos insertar los datos
    collection = db[collection_name]
    
    # Insertamos los datos
    if data:
        collection.insert_many(data)
        print(f"{len(data)} documentos insertados en la colección {collection_name}")
    else:
        print(f"No hay datos para insertar en la colección {collection_name}")


if __name__ == "__main__":
    user: str = "VE30940"
    password: str = "f16cargo"
    session = requests.Session()

    # Configuramos las cabeceras iniciales
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Origin": "https://bva.cargotrack.net",
    }
    session.headers.update(headers)

    # Hacemos la solicitud inicial para obtener las cookies
    home_response = session.get(base_url)
    cookie_value = f"user={user};{home_response.headers['Set-Cookie']}"
    session.headers.update({"cookie": cookie_value})

    # Iniciamos sesión
    login(user, password, session)

    print("Logged IN.")
    accounts_data = extract_accounts_data(session)
    invoice_data = extract_invoice_data(session)
    store_data = extract_store_data(session)
    shipping_data = extract_shipping_data(session)
    print(accounts_data)
    print(invoice_data)
    print(store_data)

    save_data_to_mongodb("accounts", accounts_data)
    save_data_to_mongodb("invoices", invoice_data)
    save_data_to_mongodb("stores", store_data)
  
