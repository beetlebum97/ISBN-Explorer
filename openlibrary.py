import csv
import requests
import json
import os
import argparse

URL_BASE = "https://openlibrary.org/api/books"

def consultar_openlibrary(isbn):
    params = {
        "bibkeys": f"ISBN:{isbn}",
        "format": "json",
        "jscmd": "data"
    }
    response = requests.get(URL_BASE, params=params)
    if response.status_code != 200:
        return None

    data = response.json()
    clave = f"ISBN:{isbn}"
    if clave not in data:
        return None

    info = data[clave]
    return {
        "isbn": isbn,
        "titulo": info.get("title"),
        "autores": [{"nombre": a.get("name"), "rol": "autor"} for a in info.get("authors", [])],
        "editorial": info.get("publishers", [{}])[0].get("name"),
        "fecha_publicacion": info.get("publish_date"),
        "numero_paginas": info.get("number_of_pages"),
        "portada": info.get("cover", {}).get("medium"),
        "categorias": [s.get("name") for s in info.get("subjects", [])],
        "fuente": {
            "origen": "OpenLibrary API",
            "tipo": "enriquecimiento"
        },
        "estado": "completo" if info.get("title") and info.get("authors") else "parcial"
    }

def procesar_lote(csv_path):
    errores = []
    os.makedirs("fuentes/openlibrary", exist_ok=True)

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for idx, row in enumerate(reader, start=1):
            id_libro = row["ID"].strip()
            titulo = row["TÍTULO"].strip()
            isbn = row["ISBN"].replace("-", "").strip()

            print(f"Consultando OpenLibrary para ISBN {isbn}")
            resultado = consultar_openlibrary(isbn)

            if resultado:
                with open(f"fuentes/openlibrary/OL_{id_libro}_{isbn}.json", "w", encoding="utf-8") as f:
                    json.dump(resultado, f, ensure_ascii=False, indent=2)
            else:
                errores.append(f"[ ID {id_libro} | ISBN {isbn} ]: {titulo} no encontrado en OpenLibrary.")

    if errores:
        with open("fuentes/informe_openlibrary.txt", "w", encoding="utf-8") as f:
            for linea in errores:
                f.write(linea + "\n")

    print("✅ OpenLibrary procesado. Revisa informe_openlibrary.txt si hay ausencias.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, default="ISBNs.csv")
    args = parser.parse_args()
    procesar_lote(args.csv)
