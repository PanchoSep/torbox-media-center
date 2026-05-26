# Mejorar Estructura de Carpetas con Tracking - Plan de Implementación

> **Para Hermes:** Usa el skill subagent-driven-development para implementar este plan tarea por tarea.

**Objetivo:** Implementar una estructura de carpetas mejorada con clasificación por tipo y resolución, sistema de tracking de ubicaciones, y respeto a cambios manuales del usuario.

**Arquitectura:** 
- Estructura: `movies/{resolution}/`, `series/`, `music/`, `others/`
- Resoluciones en movies: `2160/`, `1080/`, `720/`, `480/`, `unknown/`
- Nombres de carpeta incluyen hash: `"Title (Year) [1080p BluRay] {hash}/"`
- Base de datos trackea ubicación actual de cada archivo
- Prioridad a cambios manuales del usuario
- Flag para resetear y reclasificar todo

**Ejemplo de estructura:**
```
torbox/
├── movies/
│   ├── 2160/
│   │   └── Inception (2010) [2160p BluRay] {abc123}/
│   │       └── Inception.2010.2160p.BluRay.x265.mkv
│   ├── 1080/
│   │   ├── The Matrix (1999) [1080p BluRay] {def456}/
│   │   │   └── The.Matrix.1999.1080p.BluRay.x264.mkv
│   │   └── The Matrix (1999) [1080p WEB-DL] {ghi789}/
│   │       └── The.Matrix.1999.1080p.WEB-DL.x264.mkv
│   ├── 720/
│   ├── 480/
│   └── unknown/
├── series/
│   └── Breaking Bad (2008) [1080p] {jkl012}/
│       └── Season 01/
│           └── Breaking.Bad.S01E01.1080p.WEB-DL.mkv
├── music/
└── others/
```

**Tech Stack:** 
- PTN (ya instalado)
- TinyDB (ya instalado para tracking)
- Python 3.6+

---

## Task 1: Agregar campos de tracking a la base de datos

**Objetivo:** Extender el esquema de base de datos para trackear ubicación y clasificación manual

**Archivos:**
- Modify: `functions/databaseFunctions.py`
- Read first: `functions/databaseFunctions.py`

**Step 1: Leer estructura actual de base de datos**

Run: `cat functions/databaseFunctions.py`

**Step 2: Agregar campos nuevos al insertData**

Modificar la función `insertData` para incluir:
- `current_category`: Categoría actual (movies, series, music, others)
- `current_resolution_folder`: Carpeta de resolución actual (2160, 1080, 720, 480, unknown, null)
- `manual_override`: Boolean indicando si usuario movió manualmente
- `last_seen_path`: Última ruta física detectada

**Step 3: Verificar sintaxis**

Run: `python3 -m py_compile functions/databaseFunctions.py`
Expected: Sin errores

**Step 4: Commit**

```bash
git add functions/databaseFunctions.py
git commit -m "feat: agregar campos de tracking a base de datos"
```

---

## Task 2: Crear módulo de clasificación y parsing

**Objetivo:** Crear módulo para clasificar archivos y extraer metadata con PTN

**Archivos:**
- Create: `functions/classificationFunctions.py`

**Step 1: Crear función de extracción de resolución**

```python
import PTN
import logging
import re
from typing import Dict, Optional, Tuple

def extract_resolution(filename: str, parsed_data: Dict = None) -> str:
    """
    Extrae la resolución del nombre de archivo.
    
    Args:
        filename: Nombre del archivo
        parsed_data: Datos ya parseados por PTN (opcional)
        
    Returns:
        Resolución: '2160', '1080', '720', '480', o 'unknown'
    """
    if parsed_data is None:
        parsed_data = PTN.parse(filename)
    
    resolution = parsed_data.get('resolution', '')
    
    # Mapear resoluciones conocidas
    if '2160' in resolution or '4K' in resolution or 'UHD' in resolution:
        return '2160'
    elif '1080' in resolution:
        return '1080'
    elif '720' in resolution:
        return '720'
    elif '480' in resolution or 'SD' in resolution:
        return '480'
    else:
        # Intentar extraer con regex del filename completo
        if re.search(r'2160p|4K|UHD', filename, re.IGNORECASE):
            return '2160'
        elif re.search(r'1080p', filename, re.IGNORECASE):
            return '1080'
        elif re.search(r'720p', filename, re.IGNORECASE):
            return '720'
        elif re.search(r'480p|SD', filename, re.IGNORECASE):
            return '480'
    
    return 'unknown'
```

**Step 2: Crear función de clasificación de tipo de media**

```python
def classify_media_type(parsed_data: Dict, mimetype: str = None) -> str:
    """
    Clasifica el tipo de media.
    
    Args:
        parsed_data: Datos parseados por PTN
        mimetype: MIME type del archivo
        
    Returns:
        Categoría: 'movies', 'series', 'music', o 'others'
    """
    # Si tiene temporada/episodio, es serie
    if parsed_data.get('season') or parsed_data.get('episode'):
        return 'series'
    
    # Si el mimetype indica audio, es música
    if mimetype and mimetype.startswith('audio/'):
        return 'music'
    
    # Si el mimetype indica video, probablemente es película
    if mimetype and mimetype.startswith('video/'):
        # Si no tiene indicadores de serie, es película
        return 'movies'
    
    # Default: others
    return 'others'
```

**Step 3: Verificar sintaxis**

Run: `python3 -m py_compile functions/classificationFunctions.py`
Expected: Sin errores

**Step 4: Commit**

```bash
git add functions/classificationFunctions.py
git commit -m "feat: crear módulo de clasificación de media"
```

---

## Task 3: Crear módulo de formateo de carpetas con hash

**Objetivo:** Crear funciones para formatear nombres de carpeta incluyendo hash de Torbox

**Archivos:**
- Create: `functions/folderNamingFunctions.py`

**Step 1: Crear función de formateo para películas**

```python
import logging
from typing import Dict, Optional

def format_movie_folder(title: str, year: int = None, resolution: str = None, 
                       quality: str = None, hash: str = None) -> str:
    """
    Formatea nombre de carpeta para película.
    
    Formato: "Title (Year) [Resolution Quality] {hash}"
    Ejemplo: "The Matrix (1999) [1080p BluRay] {abc123}"
    
    Args:
        title: Título de la película
        year: Año
        resolution: Resolución (1080p, 720p, etc.)
        quality: Calidad (BluRay, WEB-DL, etc.)
        hash: Hash del torrent de Torbox
        
    Returns:
        Nombre de carpeta formateado
    """
    from functions.mediaFunctions import cleanTitle
    
    parts = [title]
    
    if year:
        parts.append(f"({year})")
    
    # Metadata técnica
    tech_parts = []
    if resolution:
        tech_parts.append(resolution)
    if quality:
        tech_parts.append(quality)
    
    if tech_parts:
        parts.append(f"[{' '.join(tech_parts)}]")
    
    # Agregar hash al final
    if hash:
        # Tomar primeros 8 caracteres del hash
        short_hash = hash[:8] if len(hash) > 8 else hash
        parts.append(f"{{{short_hash}}}")
    
    folder_name = " ".join(parts)
    folder_name = cleanTitle(folder_name)
    
    return folder_name
```

**Step 2: Crear función de formateo para series**

```python
def format_series_folder(title: str, year: int = None, resolution: str = None,
                        hash: str = None) -> str:
    """
    Formatea nombre de carpeta para serie.
    
    Formato: "Title (Year) [Resolution] {hash}"
    Ejemplo: "Breaking Bad (2008) [1080p] {def456}"
    
    Args:
        title: Título de la serie
        year: Año
        resolution: Resolución
        hash: Hash del torrent de Torbox
        
    Returns:
        Nombre de carpeta formateado
    """
    from functions.mediaFunctions import cleanTitle
    
    parts = [title]
    
    if year:
        parts.append(f"({year})")
    
    if resolution:
        parts.append(f"[{resolution}]")
    
    if hash:
        short_hash = hash[:8] if len(hash) > 8 else hash
        parts.append(f"{{{short_hash}}}")
    
    folder_name = " ".join(parts)
    folder_name = cleanTitle(folder_name)
    
    return folder_name
```

**Step 3: Verificar sintaxis**

Run: `python3 -m py_compile functions/folderNamingFunctions.py`
Expected: Sin errores

**Step 4: Commit**

```bash
git add functions/folderNamingFunctions.py
git commit -m "feat: crear módulo de formateo de carpetas con hash"
```

---

## Task 4: Agregar variables de entorno

**Objetivo:** Agregar configuración para nueva estructura y flag de reset

**Archivos:**
- Modify: `library/app.py`
- Modify: `.env.example`

**Step 1: Agregar variables en library/app.py**

```python
# Nueva estructura de carpetas con clasificación
ENHANCED_FOLDER_STRUCTURE = os.getenv("ENHANCED_FOLDER_STRUCTURE", "false").lower() == "true"

# Reset y reclasificar todo ignorando cambios manuales
FORCE_RECLASSIFY = os.getenv("FORCE_RECLASSIFY", "false").lower() == "true"
```

**Step 2: Actualizar .env.example**

```bash
# ENHANCED_FOLDER_STRUCTURE - Habilita estructura mejorada de carpetas
# Estructura: movies/{resolution}/, series/, music/, others/
# Resoluciones: 2160/, 1080/, 720/, 480/, unknown/
# Nombres incluyen hash: "Title (Year) [1080p BluRay] {hash}/"
# Default: false
ENHANCED_FOLDER_STRUCTURE=false

# FORCE_RECLASSIFY - Fuerza reclasificación ignorando cambios manuales
# Útil para resetear toda la estructura
# Default: false
FORCE_RECLASSIFY=false
```

**Step 3: Commit**

```bash
git add library/app.py .env.example
git commit -m "feat: agregar variables ENHANCED_FOLDER_STRUCTURE y FORCE_RECLASSIFY"
```

---

## Task 5: Crear sistema de detección de cambios manuales

**Objetivo:** Detectar cuando usuario mueve carpetas manualmente

**Archivos:**
- Create: `functions/trackingFunctions.py`

**Step 1: Crear función de escaneo de ubicaciones actuales**

```python
import os
import glob
import logging
from typing import Dict, List, Optional
from library.filesystem import MOUNT_PATH

def scan_current_locations() -> Dict[str, Dict]:
    """
    Escanea el filesystem y retorna ubicaciones actuales de archivos .strm
    
    Returns:
        Dict con hash como key y info de ubicación como value
    """
    locations = {}
    
    # Buscar todos los .strm recursivamente
    strm_files = glob.glob(os.path.join(MOUNT_PATH, "**", "*.strm"), recursive=True)
    
    for strm_path in strm_files:
        # Extraer información de la ruta
        rel_path = os.path.relpath(strm_path, MOUNT_PATH)
        parts = rel_path.split(os.sep)
        
        if len(parts) < 2:
            continue
        
        category = parts[0]  # movies, series, music, others
        
        # Extraer hash del nombre de carpeta
        folder_name = parts[-2] if len(parts) > 1 else None
        hash_match = None
        if folder_name:
            import re
            match = re.search(r'\{([a-f0-9]+)\}', folder_name)
            if match:
                hash_match = match.group(1)
        
        if hash_match:
            resolution_folder = None
            if category == 'movies' and len(parts) >= 3:
                resolution_folder = parts[1]  # 2160, 1080, etc.
            
            locations[hash_match] = {
                'path': strm_path,
                'category': category,
                'resolution_folder': resolution_folder,
                'folder_name': folder_name,
            }
    
    return locations
```

**Step 2: Crear función de detección de cambios**

```python
def detect_manual_changes(db_data: List[Dict], current_locations: Dict) -> List[Dict]:
    """
    Detecta cambios manuales comparando DB con filesystem actual.
    
    Args:
        db_data: Lista de registros de la base de datos
        current_locations: Dict de ubicaciones actuales del filesystem
        
    Returns:
        Lista de registros que necesitan actualización
    """
    changes = []
    
    for record in db_data:
        hash = record.get('folder_hash', '')[:8]  # Primeros 8 chars
        
        if not hash:
            continue
        
        # Ubicación esperada según DB
        db_category = record.get('current_category', 'movies')
        db_resolution = record.get('current_resolution_folder')
        
        # Ubicación actual en filesystem
        current = current_locations.get(hash)
        
        if not current:
            # Archivo no encontrado, podría estar eliminado
            continue
        
        # Comparar ubicaciones
        if (current['category'] != db_category or 
            current['resolution_folder'] != db_resolution):
            
            logging.info(f"Cambio manual detectado para {hash}: "
                        f"{db_category}/{db_resolution} -> "
                        f"{current['category']}/{current['resolution_folder']}")
            
            changes.append({
                'record': record,
                'new_category': current['category'],
                'new_resolution': current['resolution_folder'],
                'manual_override': True,
            })
    
    return changes
```

**Step 3: Commit**

```bash
git add functions/trackingFunctions.py
git commit -m "feat: crear sistema de detección de cambios manuales"
```

---

## Task 6: Integrar en torboxFunctions.py

**Objetivo:** Modificar process_file y searchMetadata para usar nueva estructura

**Archivos:**
- Modify: `functions/torboxFunctions.py`

**Step 1: Agregar imports**

```python
from functions.classificationFunctions import extract_resolution, classify_media_type
from functions.folderNamingFunctions import format_movie_folder, format_series_folder
from library.app import ENHANCED_FOLDER_STRUCTURE, FORCE_RECLASSIFY
```

**Step 2: Modificar process_file para agregar clasificación**

En la función `process_file`, después de parsear con PTN (línea ~52), agregar:

```python
# Clasificar tipo de media y resolución
if ENHANCED_FOLDER_STRUCTURE:
    media_category = classify_media_type(title_data, file.get('mimetype'))
    resolution_folder = extract_resolution(file.get('short_name'), title_data)
    
    data['current_category'] = media_category
    data['current_resolution_folder'] = resolution_folder if media_category == 'movies' else None
    data['manual_override'] = False
```

**Step 3: Commit**

```bash
git add functions/torboxFunctions.py
git commit -m "feat: integrar clasificación en process_file"
```

---

## Task 7: Actualizar searchMetadata para nueva estructura

**Objetivo:** Generar metadata_rootfoldername con nuevo formato

**Archivos:**
- Modify: `functions/torboxFunctions.py:135-193`

**Step 1: Modificar generación de metadata_rootfoldername**

Reemplazar línea 183 con lógica condicional:

```python
# Generar nombre de carpeta raíz
if ENHANCED_FOLDER_STRUCTURE:
    if data.get("type") == "series" or data.get("type") == "anime":
        base_metadata["metadata_rootfoldername"] = format_series_folder(
            title=title,
            year=base_metadata['metadata_years'],
            resolution=title_data.get('resolution'),
            hash=hash
        )
    elif data.get("type") == "movie":
        base_metadata["metadata_rootfoldername"] = format_movie_folder(
            title=title,
            year=base_metadata['metadata_years'],
            resolution=title_data.get('resolution'),
            quality=title_data.get('quality'),
            hash=hash
        )
else:
    # Formato original
    base_metadata["metadata_rootfoldername"] = f"{title} ({base_metadata['metadata_years']})"
```

**Step 2: Commit**

```bash
git add functions/torboxFunctions.py
git commit -m "feat: actualizar searchMetadata para nueva estructura"
```

---

## Task 8: Actualizar stremFilesystemFunctions.py

**Objetivo:** Modificar generateFolderPath para usar nueva estructura con resoluciones

**Archivos:**
- Modify: `functions/stremFilesystemFunctions.py`

**Step 1: Modificar generateFolderPath**

Reemplazar la función completa para soportar nueva estructura:

```python
def generateFolderPath(data: dict) -> str | None:
    """
    Genera la ruta de carpeta para un download.
    Soporta estructura mejorada con resoluciones.
    """
    from library.app import ENHANCED_FOLDER_STRUCTURE
    
    if RAW_MODE:
        original_path = data.get("path")
        if original_path:
            return os.path.dirname(original_path)
        return None
    
    if not ENHANCED_FOLDER_STRUCTURE:
        # Estructura original
        root_folder = data.get("metadata_rootfoldername", None)
        metadata_foldername = data.get("metadata_foldername", None)
        
        if not root_folder:
            return None
        
        if data.get("metadata_mediatype") == "series":
            if not metadata_foldername:
                return None
            return os.path.join(root_folder, metadata_foldername)
        elif data.get("metadata_mediatype") == "movie":
            return root_folder
        elif data.get("metadata_mediatype") == "anime":
            if not metadata_foldername:
                return None
            return os.path.join(root_folder, metadata_foldername)
        
        return root_folder
    
    # Nueva estructura mejorada
    category = data.get("current_category", "movies")
    root_folder = data.get("metadata_rootfoldername")
    
    if not root_folder:
        return None
    
    # Para películas, agregar subcarpeta de resolución
    if category == "movies":
        resolution_folder = data.get("current_resolution_folder", "unknown")
        folder_path = os.path.join(resolution_folder, root_folder)
    else:
        folder_path = root_folder
    
    # Para series, agregar carpeta de temporada
    if data.get("metadata_mediatype") in ["series", "anime"]:
        metadata_foldername = data.get("metadata_foldername")
        if metadata_foldername:
            folder_path = os.path.join(folder_path, metadata_foldername)
    
    return folder_path
```

**Step 2: Commit**

```bash
git add functions/stremFilesystemFunctions.py
git commit -m "feat: actualizar generateFolderPath para nueva estructura"
```

---

## Task 9: Actualizar generateStremFile para nueva estructura

**Objetivo:** Modificar generateStremFile para usar categorías correctas

**Archivos:**
- Modify: `functions/stremFilesystemFunctions.py:47-74`

**Step 1: Modificar generateStremFile**

```python
def generateStremFile(file_path: str, url: str, type: str, file_name: str, download=None):
    from library.app import ENHANCED_FOLDER_STRUCTURE
    
    if RAW_MODE:
        original_path = download.get("path")
        if original_path:
            full_path = os.path.join(MOUNT_PATH, os.path.dirname(original_path))
    elif ENHANCED_FOLDER_STRUCTURE:
        # Nueva estructura con categorías
        category = download.get("current_category", "movies")
        full_path = os.path.join(MOUNT_PATH, category, file_path)
    else:
        # Estructura original
        if type == "movie":
            type = "movies"
        elif type == "series":
            type = "series"
        elif type == "anime":
            type = "series"
        full_path = os.path.join(MOUNT_PATH, type, file_path)
    
    try:
        os.makedirs(full_path, exist_ok=True)
        with open(f"{full_path}/{file_name}.strm", "w") as file:
            file.write(url)
        logging.debug(f"Created strm file: {full_path}/{file_name}.strm")
        return True
    except FileNotFoundError as e:
        logging.error(f"Error creating strm file (likely bad naming scheme of file): {e}")
        return False
    except OSError as e:
        logging.error(f"Error creating strm file (likely bad or missing permissions): {e}")
        return False
    except Exception as e:
        logging.error(f"Error creating strm file: {e}")
        return False
```

**Step 2: Commit**

```bash
git add functions/stremFilesystemFunctions.py
git commit -m "feat: actualizar generateStremFile para categorías"
```

---

## Task 10: Integrar detección de cambios en runStrm

**Objetivo:** Agregar lógica para detectar y respetar cambios manuales

**Archivos:**
- Modify: `functions/stremFilesystemFunctions.py:76-114`

**Step 1: Modificar runStrm para incluir tracking**

Al inicio de la función, agregar:

```python
from library.app import ENHANCED_FOLDER_STRUCTURE, FORCE_RECLASSIFY
from functions.trackingFunctions import scan_current_locations, detect_manual_changes
from functions.databaseFunctions import updateData

# Detectar cambios manuales si no estamos forzando reclasificación
if ENHANCED_FOLDER_STRUCTURE and not FORCE_RECLASSIFY:
    current_locations = scan_current_locations()
    changes = detect_manual_changes(all_downloads, current_locations)
    
    # Aplicar cambios detectados
    for change in changes:
        record = change['record']
        record['current_category'] = change['new_category']
        record['current_resolution_folder'] = change['new_resolution']
        record['manual_override'] = True
        
        # Actualizar en DB
        updateData(record, record.get('type'))
```

**Step 2: Commit**

```bash
git add functions/stremFilesystemFunctions.py
git commit -m "feat: integrar detección de cambios manuales en runStrm"
```

---

## Task 11: Actualizar README

**Objetivo:** Documentar nueva funcionalidad

**Archivos:**
- Modify: `README.md`

**Step 1: Agregar documentación**

Después de línea 96, agregar:

```markdown
`ENHANCED_FOLDER_STRUCTURE` Enables enhanced folder structure with automatic classification. When enabled, content is organized into `movies/`, `series/`, `music/`, and `others/` categories. Movies are further organized by resolution (2160/, 1080/, 720/, 480/, unknown/). Folder names include technical metadata and a unique hash to prevent duplicates: "Title (Year) [1080p BluRay] {hash}/". The system tracks file locations and respects manual changes - if you move a folder to a different category or resolution, it will stay there. Default: `false`. This is optional.

`FORCE_RECLASSIFY` Forces complete reclassification of all content, ignoring any manual changes you've made. Useful for resetting the entire structure. Only works when `ENHANCED_FOLDER_STRUCTURE` is enabled. Default: `false`. This is optional.
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: documentar nueva estructura y tracking"
```

---

## Task 12: Crear tests

**Objetivo:** Crear script de prueba para verificar clasificación y formateo

**Archivos:**
- Create: `tests/test_classification.py`

**Step 1: Crear script de prueba**

```python
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.classificationFunctions import extract_resolution, classify_media_type
from functions.folderNamingFunctions import format_movie_folder, format_series_folder
import PTN

test_cases = [
    "The.Matrix.1999.1080p.BluRay.x264.DTS-FGT.mkv",
    "Inception.2010.2160p.UHD.BluRay.x265.HDR.mkv",
    "Breaking.Bad.S01E01.1080p.WEB-DL.mkv",
    "Game.of.Thrones.S08E06.720p.mkv",
]

print("=" * 80)
print("TEST DE CLASIFICACIÓN Y FORMATEO")
print("=" * 80)

for filename in test_cases:
    print(f"
Archivo: {filename}")
    print("-" * 80)
    
    parsed = PTN.parse(filename)
    resolution = extract_resolution(filename, parsed)
    media_type = classify_media_type(parsed, 'video/x-matroska')
    
    print(f"Resolución: {resolution}")
    print(f"Tipo: {media_type}")
    
    if media_type == 'movies':
        folder = format_movie_folder(
            title=parsed.get('title', 'Unknown'),
            year=parsed.get('year'),
            resolution=parsed.get('resolution'),
            quality=parsed.get('quality'),
            hash='abc123def456'
        )
        print(f"Carpeta: movies/{resolution}/{folder}/")
    else:
        folder = format_series_folder(
            title=parsed.get('title', 'Unknown'),
            year=parsed.get('year'),
            resolution=parsed.get('resolution'),
            hash='abc123def456'
        )
        print(f"Carpeta: series/{folder}/Season XX/")

print("
" + "=" * 80)
```

**Step 2: Ejecutar test**

Run: `python3 tests/test_classification.py`
Expected: Output mostrando clasificación correcta

**Step 3: Commit**

```bash
git add tests/test_classification.py
git commit -m "test: agregar tests de clasificación"
```

---

## Task 13: Prueba de integración

**Objetivo:** Verificar que todo funciona correctamente

**Step 1: Verificar imports**

Run: `python3 -c "from functions.classificationFunctions import *; from functions.folderNamingFunctions import *; from functions.trackingFunctions import *; print('OK')"`
Expected: "OK"

**Step 2: Verificar variables de entorno**

Run: `python3 -c "from library.app import ENHANCED_FOLDER_STRUCTURE, FORCE_RECLASSIFY; print(f'ENHANCED: {ENHANCED_FOLDER_STRUCTURE}, FORCE: {FORCE_RECLASSIFY}')"`
Expected: Output con valores

**Step 3: Ejecutar tests**

Run: `python3 tests/test_classification.py`
Expected: Sin errores

**Step 4: Verificar sintaxis de todos los archivos**

Run: `python3 -m py_compile functions/*.py library/*.py`
Expected: Sin errores

---

## Resumen

### Archivos Nuevos:
- `functions/classificationFunctions.py` - Clasificación y extracción de resolución
- `functions/folderNamingFunctions.py` - Formateo de carpetas con hash
- `functions/trackingFunctions.py` - Detección de cambios manuales
- `tests/test_classification.py` - Tests

### Archivos Modificados:
- `functions/databaseFunctions.py` - Campos de tracking
- `library/app.py` - Variables ENHANCED_FOLDER_STRUCTURE y FORCE_RECLASSIFY
- `.env.example` - Documentación
- `functions/torboxFunctions.py` - Integración de clasificación
- `functions/stremFilesystemFunctions.py` - Nueva estructura y tracking
- `README.md` - Documentación

### Funcionalidad:
✅ Estructura: movies/{resolution}/, series/, music/, others/
✅ Resoluciones: 2160/, 1080/, 720/, 480/, unknown/
✅ Hash en carpetas previene duplicados
✅ Sistema de tracking en base de datos
✅ Respeta cambios manuales del usuario
✅ Flag FORCE_RECLASSIFY para resetear
✅ Compatible con estructura actual (default: false)
