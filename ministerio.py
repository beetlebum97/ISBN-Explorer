import csv
import json
import os
import re
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configuración Selenium
options = Options()
options.headless = True
service = Service(executable_path=r"C:\Users\knock\Programas\geckodriver-v0.36.0-win64\geckodriver.exe")

# Mapeo de roles
ROL_MAP = {
    "tr.": "traductor",
    "pr.": "prologuista",
    "il.": "ilustrador",
    "ed.": "editor",
    "ed. lit.": "editor literario",
    "co.": "coordinador",
    "comp.": "compilador"
}

def limpiar_autores_td(td):
    autores = []
    for span in td.find_all("span"):
        for a in span.find_all("a"):
            a.decompose()
        texto = span.get_text(strip=True)
        texto = re.sub(r"\s+", " ", texto)

        rol = "autor"
        for clave, valor in ROL_MAP.items():
            if re.search(rf";\s*{re.escape(clave)}", texto):
                rol = valor
                texto = re.sub(rf";\s*{re.escape(clave)}", "", texto).strip()

        fechas = ""
        match = re.search(r"\(([^)]+)\)", texto)
        if match:
            fechas = match.group(1)
            texto = re.sub(r"\s*\([^)]+\)", "", texto)

        autores.append({
            "nombre": texto,
            "fechas": fechas,
            "rol": rol
        })
    return autores

def extraer_ficha(driver, url, isbn):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//table"))
    )
    soup = BeautifulSoup(driver.page_source, "html.parser")

    datos = {
        "isbn": isbn,
        "fuente": {
            "origen": "Ministerio de Cultura - Base de datos de libros editados en España",
            "tipo": "detalle"
        }
    }

    for fila in soup.find_all("tr"):
        th = fila.find("th", {"scope": "row"})
        td = fila.find("td")
        if th and td:
            campo = th.get_text(strip=True).lower()
            if "autor" in campo:
                datos["autores"] = limpiar_autores_td(td)
            elif "materia" in campo:
                datos["materias"] = [span.get_text(strip=True) for span in td.find_all("span")]
            else:
                valor = td.get_text(" ", strip=True).replace("[Ver títulos]", "").strip()
                campo = campo.replace(" ", "_").replace(":", "")
                datos[campo] = valor
    return datos

def buscar_isbn(driver, isbn):
    driver.get("https://www.cultura.gob.es/webISBN/tituloSimpleFilter.do?cache=init&prev_layout=busquedaisbn&layout=busquedaisbn&language=es")
    campo_isbn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "params.cisbnExt"))
    )
    campo_isbn.clear()
    campo_isbn.send_keys(isbn)
    driver.find_element(By.XPATH, "//input[@value='Buscar']").click()

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "formularios"))
    )
    soup = BeautifulSoup(driver.page_source, "html.parser")
    enlaces = soup.select("a[href*='tituloDetalle.do']")

    if not enlaces:
        return None

    tomos = []
    for enlace in enlaces:
        href = enlace.get("href")
        texto = enlace.get_text().replace("-", "").strip()
        if not texto.startswith("978"):
            continue
        url = urljoin("https://www.cultura.gob.es", href)
        datos = extraer_ficha(driver, url, texto)
        tomos.append(datos)

    return {
        "isbn_consultado": isbn,
        "fuente": {
            "origen": "Ministerio de Cultura - Base de datos de libros editados en España",
            "tipo": "detalle"
        },
        "tomos": tomos
    }

def procesar_lote(csv_path):
    errores = []
    os.makedirs("fuentes/MC", exist_ok=True)

    # Solo se actualiza el bloque de lectura del CSV
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        driver = webdriver.Firefox(service=service, options=options)

        for idx, row in enumerate(reader, start=1):
            id_libro = row["ID"].strip()
            titulo = row["TÍTULO"].strip()
            isbn = row["ISBN"].replace("-", "").strip()

            print(f"Consultando MC para ISBN {isbn}")
            resultado = buscar_isbn(driver, isbn)

            if resultado:                         
                with open(f"fuentes/MC/MC_{id_libro}_{isbn}.json", "w", encoding="utf-8") as f:
                    json.dump(resultado, f, ensure_ascii=False, indent=2)
            else:
                errores.append(f"[ ID {id_libro} | ISBN {isbn} ]: {titulo} no encontrado en MC.")

        driver.quit()

    if errores:
        with open("fuentes/informe_MC.txt", "w", encoding="utf-8") as f:
            for linea in errores:
                f.write(linea + "\n")

    print("✅ Ministerio procesado. Revisa informe_MC.txt si hay ausencias.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, default="ISBNs.csv")
    args = parser.parse_args()
    procesar_lote(args.csv)
