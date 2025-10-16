import csv
import requests
import json
import os
import argparse

API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
URL_BASE = "https://www.googleapis.com/books/v1/volumes"

def consultar_google_books(isbn):
    params = {
        "q": f"isbn:{isbn}",
        "key": API_KEY
    }
    response = requests.get(URL_BASE, params=params)
    if response.status_code != 200:
        return None

    data = response.json()
    if "items" not in data:
        return None

    info = data["items"][0]["volumeInfo"]
    return {
        "isbn": isbn,
        "titulo": info.get("title"),
        "autores": info.get("authors", []),
        "editorial": info.get("publisher"),
        "fecha_publicacion": info.get("publishedDate"),
        "descripcion": info.get("description"),
        "categorias": info.get("categories", []),
        "portada": info.get("imageLinks", {}).get("thumbnail"),
        "fuente": {
            "origen": "Google Books API",
            "tipo": "enriquecimiento"
        },
        "estado": "completo" if info.get("title") and info.get("authors") else "parcial"
    }

def procesar_lote(csv_path):
    errores = []
    os.makedirs("fuentes/googlebooks", exist_ok=True)

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for idx, row in enumerate(reader, start=1):
            id_libro = row["ID"].strip()
            titulo = row["TÍTULO"].strip()
            isbn = row["ISBN"].replace("-", "").strip()

            print(f"Consultando Google Books para ISBN {isbn}")
            resultado = consultar_google_books(isbn)

            if resultado:
                with open(f"fuentes/googlebooks/GB_{id_libro}_{isbn}.json", "w", encoding="utf-8") as f:
                    json.dump(resultado, f, ensure_ascii=False, indent=2)
            else:
                errores.append(f"[ ID {id_libro} | ISBN {isbn} ]: {titulo} no encontrado en Google Books.")

    if errores:
        with open("fuentes/informe_googlebooks.txt", "w", encoding="utf-8") as f:
            for linea in errores:
                f.write(linea + "\n")

    print("✅ Google Books procesado. Revisa informe_googlebooks.txt si hay ausencias.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, default="ISBNs.csv")
    args = parser.parse_args()
    procesar_lote(args.csv)