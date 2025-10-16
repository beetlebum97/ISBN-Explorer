import sys
import os
import json
from datetime import datetime
import random

FICHAS_DIR = "fichas"
FUENTES_DIR = "fuentes"

def generar_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    aleatorio = random.randint(100, 999)
    return f"AUTO_{timestamp}_{aleatorio}"

def fusionar(id_libro, titulo, isbn):
    isbn = isbn.replace("-", "").strip()
    ficha = {
        "id": id_libro,
        "titulo_solicitado": titulo,
        "isbn_solicitado": isbn,
        "fuentes_consultadas": [],
    }

    fuentes = {
        "MC": f"{FUENTES_DIR}/MC/MC_{id_libro}_{isbn}.json",
        "googlebooks": f"{FUENTES_DIR}/googlebooks/GB_{id_libro}_{isbn}.json",
        "openlibrary": f"{FUENTES_DIR}/openlibrary/OL_{id_libro}_{isbn}.json"
    }

    for clave, ruta in fuentes.items():
        if os.path.exists(ruta):
            with open(ruta, encoding="utf-8") as f:
                datos = json.load(f)
                ficha["fuentes_consultadas"].append(datos.get("fuente", clave))
                for k, v in datos.items():
                    if k not in ficha and k != "fuente":
                        ficha[k] = v

    if len(ficha["fuentes_consultadas"]) == 0:
        return None

    os.makedirs(FICHAS_DIR, exist_ok=True)
    salida = os.path.join(FICHAS_DIR, f"ficha_{id_libro}_{isbn}.json")
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(ficha, f, ensure_ascii=False, indent=2)
    return salida

if __name__ == "__main__":
    if len(sys.argv) == 4:
        _, id_libro, titulo, isbn = sys.argv
        id_libro = id_libro.strip() or generar_id()
    else:
        print("❌ Entrada inválida. Usa: python fusiones_fichas.py ID TÍTULO ISBN")
        sys.exit(1)

    resultado = fusionar(id_libro.strip(), titulo.strip(), isbn.strip())
    if resultado:
        print(f"✅ Ficha generada: {resultado}")
    else:
        print(f"❌ No se pudo generar ficha para ISBN {isbn.strip()}")
