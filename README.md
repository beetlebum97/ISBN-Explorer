# ?? ISBN Explorer

**ISBN Explorer** es una herramienta modular para consultar, fusionar y auditar fichas bibliogr芍ficas a partir de un archivo CSV. Permite interactuar con m迆ltiples fuentes externas (Ministerio de Cultura, Google Books, OpenLibrary), generar fichas individuales, consolidarlas en un 迆nico archivo y auditar el estado de la colecci車n.

> ?? Este repositorio incluye fichas de ejemplo en `fichas/` y `fuentes/` para facilitar pruebas y exploraci車n.  
> Si deseas comenzar desde cero, ejecuta `python isbn_explorer.py --reset` tras clonar el proyecto.

---
## ?? Video Demostraci車n

### ?? Ejecuci車n Completa (Flujo Full)
[![ISBN Explorer - Ejecuci車n Completa](https://raw.githubusercontent.com/beetlebum97/ISBN-Explorer/refs/heads/master/screenshoots/01.Selenium-scraping.png)](https://youtu.be/AyHgzzkEl84)
- **00:00** - [Presentaci車n y estructura del proyecto](https://youtu.be/AyHgzzkEl84?t=0)
- **00:50** - [Ejecuci車n fuente: Ministerio de Cultura (Selenium)](https://youtu.be/AyHgzzkEl84?t=50)
- **03:40** - [Ejecuci車n fuente: Google Books (API)](https://youtu.be/AyHgzzkEl84?t=220)
- **07:22** - [Ejecuci車n fuente: OpenLibrary (API)](https://youtu.be/AyHgzzkEl84?t=442)
- **09:32** - [Fusi車n de metadatos](https://youtu.be/AyHgzzkEl84?t=572)
- **11:00** - [Auditor赤a y resultados finales](https://youtu.be/AyHgzzkEl84?t=660)

### ?? Modos de Operaci車n y Opciones
[![ISBN Explorer - Modos de Operaci車n](https://raw.githubusercontent.com/beetlebum97/ISBN-Explorer/refs/heads/master/screenshoots/07.Fuente-ID-2.png)](https://youtu.be/Uq7RjzAM13Y)
- **00:00** - [Limpieza: Borrado de archivos (--reset)](https://youtu.be/Uq7RjzAM13Y?t=0)
- **01:35** - [Uso de --fuente para consultas individuales con rangos --id](https://youtu.be/Uq7RjzAM13Y?t=95)
- **05:45** - [Fusi車n de fichas individuales](https://youtu.be/Uq7RjzAM13Y?t=345)
- **07:35** - [Consolidaci車n. Archivo JSON con todos los datos](https://youtu.be/Uq7RjzAM13Y?t=455)
- **08:30** - [Auditor赤a y estado del sistema](https://youtu.be/Uq7RjzAM13Y?t=510)

---
## ??? Tecnolog赤as Utilizadas

| Categor赤a | Tecnolog赤as |
|-----------|-------------|
| **Lenguaje** | Python 3.10+ |
| **APIs** | Google Books API, OpenLibrary API |
| **Web Scraping** | Selenium, BeautifulSoup |
| **Procesamiento** | JSON, CSV, Manipulaci車n de datos |
| **Utilidades** | Colorama, python-dotenv, argparse |
---

## ?? Caracter赤sticas Principales

- **?? Consulta m迆ltiples fuentes** (Ministerio de Cultura, Google Books, OpenLibrary)
- **?? Fusi車n inteligente** de metadatos desde diferentes or赤genes
- **?? Auditor赤a autom芍tica** de fichas faltantes o incompletas
- **?? Consolidaci車n en JSON** para f芍cil procesamiento posterior
- **??? Modular y extensible** para agregar nuevas fuentes f芍cilmente
- **?? Procesamiento por lotes** con control de rango y bloques
---

## ?? Requisitos

- Python 3.10+
- Clave API de Google Books (a?adir en `.env` como `GOOGLE_BOOKS_API_KEY=<CLAVE>` o introducir interactivamente al iniciar script)
- Archivo `biblioteca.csv` con columnas: `ID`, `T赤TULO`, `ISBN`
- **Selenium** instalado (`pip install selenium`)
- **Geckodriver** instalado y accesible en el PATH (para Firefox)

### ?? Instalaci車n de Geckodriver

1. Descarga desde: [https://github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases)
2. Extrae el ejecutable y col車calo en una carpeta incluida en tu `PATH`
   - Ejemplo: `C:\Program Files\Geckodriver\`
3. Verifica con:

```bash
geckodriver --version
```
4. En la l赤nea 18 de ministerio.py indica el PATH de geckodriver
```
# Configuraci車n Selenium
options = Options()
options.headless = True
service = Service(executable_path=r"C:\Users\knock\Programas\geckodriver-v0.36.0-win64\geckodriver.exe")
```
---

## ??? Estructura

```
ISBN-Explorer/
念岸岸 isbn_explorer.py           # Script maestro
念岸岸 ministerio.py              # Fuente: Ministerio de Cultura
念岸岸 googlebooks.py             # Fuente: Google Books
念岸岸 openlibrary.py             # Fuente: OpenLibrary
念岸岸 fusiones_fichas.py         # Fusi車n de fichas individuales
念岸岸 clave.py                   # Clave API de Google Books
念岸岸 biblioteca.csv             # Archivo principal con ID, T赤TULO, ISBN
念岸岸 fuentes/                   # Fichas individuales por fuente
岫   念岸岸 MC/
岫   念岸岸 googlebooks/
岫   弩岸岸 openlibrary/
念岸岸 fichas/                    # Fichas fusionadas y consolidadas
岫   念岸岸 ficha_ID_ISBN.json
岫   弩岸岸 fichas.json
念岸岸 logs/                      # Trazas de ejecuci車n
岫   弩岸岸 log_YYYYMMDD_HHMMSS_modo.txt
念岸岸 screenshoots/                  # Evidencias visuales para el README
```

---


## ?? Informaci車n esperada del CSV

El archivo `biblioteca.csv` debe contener las siguientes columnas:

| Columna | Descripci車n              |
|---------|--------------------------|
| `ID`    | N迆mero de registro       |
| `T赤TULO`| T赤tulo del libro         |
| `ISBN`  | C車digo ISBN              |

> Se recomienda mantener encabezados (columnas) en may迆sculas y sin espacios extra.

---

### ?? Edici車n del CSV

El archivo `biblioteca.csv` se utiliza como fuente principal de registros. Puedes editarlo manualmente o regenerarlo desde otras fuentes. El script maestro lo carga autom芍ticamente al iniciar cualquier flujo.

> ?? El archivo usado est芍 definido en la l赤nea 21 dentro de `isbn_explorer.py`.

```
CSV_DEFAULT = "biblioteca.csv"
```

---

## ?? Comandos disponibles

| Comando         | Descripci車n                                                                 |
|----------------|------------------------------------------------------------------------------|
| `--fuente`      | Ejecuta una fuente espec赤fica (`MC`, `googlebooks`, `openlibrary`)          |
| `--full`        | Ejecuta todas las fuentes sobre el CSV completo                             |
| `--fusionar`    | Fusiona fichas individuales en una ficha completa por libro                 |
| `--consolidar`  | Genera `fichas.json` con todas las fichas completas                         |
| `--estado`      | Muestra el estado actual del sistema (fichas por fuente, fusionadas, etc.)  |
| `--auditar`     | Detecta fichas faltantes por ID e ISBN                                      |
| `--reset`       | Borra todas las fichas, logs e informes                                     |

---

## ?? Ejecuci車n por rango

| Comando             | Resultado                                 |
|---------------------|-------------------------------------------|
| `--id 15`           | Solo la fila 15 del CSV                   |
| `--id 15 20`        | De la 15 a la 20 (ambas incluidas)        |
| Sin `--id`          | Procesa todo el CSV                       |

---

## ?? Ejemplos de uso

```bash
python isbn_explorer.py --full
python isbn_explorer.py --fuente openlibrary --id 83 100
python isbn_explorer.py --fusionar
python isbn_explorer.py --consolidar
python isbn_explorer.py --estado
python isbn_explorer.py --auditar
python isbn_explorer.py --reset
```

## ?? Ayuda del script

Puedes consultar la ayuda del script en cualquier momento con:

```bash
python isbn_explorer.py --help
```

Salida:

```
usage: isbn_explorer.py [-h] [--csv CSV] [--full] [--fuente {MC,googlebooks,openlibrary}]
                        [--id ID [ID ...]] [--fusionar] [--consolidar]
                        [--estado] [--auditar] [--reset]

ISBN Explorer

options:
  -h, --help            Muestra este mensaje de ayuda y termina
  --csv CSV             Archivo CSV. Por defecto: biblioteca.csv
  --full                Ejecuta todo el flujo completo
  --fuente {MC,googlebooks,openlibrary}
                        Ejecuta solo una fuente espec赤fica
  --id ID [ID ...]      Procesa un rango de filas del CSV (ej. --id 200 600) o una sola (ej. --id 30)
  --fusionar            Fusiona fichas individuales por libro
  --consolidar          Genera archivo fichas.json con todas las fichas completas
  --estado              Muestra el estado actual del sistema
  --auditar             Verifica qu谷 fichas completas faltan seg迆n el CSV
  --reset               Borra todas las fichas, logs e informes
```

## ?? Flujo completo (`--full`)

El comando --full ejecuta todo el flujo de procesamiento sobre el archivo CSV completo (biblioteca.csv), consultando todas las fuentes disponibles, generando fichas individuales por libro, fusionando los resultados y creando el archivo final fichas.json.

Admite par芍metro ID, por si no se quiere realizar el proceso sobre todas las filas del  fichero CSV.

### ?? Comando

Todas las filas:

```bash
python isbn_explorer.py --full
```

Solo fila con id 230:

```
python isbn_explorer.py --full --id 230
```

Primeras 200 filas:
```
python isbn_explorer.py --full --id 1 200
```

### ?? Qu谷 hace

- Procesa todas las filas del CSV
- Ejecuta las tres fuentes: `MC`, `googlebooks`, `openlibrary`
- Genera fichas individuales en `fuentes/` por fuente
- Guarda trazas en `logs/` con nombre tipo `log_YYYYMMDD_HHMMSS_full.txt`

### ?? Resultado esperado

```
fuentes/
念岸岸 MC/
岫   念岸岸 ficha_001_9781234567890.json
岫   弩岸岸 ...
念岸岸 googlebooks/
岫   念岸岸 ficha_001_9781234567890.json
岫   弩岸岸 ...
念岸岸 openlibrary/
岫   念岸岸 ficha_001_9781234567890.json
岫   弩岸岸 ...
logs/
念岸岸 log_20251015_2124_full.txt
```

---

### ?? Consideraciones

- Si una fuente falla o no responde, se registra en el log
- El tiempo de ejecuci車n puede variar seg迆n el tama?o del CSV y la respuesta de las APIs
- Realiza la fusi車n y consolidaci車n autom芍tica: ambas opciones se pueden ejecutar aisladamente con las opciones `--fusionar` y `--consolidar`

### ?? Flujo interno del comando `--full`

| Paso | Acci車n                                                                 |
|------|------------------------------------------------------------------------|
| 1??   | Carga el archivo `biblioteca.csv`                                      |
| 2??   | Ejecuta todas las fuentes (`MC`, `googlebooks`, `openlibrary`)         |
| 3??   | Genera fichas individuales por fuente en `fuentes/`                    |
| 4??   | Fusiona fichas por libro (`fusiones_fichas.py`)                        |
| 5??   | Genera fichas completas en `fichas/`                                   |
| 6??   | Consolida todas las fichas en un 迆nico archivo `fichas.json`           |
| 7??   | Guarda trazas completas en `logs/log_YYYYMMDD_HHMMSS_full.txt`         |
| 8??   | Muestra resumen final en consola con colores y s赤mbolos narrativos     |

---

### ?? Ejemplo de uso 

```
E:\ISBN_Explorer>python isbn_explorer.py --full

?? [MC] Bloque 1 (100 ISBNs)

?? Ejecutando fuente: MC
Consultando MC para ISBN 9788467903317
Consultando MC para ISBN 9788467904680
Consultando MC para ISBN 9788499470115
...
Consultando MC para ISBN 9788483577189
Consultando MC para ISBN 9788433920997
? Ministerio procesado. Revisa informe_MC.txt si hay ausencias.
?? Eliminados 1 archivos temporales
```

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/ISBN-Explorer/refs/heads/master/screenshoots/1_selenium_full.jpg)

```
?? [googlebooks] Bloque 1 (100 ISBNs)

?? Ejecutando fuente: googlebooks
Consultando Google Books para ISBN 9788467903317
Consultando Google Books para ISBN 9788467904680
Consultando Google Books para ISBN 9788499470115
...
Consultando Google Books para ISBN 9788483577189
Consultando Google Books para ISBN 9788433920997
? Google Books procesado. Revisa informe_googlebooks.txt si hay ausencias.
?? Eliminados 1 archivos temporales
```

```
?? Ejecutando fuente: openlibrary
Consultando OpenLibrary para ISBN 9788467903317
Consultando OpenLibrary para ISBN 9788467904680
Consultando OpenLibrary para ISBN 9788499470115
...
Consultando OpenLibrary para ISBN 9788449344251
Consultando OpenLibrary para ISBN 9788433920997
? OpenLibrary procesado. Revisa informe_openlibrary.txt si hay ausencias.
?? Eliminados 1 archivos temporales
```

FUSI車N

```
?? Fusionando fichas completas...
↙ Generando ficha: 001 | Sin City Integral Vol. 1 | 9788467903317
   ? Fuentes disponibles: MC, googlebooks, openlibrary
↙ Generando ficha: 002 | Sin City Integral Vol. 2 | 9788467904680
   ? Fuentes disponibles: MC, googlebooks, openlibrary
↙ Generando ficha: 003 | Frank Cappa Integral | 9788499470115
   ? Fuentes disponibles: MC, googlebooks
↙ Generando ficha: 004 | Alex Magnum | 9788483577189
   ? Fuentes disponibles: MC, googlebooks
↙ Generando ficha: 005 | On赤rica | 9788499470931
   ? Fuentes disponibles: MC, googlebooks
↙ Generando ficha: 006 | Maus | 9788439720713
   ? Fuentes disponibles: MC, googlebooks, openlibrary
↙ Generando ficha: 007 | Pers谷polis | 9788498470666
   ? Fuentes disponibles: MC, googlebooks, openlibrary
↙ Generando ficha: 008 | Shenzhen | 9788493508807
   ? Fuentes disponibles: MC, googlebooks, openlibrary
↙ Generando ficha: 009 | Pyongyang | 9788496815056
   ? Fuentes disponibles: MC, googlebooks, openlibrary
↙ Generando ficha: 010 | Ranx | 9788478338931
   ? Fuentes disponibles: MC, googlebooks, openlibrary
```

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/ISBN-Explorer/refs/heads/master/screenshoots/04.Fusionar-fichas.png)

```
↙ Generando ficha: 469 | Los archivos personales de Stanley Kubrick | 9783836556859
   ? Fuentes disponibles: googlebooks, openlibrary
↙ Generando ficha: 470 | Moonfire. El viaje 谷pico del Apollo 11 | 9783836571166
   ? Fuentes disponibles: googlebooks, openlibrary
↙ Generando ficha: 471 | Los 芍ngeles del Infierno. Una extra?a y terrible saga | 9788433975867
   ? Fuentes disponibles: MC, googlebooks, openlibrary
↙ Generando ficha: 472 | La metamorfosis y otros relatos de animales | 9788467043648
   ? Fuentes disponibles: googlebooks, openlibrary
↙ Generando ficha: 473 | El hombre y sus s赤mbolos | 9788449344251
   ? Fuentes disponibles: ninguna
↙ Generando ficha: 474 | Mujeres | 9788433920997
   ? Fuentes disponibles: MC, googlebooks, openlibrary
? Fichas fusionadas: 458
?? 16 fichas no se generaron por falta de datos

?? Consolidado 458 registros en fichas.json

?? Validando fichas faltantes...
?? Faltan 16 fichas completas:
  ID 031 ↙ ?Dr芍cula, Dracul, Vlad? ?Bah...! | 84-95834-96-3
  ID 041 ↙ El hombre que r赤e | 84-86450-92-6
  ID 133 ↙ Light & Bold | 987-84-8357-807-0
  ID 148 ↙ La vida en vi?etas: Historias autobiogr芍ficas | 978-84-9814-950
  ID 153 ↙ Seis | 978-84-965587-86-1
  ID 164 ↙ Negative Burn 2 | 84-96402-94-0
  ID 228 ↙ Predicador V | 978-84-18475-63-4
  ID 251 ↙ Los mejores 13 episodios de Golgo 13 Vol.1 | 978-84-9947-772-5
  ID 252 ↙ Los mejores 13 episodios de Golgo 13 Vol.2 | 978-84-9947-773-5
  ID 284 ↙ Vans Of The Wall. A european skateboard movie | 978-1-907875-00-7
  ID 292 ↙ Batman: El regreso del caballero oscuro | 978-84-17509-85-9
  ID 303 ↙ Cyberpunk 207: La Gu赤a Oficial Completa (Edici車n coleccionista) | 978-1-911015-86-4
  ID 315 ↙ Blur: 3862 days. The Official History | 0-735-0287-9
  ID 450 ↙ Blur. The complete quiz book | 979-83-011-3141-7
  ID 452 ↙ Hombre vol. 2 | 978-84-10330-35-1
  ID 473 ↙ El hombre y sus s赤mbolos | 978-84-493-4425-1
```


- Captura de consola con trazas por fuente
- Fragmento del log generado
- Vista de la carpeta `fuentes/` con fichas por fuente


---

## ?? `--estado`: Diagn車stico actual del sistema

Esta opci車n imprime un resumen del estado del entorno de trabajo, 迆til para verificar el progreso antes de ejecutar acciones como `--fusionar`, `--consolidar` o `--validar`.

Incluye:

- ?? N迆mero de fichas individuales detectadas por fuente (`MC`, `googlebooks`, `openlibrary`)
- ?? Total de fichas fusionadas (si existen en `fichas_fusionadas.json`)
- ?? Total de registros consolidados en `fichas.json` (si existe)

#### Ejemplo de uso

```
E:\ISBN_Explorer>python isbn_explorer.py --estado

?? Estado actual del sistema:
  MC: 362 fichas individuales
  googlebooks: 404 fichas individuales
  openlibrary: 167 fichas individuales

?? Fichas fusionadas: 458
?? fichas.json contiene 458 registros consolidados
```

```
E:\ISBN_Explorer>python isbn_explorer.py --estado

?? Estado actual del sistema:
  MC: 362 fichas individuales
  googlebooks: 44 fichas individuales
  openlibrary: 1 fichas individuales
?? Fichas fusionadas: 0
?? fichas.json a迆n no ha sido generado

```

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/ISBN-Explorer/refs/heads/master/screenshoots/03.Estado.png)

---

## ?? `--fuente`: Exploraci車n individual por origen

Esta opci車n permite ejecutar una fuente espec赤fica (`MC`, `googlebooks`, `openlibrary`) de forma aislada, sin pasar por el flujo completo de fusi車n o consolidaci車n. Es ideal para validar respuestas, regenerar fichas o depurar comportamientos fuente por fuente.

### Comportamiento

- ?? Procesa todos los registros del CSV activo (`biblioteca.csv` o los que se definan mediante opci車n --id)
- ??? Genera fichas individuales en `fuentes/<fuente>/`
- ?? No fusiona ni consolida autom芍ticamente
- ?? 迆til para pruebas, calibraci車n y depuraci車n modular

### Ejemplos de uso

Procesar todos los registros desde Ministerio Cultura:

```
python isbn_explorer.py --fuente MC
```

Procesar los primeros 50 registros desde Google Books:

```
python isbn_explorer.py --fuente googlebooks --id 1 50
```

Procesar el registro 222 desde OpenLibrary:

```
python isbn_explorer.py --fuente openlibrary --id 222
```
```
E:\ISBN_Explorer>python isbn_explorer.py --fuente openlibrary --id 222
?? [openlibrary] Bloque 1 (1 ISBNs)
?? Ejecutando fuente: openlibrary
Consultando OpenLibrary para ISBN 9788418475313
? OpenLibrary procesado. Revisa informe_openlibrary.txt si hay ausencias.
```
![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/ISBN-Explorer/refs/heads/master/screenshoots/4_fuente_id.jpg)

---

## ?? `--fusionar`: Integraci車n de fichas desde m迆ltiples fuentes

Esta opci車n permite fusionar las respuestas obtenidas desde distintas fuentes (`MC`, `googlebooks`, `openlibrary`) en una 迆nica ficha consolidada por registro. Es el paso clave para construir un corpus enriquecido, comparativo y trazable.

### Comportamiento

- ?? Recorre todos los registros del CSV activo (`biblioteca.csv` o el definido)
- ?? Busca fichas individuales en `fuentes/<fuente>/` para cada registro
- ?? Aplica l車gica de fusi車n: prioriza, compara y sintetiza respuestas
- ?? Genera fichas consolidadas en `fichas/`, una por registro
- ?? No elimina las fichas fuente: permite auditor赤a y trazabilidad

#### Ejemplo de uso

```
python isbn_explorer.py --fusionar
```

```
?? Fusionando respuestas para 120 registros...
?? Ficha generada: fichas/00042.json
?? Ficha generada: fichas/00043.json
...
? Fusi車n completada: 120 fichas consolidadas
```

---

## ?? `--consolidar`: Revisi車n y depuraci車n de fichas consolidadas

Esta opci車n permite inspeccionar, validar y depurar las fichas generadas tras la fusi車n. Recorre el directorio `fichas/` y aplica l車gica de consolidaci車n, correcci車n o enriquecimiento seg迆n el estado de cada ficha. Es 迆til para asegurar consistencia, detectar errores y preparar el corpus final.

### Comportamiento

- ?? Recorre todas las fichas en `fichas/`
- ?? Aplica l車gica de revisi車n: corrige campos, normaliza estructuras, detecta incoherencias
- ?? Puede regenerar campos faltantes, limpiar duplicados o aplicar reglas de formato
- ?? Deja trazas claras de cada ficha procesada, incluyendo cambios aplicados
- ?? No elimina fichas: respeta el corpus existente y lo mejora

### Ejemplo de uso

```
python isbn_explorer.py --consolidar
```
```
E:\ISBN_Explorer>python isbn_explorer.py --consolidar
? 10 fichas consolidadas guardadas en orden en fichas/fichas.json
?? Primer ID: 300 〞 迆ltimo ID: 310

E:\ISBN_Explorer>python isbn_explorer.py --estado

?? Estado actual del sistema:
  MC: 9 fichas individuales
  googlebooks: 10 fichas individuales
  openlibrary: 8 fichas individuales
```
![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/ISBN-Explorer/refs/heads/master/screenshoots/5_consolidar.jpg)

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/ISBN-Explorer/refs/heads/master/screenshoots/6_consolidar.jpg)

---

### ?? `--reset`: Limpieza del entorno de trabajo

Esta opci車n elimina todos los archivos generados durante el flujo, dejando solo los archivos permanentes. Es 迆til para reiniciar el entorno antes de una nueva ejecuci車n completa.

#### Acciones realizadas

- ?? Elimina todos los archivos `.json` dentro de `fichas/`
- ?? Elimina todos los archivos dentro de `fuentes/`
- ?? Elimina todos los archivos dentro de `logs/`

#### Ejemplo de uso

```
python isbn_explorer.py --reset
```
```
E:\ISBN_Explorer>python isbn_explorer.py --reset
?? Ejecutando limpieza total de archivos...
?? Fichas eliminadas: 458
?? Logs eliminados: 12
?? Informes eliminados: 0
? Limpieza completa.
```
![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/ISBN-Explorer/refs/heads/master/screenshoots/05.Reset.png)

---
## ?? Pr車ximas Mejoras

- **Base de datos NoSQL** para almacenamiento escalable
- **Interfaz web** con Flask/FastAPI
- **Dashboard** para visualizaci車n de resultados
- **Nuevas fuentes** (Amazon, GoodReads, etc.)
- **Despliegue en cloud**

---
## ?? Autor

**David V芍zquez Rodr赤guez**  
?? Madrid, Espa?a  
?? [LinkedIn](https://www.linkedin.com/in/dvazrod)  
?? [GitHub](https://github.com/beetlebum97)
---




