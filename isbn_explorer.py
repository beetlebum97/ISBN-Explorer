# 🧩 Parte 1: Encabezado y funciones auxiliares

import argparse
import csv
import os
import subprocess
import json
import chardet
import sys
import re
import shutil
from colorama import init, Fore
from dotenv import load_dotenv
from datetime import datetime  # Añade este import si no lo tienes ya

load_dotenv()
init(autoreset=True)

FUENTES_DIR = "fuentes"
FICHAS_DIR = "fichas"
CSV_DEFAULT = "biblioteca.csv"
TAMAÑO_BLOQUE = 100  # Bloque fijo para --full

def cargar_clave_api():
    clave = os.getenv("GOOGLE_BOOKS_API_KEY")
    if not clave:
        clave = input("🔑 Introduce tu clave API de Google Books: ").strip()
        os.environ["GOOGLE_BOOKS_API_KEY"] = clave
    return clave

def contar_fichas_existentes():
    fichas = [f for f in os.listdir(FICHAS_DIR) if f.startswith("ficha_") and f.endswith(".json")]
    return len(fichas)

def cargar_csv(ruta_csv, límite=None):
    with open(ruta_csv, 'rb') as f:
        raw = f.read(10000)
        encoding = chardet.detect(raw)['encoding']
    with open(ruta_csv, encoding=encoding) as f:
        sample = f.read(1024)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sample)
        reader = csv.DictReader(f, dialect=dialect)
        filas = list(reader)
    return filas[:límite] if límite else filas

def dividir_en_bloques(filas, tamaño):
    for i in range(0, len(filas), tamaño):
        yield filas[i:i + tamaño]
        
ANSI_ESCAPE = re.compile(r'\x1B[0-?]*[ -/]*[@-~]')

class DualWriter:
    def __init__(self, file):
        self.terminal = sys.__stdout__
        self.logfile = file

    def write(self, message):
        self.terminal.write(message)
        clean = ANSI_ESCAPE.sub('', message)
        self.logfile.write(clean)

    def flush(self):
        self.terminal.flush()
        self.logfile.flush()

def redirigir_salida_a_log(modo="ejecucion"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_log = f"log_{timestamp}_{modo}.txt"
    LOGS_DIR = "logs"
    os.makedirs(LOGS_DIR, exist_ok=True)
    ruta_log = os.path.join(LOGS_DIR, nombre_log)

    log_file = open(ruta_log, "w", encoding="utf-8")
    sys.stdout = DualWriter(log_file)
    sys.stderr = sys.stdout
    
# 🧩 Parte 2: Procesamiento, fusión y consolidación

def procesar_fuente(nombre_script, fuente, ruta_csv):
    print(Fore.CYAN + f"\n🔍 Ejecutando fuente: {fuente}")
    subprocess.run(["python", nombre_script, "--csv", ruta_csv], timeout=900)

def fusionar_fichas(filas, offset=0):
    errores = []
    fusionados = 0

    def verificar_fuentes_disponibles(id_libro, isbn):
        isbn = isbn.replace("-", "").strip()
        rutas = {
            "MC": f"fuentes/MC/MC_{id_libro}_{isbn}.json",
            "googlebooks": f"fuentes/googlebooks/GB_{id_libro}_{isbn}.json",
            "openlibrary": f"fuentes/openlibrary/OL_{id_libro}_{isbn}.json"
        }
        disponibles = []
        for fuente, ruta in rutas.items():
            if os.path.exists(ruta):
                disponibles.append(fuente)
        return disponibles

    for idx, row in enumerate(filas, start=offset + 1):
        id_libro = row.get("ID", f"{idx:03d}").strip()
        titulo = row.get("TÍTULO", "").strip()
        isbn = row.get("ISBN", "").replace("-", "").strip()

        print(Fore.YELLOW + f"→ Generando ficha: {id_libro} | {titulo} | {isbn}")
        fuentes = verificar_fuentes_disponibles(id_libro, isbn)
        print(Fore.CYAN + f"   ↳ Fuentes disponibles: {', '.join(fuentes) if fuentes else 'ninguna'}")

        try:
            resultado = subprocess.run(
                ["python", "fusiones_fichas.py", id_libro, titulo, isbn],
                capture_output=True,
                text=True,
                timeout=30
            )

            ficha_path = os.path.join(FICHAS_DIR, f"ficha_{id_libro}_{isbn}.json")
            if os.path.exists(ficha_path):
                with open(ficha_path, encoding="utf-8") as f:
                    contenido = json.load(f)
                    if contenido.get("fuentes_consultadas"):
                        contenido["id"] = id_libro
                        with open(ficha_path, "w", encoding="utf-8") as fw:
                            json.dump(contenido, fw, ensure_ascii=False, indent=2)
                        fusionados += 1
                    else:
                        os.remove(ficha_path)
                        errores.append((id_libro, titulo, isbn))
            else:
                errores.append((id_libro, titulo, isbn))

        except Exception as e:
            errores.append((id_libro, titulo, isbn))
            print(Fore.RED + f"⚠️ Error al fusionar {id_libro}: {e}")

    return fusionados, errores

def consolidar_fichas():
    fichas_completas = {}

    # Cargar fichas individuales desde la carpeta 'fichas/'
    for archivo in os.listdir("fichas/"):
        if archivo.startswith("ficha_") and archivo.endswith(".json"):
            ruta = os.path.join("fichas", archivo)
            with open(ruta, "r", encoding="utf-8") as f:
                ficha = json.load(f)
                id = extraer_id(ficha)
                if id:
                    fichas_completas[id] = ficha

    # Ordenar por ID numérico antes de guardar
    fichas_ordenadas = dict(sorted(fichas_completas.items(), key=lambda x: int(x[0])))

    with open("fichas/fichas.json", "w", encoding="utf-8") as f:
        json.dump(fichas_ordenadas, f, indent=2, ensure_ascii=False)

    if fichas_ordenadas:
        primer_id = next(iter(fichas_ordenadas))
        ultimo_id = next(reversed(fichas_ordenadas))
        print(f"✅ {len(fichas_ordenadas)} fichas consolidadas guardadas en orden en fichas/fichas.json")
        print(f"🔢 Primer ID: {primer_id} — Último ID: {ultimo_id}")
    else:
        print("⚠️ No se consolidó ninguna ficha. Verifica que la carpeta 'fichas/' contiene archivos válidos.")


def extraer_id(ficha):
    # Intenta varias variantes del campo ID
    for clave in ["ID", "id", "Id"]:
        if clave in ficha:
            return ficha[clave]
    return None


# 🧩 Parte 3: Diagnóstico, limpieza y estado

def limpiar_temporales():
    eliminados = 0
    for archivo in os.listdir():
        if archivo.startswith("temp_") and archivo.endswith(".csv"):
            os.remove(archivo)
            eliminados += 1
    if eliminados:
        print(Fore.MAGENTA + f"\n🧹 Eliminados {eliminados} archivos temporales")
        
def validar_fichas_faltantes(filas):
    # Cargar fichas consolidadas si existen
    ruta_consolidado = os.path.join(FICHAS_DIR, "fichas.json")
    fichas_consolidadas = set()
    if os.path.exists(ruta_consolidado):
        with open(ruta_consolidado, encoding="utf-8") as f:
            datos = json.load(f)
            fichas_consolidadas = set(datos.keys())
            
    faltantes = []
    for row in filas:
        id_libro = row["ID"].strip()
        isbn_raw = row["ISBN"].strip()
        isbn = isbn_raw.replace("-", "")

        # Verificar contra fichas.json si está disponible
        if fichas_consolidadas:
            if id_libro not in fichas_consolidadas:
                faltantes.append((id_libro, row["TÍTULO"], isbn_raw))
        else:
            ficha_path = os.path.join(FICHAS_DIR, f"ficha_{id_libro}_{isbn}.json")
            if not os.path.exists(ficha_path):
                faltantes.append((id_libro, row["TÍTULO"], isbn_raw))

    print(Fore.CYAN + "\n🔎 Validando fichas faltantes...")
    if faltantes:
        print(Fore.RED + f"⚠️ Faltan {len(faltantes)} fichas completas:")
        for id_libro, titulo, isbn in faltantes:
            print(f"  ID {id_libro} → {titulo} | {isbn}")
    else:
        print(Fore.GREEN + "✅ Todas las fichas están completas.")

    
def mostrar_estado(filas_csv):
    fuentes = ["MC", "googlebooks", "openlibrary"]
    print(Fore.CYAN + "\n📊 Estado actual del sistema:")

    for fuente in fuentes:
        carpeta = os.path.join(FUENTES_DIR, fuente)
        if os.path.exists(carpeta):
            archivos = [f for f in os.listdir(carpeta) if f.endswith(".json")]
            print(Fore.YELLOW + f"  {fuente}: {len(archivos)} fichas individuales")
        else:
            print(Fore.YELLOW + f"  {fuente}: (sin carpeta)")

    total_fichas = contar_fichas_existentes()
    print(Fore.GREEN + f"\n📦 Fichas fusionadas: {total_fichas}")

    consolidado = os.path.join(FICHAS_DIR, "fichas.json")
    if os.path.exists(consolidado):
        with open(consolidado, encoding="utf-8") as f:
            try:
                datos = json.load(f)
                print(Fore.GREEN + f"📚 fichas.json contiene {len(datos)} registros consolidados")
            except Exception:
                print(Fore.RED + "⚠️ Error al leer fichas.json")
    else:
        print(Fore.YELLOW + "ℹ️ fichas.json aún no ha sido generado")

import os
import sys
import shutil
from colorama import Fore

def resetear_todo():
    print(Fore.RED + "\n⚠️ Ejecutando limpieza total de archivos...")

    # Borrar fichas completas en fichas/
    FICHAS_DIR = "fichas"
    if os.path.exists(FICHAS_DIR):
        fichas = [f for f in os.listdir(FICHAS_DIR) if f.endswith(".json")]
        for f in fichas:
            os.remove(os.path.join(FICHAS_DIR, f))
        print(Fore.YELLOW + f"🧹 Fichas eliminadas: {len(fichas)}")

    # Borrar archivos dentro de fuentes/, incluyendo fichas en subdirectorios protegidos
    FUENTES_DIR = "fuentes"
    protegidos = {"MC", "googlebooks", "openlibrary"}
    eliminados_fuentes = 0

    if os.path.exists(FUENTES_DIR):
        for f in os.listdir(FUENTES_DIR):
            ruta = os.path.join(FUENTES_DIR, f)
            if os.path.isfile(ruta):
                os.remove(ruta)
                eliminados_fuentes += 1
            elif os.path.isdir(ruta):
                if f in protegidos:
                    # Eliminar fichas dentro del subdirectorio protegido
                    fichas = [x for x in os.listdir(ruta) if x.endswith(".json")]
                    for ficha in fichas:
                        os.remove(os.path.join(ruta, ficha))
                        eliminados_fuentes += 1
                else:
                    # Eliminar subdirectorios no protegidos
                    shutil.rmtree(ruta)
                    eliminados_fuentes += 1

        print(Fore.YELLOW + f"🧹 Archivos eliminados en fuentes/: {eliminados_fuentes}")
        print(Fore.CYAN + f"📁 Subdirectorios conservados: {', '.join(sorted(protegidos))}")

    # Borrar logs, excluyendo el archivo en uso
    LOGS_DIR = "logs"
    log_actual = None
    if hasattr(sys.stdout, "logfile") and hasattr(sys.stdout.logfile, "name"):
        log_actual = os.path.basename(sys.stdout.logfile.name)

    if os.path.exists(LOGS_DIR):
        logs = [f for f in os.listdir(LOGS_DIR) if f != log_actual]
        for f in logs:
            os.remove(os.path.join(LOGS_DIR, f))
        print(Fore.YELLOW + f"🧹 Logs eliminados: {len(logs)}")
        if log_actual:
            print(Fore.CYAN + f"📄 Log actual conservado: {log_actual}")

    print(Fore.GREEN + "\n✅ Limpieza completa.")


# 🧩 Parte 4: Bloque principal main()

def main():
    parser = argparse.ArgumentParser(description="ISBN Explorer")
    parser.add_argument("--csv", type=str, default=CSV_DEFAULT, help="Archivo CSV. Por defecto: biblioteca.csv")
    parser.add_argument("--full", action="store_true", help="Ejecutar todo el flujo completo")
    parser.add_argument("--fuente", type=str, choices=["MC", "googlebooks", "openlibrary"], help="Ejecutar solo una fuente")
    parser.add_argument("--id", nargs="+", type=int, help="Procesar un rango de CSV (ej. --id 200 600) o un único ID (ej. --id 30)")
    parser.add_argument("--fusionar", action="store_true", help="Fusionar fichas individuales")
    parser.add_argument("--consolidar", action="store_true", help="Generar archivo fichas.json")
    parser.add_argument("--estado", action="store_true", help="Mostrar estado actual")
    parser.add_argument("--auditar", action="store_true", help="Verifica qué fichas completas faltan según el CSV")
    parser.add_argument("--reset", action="store_true", help="Borra todas las fichas, logs e informes")

    args = parser.parse_args()
    filas = cargar_csv(args.csv)

    # 🧩 Determinar rango de ejecución

    if args.id:
        inicio = args.id[0] - 1
        fin = args.id[1] - 1 if len(args.id) > 1 else args.id[0] - 1
    else:
        inicio = 0
        fin = len(filas) - 1

    bloques = [filas[inicio:fin + 1]]



    # 🧩 Determinar modo para nombrar el log
    modo = "full" if args.full else (
        f"fuente_{args.fuente}_id_{inicio}_{fin}" if args.fuente else (
            "fusionar" if args.fusionar else (
                "consolidar" if args.consolidar else (
                    "auditar" if args.auditar else (
                        "estado" if args.estado else "ejecucion"
                    )
                )
            )
        )
    )
    redirigir_salida_a_log(modo)

    if args.estado:
        mostrar_estado(filas)
        exit()

    if args.auditar:
        validar_fichas_faltantes(filas)
        exit()

    os.makedirs(FICHAS_DIR, exist_ok=True)
    for carpeta in [f"{FUENTES_DIR}/googlebooks", f"{FUENTES_DIR}/openlibrary", f"{FUENTES_DIR}/MC"]:
        os.makedirs(carpeta, exist_ok=True)

    script_map = {
        "MC": "ministerio.py",
        "googlebooks": "googlebooks.py",
        "openlibrary": "openlibrary.py"
    }

    if args.full:
        for fuente in ["MC", "googlebooks", "openlibrary"]:
            for i, bloque in enumerate(dividir_en_bloques(bloques[0], TAMAÑO_BLOQUE), start=1):
                print(Fore.CYAN + f"\n📦 [{fuente}] Bloque {i} ({len(bloque)} ISBNs)")
                temp_csv = f"temp_{fuente}_bloque_{i}.csv"
                with open(temp_csv, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["ID", "TÍTULO", "ISBN"], delimiter=";")
                    writer.writeheader()
                    writer.writerows(bloque)

                if fuente == "googlebooks":
                    clave_api = cargar_clave_api()

                procesar_fuente(script_map[fuente], fuente, temp_csv)
                limpiar_temporales()

        print(Fore.CYAN + "\n🔗 Fusionando fichas completas...")
        fusionados, errores = fusionar_fichas(filas)
        print(Fore.GREEN + f"✅ Fichas fusionadas: {fusionados}")
        if errores:
            print(Fore.RED + f"⚠️ {len(errores)} fichas no se generaron por falta de datos")

        consolidar_fichas()
        validar_fichas_faltantes(filas)
        limpiar_temporales()
        exit()

    if args.fuente:
        for i, bloque in enumerate(dividir_en_bloques(bloques[0], TAMAÑO_BLOQUE), start=1):
            print(Fore.CYAN + f"\n📦 [{args.fuente}] Bloque {i} ({len(bloque)} ISBNs)")
            temp_csv = f"temp_{args.fuente}_bloque_{i}.csv"
            with open(temp_csv, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["ID", "TÍTULO", "ISBN"], delimiter=";")
                writer.writeheader()
                writer.writerows(bloque)

            if args.fuente == "googlebooks":
                clave_api = cargar_clave_api()

            procesar_fuente(script_map[args.fuente], args.fuente, temp_csv)
            limpiar_temporales()
        exit()

    if args.fusionar:
        fusionar_fichas(filas, contar_fichas_existentes())
        validar_fichas_faltantes(filas)
        exit()

    if args.consolidar:
        consolidar_fichas()
        validar_fichas_faltantes(filas)
        exit()
        
    if args.reset:
        resetear_todo()
        exit()

    # Ayuda por defecto si no se pasa ningún argumento
    print(Fore.CYAN + "\n📚 Bienvenido a ISBN Explorer")
    print(Fore.YELLOW + "Este script permite consultar fuentes bibliográficas, fusionar fichas y consolidar resultados.")
    print(Fore.GREEN + "\nModos disponibles:")
    print(Fore.GREEN + "  --full                 Ejecuta todo el flujo completo")
    print(Fore.GREEN + "  --fuente [MC|...]      Ejecuta solo una fuente")
    print(Fore.GREEN + "  --id [inicio] [fin]    Procesa un rango del CSV")
    print(Fore.GREEN + "  --fusionar             Fusiona fichas individuales")
    print(Fore.GREEN + "  --consolidar           Genera archivo fichas.json")
    print(Fore.GREEN + "  --estado               Muestra estado actual")
    print(Fore.GREEN + "  --auditar              Verifica qué fichas completas faltan según el CSV")
    print(Fore.MAGENTA + "\nEjemplos:")
    print(Fore.MAGENTA + "  python isbn_explorer.py --fuente MC --id 0 500")
    print(Fore.MAGENTA + "  python isbn_explorer.py --full --id 0 1000")
    print(Fore.MAGENTA + "  python isbn_explorer.py --fusionar")
    print(Fore.MAGENTA + "  python isbn_explorer.py --consolidar")
    print(Fore.MAGENTA + "  python isbn_explorer.py --auditar\n")

if __name__ == "__main__":
    main()
