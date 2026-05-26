# Mejorar Organización de Carpetas con PTN - Plan de Implementación

> **Para Hermes:** Usa el skill subagent-driven-development para implementar este plan tarea por tarea.

**Objetivo:** Mejorar la organización de carpetas usando PTN (Parse Torrent Name) para crear una estructura de directorios más detallada y organizada, manteniendo los nombres de archivo originales sin cambios.

**Arquitectura:** 
- Expandir el uso de PTN para extraer todos los campos disponibles (resolución, codec, audio, calidad, año)
- Crear funciones de formateo de nombres de **carpetas** más robustas
- Agregar opción de estructura de carpetas mejorada (opcional vía variable de entorno)
- Mantener nombres de archivo originales (metadata_filename sin cambios)
- Mantener compatibilidad con estructura actual por defecto

**Ejemplo de estructura mejorada:**
```
movies/
  ├── Action/
  │   └── The Matrix (1999) [1080p BluRay]/
  │       └── The.Matrix.1999.1080p.BluRay.x264.mkv
  └── Drama/
      └── Inception (2010) [2160p WEB-DL]/
          └── Inception.2010.2160p.WEB-DL.x265.mkv

series/
  ├── Breaking Bad (2008) [1080p]/
  │   ├── Season 01/
  │   │   ├── Breaking.Bad.S01E01.1080p.WEB-DL.mkv
  │   │   └── Breaking.Bad.S01E02.1080p.WEB-DL.mkv
  │   └── Season 02/
  └── Game of Thrones (2011) [2160p]/
      └── Season 08/
```

**Tech Stack:** 
- PTN (ya instalado)
- Python 3.6+
- Estructura actual del proyecto

---

## Task 1: Crear módulo de parsing mejorado para carpetas

**Objetivo:** Crear un nuevo módulo que encapsule toda la lógica de parsing y formateo de nombres de carpetas

**Archivos:**
- Create: `functions/folderNamingFunctions.py`
- Test: Manual (verificar con nombres de ejemplo)

**Step 1: Crear archivo base con función de parsing extendido**

```python
import PTN
import logging
from typing import Dict, Optional

def parse_filename_extended(filename: str) -> Dict:
    """
    Parse filename usando PTN y retorna metadata extendida.
    
    Args:
        filename: Nombre del archivo a parsear
        
    Returns:
        Dict con metadata parseada incluyendo:
        - title: Título limpio
        - year: Año
        - season: Temporada (para series)
        - episode: Episodio (para series)
        - resolution: Resolución (1080p, 720p, 4K, etc.)
        - codec: Codec de video (x264, x265, HEVC, etc.)
        - audio: Codec de audio (AAC, DTS, etc.)
        - quality: Calidad (BluRay, WEB-DL, HDTV, etc.)
        - group: Grupo de release
    """
    try:
        parsed = PTN.parse(filename)
        
        # Extraer información adicional que PTN puede proveer
        result = {
            'title': parsed.get('title', ''),
            'year': parsed.get('year'),
            'season': parsed.get('season'),
            'episode': parsed.get('episode'),
            'resolution': parsed.get('resolution'),
            'codec': parsed.get('codec'),
            'audio': parsed.get('audio'),
            'quality': parsed.get('quality'),
            'group': parsed.get('group'),
            'excess': parsed.get('excess', []),
        }
        
        logging.debug(f"Parsed '{filename}': {result}")
        return result
        
    except Exception as e:
        logging.error(f"Error parsing filename '{filename}': {e}")
        return {
            'title': filename,
            'year': None,
            'season': None,
            'episode': None,
            'resolution': None,
            'codec': None,
            'audio': None,
            'quality': None,
            'group': None,
            'excess': [],
        }
```

**Step 2: Agregar función de formateo de carpeta raíz para películas**

```python
def format_movie_root_folder(parsed_data: Dict, title_override: str = None, year_override: int = None) -> str:
    """
    Formatea nombre de carpeta raíz para película con metadata técnica.
    
    Formato: "Title (Year) [Resolution Quality]"
    Ejemplo: "The Matrix (1999) [1080p BluRay]"
    
    Args:
        parsed_data: Dict con metadata parseada de PTN
        title_override: Título desde API de metadata (más limpio)
        year_override: Año desde API de metadata
        
    Returns:
        Nombre de carpeta formateado
    """
    from functions.mediaFunctions import cleanTitle
    
    # Usar override si está disponible (viene de API), sino usar parsed
    title = title_override if title_override else parsed_data.get('title', 'Unknown')
    year = year_override if year_override else parsed_data.get('year')
    resolution = parsed_data.get('resolution')
    quality = parsed_data.get('quality')
    
    # Construir nombre base
    parts = [title]
    
    if year:
        parts.append(f"({year})")
    
    # Agregar metadata técnica si está disponible
    tech_parts = []
    if resolution:
        tech_parts.append(resolution)
    if quality:
        tech_parts.append(quality)
    
    if tech_parts:
        parts.append(f"[{' '.join(tech_parts)}]")
    
    folder_name = " ".join(parts)
    
    # Limpiar caracteres inválidos
    folder_name = cleanTitle(folder_name)
    
    return folder_name
```

**Step 3: Agregar función de formateo de carpeta raíz para series**

```python
def format_series_root_folder(parsed_data: Dict, title_override: str = None, year_override: int = None) -> str:
    """
    Formatea nombre de carpeta raíz para serie con metadata técnica.
    
    Formato: "Title (Year) [Resolution]"
    Ejemplo: "Breaking Bad (2008) [1080p]"
    
    Args:
        parsed_data: Dict con metadata parseada de PTN
        title_override: Título desde API de metadata (más limpio)
        year_override: Año desde API de metadata
        
    Returns:
        Nombre de carpeta formateado
    """
    from functions.mediaFunctions import cleanTitle
    
    # Usar override si está disponible (viene de API), sino usar parsed
    title = title_override if title_override else parsed_data.get('title', 'Unknown')
    year = year_override if year_override else parsed_data.get('year')
    resolution = parsed_data.get('resolution')
    
    # Construir nombre base
    parts = [title]
    
    if year:
        parts.append(f"({year})")
    
    # Para series, solo agregar resolución (no calidad, porque puede variar por temporada)
    if resolution:
        parts.append(f"[{resolution}]")
    
    folder_name = " ".join(parts)
    
    # Limpiar caracteres inválidos
    folder_name = cleanTitle(folder_name)
    
    return folder_name
```

**Step 4: Verificar sintaxis**

Run: `python3 -m py_compile functions/folderNamingFunctions.py`
Expected: Sin errores

**Step 5: Commit**

```bash
git add functions/folderNamingFunctions.py
git commit -m "feat: agregar módulo de formateo de carpetas con PTN"
```

---

## Task 2: Agregar variable de entorno para habilitar formato mejorado

**Objetivo:** Agregar configuración opcional para usar el nuevo formato de carpetas sin romper instalaciones existentes

**Archivos:**
- Modify: `library/app.py`
- Modify: `.env.example`

**Step 1: Leer archivo actual de configuración**

Run: `cat library/app.py`

**Step 2: Agregar variable de entorno ENHANCED_FOLDER_STRUCTURE**

Agregar después de las variables existentes en `library/app.py`:

```python
ENHANCED_FOLDER_STRUCTURE = os.getenv("ENHANCED_FOLDER_STRUCTURE", "false").lower() == "true"
```

**Step 3: Actualizar .env.example**

Agregar al final de `.env.example`:

```bash
# ENHANCED_FOLDER_STRUCTURE - Habilita estructura de carpetas mejorada con metadata técnica
# Si está habilitado, las carpetas incluirán resolución y calidad en sus nombres
# Formato películas: "Title (Year) [1080p BluRay]/"
# Formato series: "Title (Year) [1080p]/"
# Los nombres de archivo NO cambian, solo la estructura de carpetas
# Default: false (mantiene compatibilidad con estructura actual)
ENHANCED_FOLDER_STRUCTURE=false
```

**Step 4: Verificar sintaxis**

Run: `python3 -m py_compile library/app.py`
Expected: Sin errores

**Step 5: Commit**

```bash
git add library/app.py .env.example
git commit -m "feat: agregar variable ENHANCED_FOLDER_STRUCTURE"
```

---

## Task 3: Integrar parsing mejorado en torboxFunctions.py

**Objetivo:** Usar las nuevas funciones de formateo de carpetas en la función searchMetadata

**Archivos:**
- Modify: `functions/torboxFunctions.py`

**Step 1: Agregar imports del nuevo módulo**

En la sección de imports (después de línea 7), agregar:

```python
from functions.folderNamingFunctions import parse_filename_extended, format_movie_root_folder, format_series_root_folder
from library.app import ENHANCED_FOLDER_STRUCTURE
```

**Step 2: Modificar función process_file para usar parsing extendido**

Reemplazar línea 52:
```python
title_data = PTN.parse(file.get("short_name"))
```

Por:
```python
# Usar parsing extendido para obtener más metadata
title_data = parse_filename_extended(file.get("short_name"))
```

**Step 3: Verificar sintaxis**

Run: `python3 -m py_compile functions/torboxFunctions.py`
Expected: Sin errores

**Step 4: Commit**

```bash
git add functions/torboxFunctions.py
git commit -m "refactor: usar parsing extendido en process_file"
```

---

## Task 4: Actualizar searchMetadata para usar formato mejorado de carpetas

**Objetivo:** Modificar la función searchMetadata para generar nombres de carpeta con el nuevo formato cuando ENHANCED_FOLDER_STRUCTURE está habilitado

**Archivos:**
- Modify: `functions/torboxFunctions.py:135-193`

**Step 1: Modificar generación de metadata_rootfoldername para series**

Reemplazar línea 183:
```python
base_metadata["metadata_rootfoldername"] = f"{title} ({base_metadata['metadata_years']})"
```

Por:
```python
# Generar nombre de carpeta raíz
if ENHANCED_FOLDER_STRUCTURE:
    if data.get("type") == "anime" or data.get("type") == "series":
        base_metadata["metadata_rootfoldername"] = format_series_root_folder(
            title_data, 
            title_override=title, 
            year_override=base_metadata['metadata_years']
        )
    elif data.get("type") == "movie":
        base_metadata["metadata_rootfoldername"] = format_movie_root_folder(
            title_data, 
            title_override=title, 
            year_override=base_metadata['metadata_years']
        )
else:
    # Formato original
    base_metadata["metadata_rootfoldername"] = f"{title} ({base_metadata['metadata_years']})"
```

**Step 2: Verificar sintaxis**

Run: `python3 -m py_compile functions/torboxFunctions.py`
Expected: Sin errores

**Step 3: Commit**

```bash
git add functions/torboxFunctions.py
git commit -m "feat: integrar formato mejorado de carpetas en searchMetadata"
```

---

## Task 5: Agregar tests manuales con nombres de ejemplo

**Objetivo:** Crear script de prueba para verificar el parsing y formateo de carpetas

**Archivos:**
- Create: `tests/test_folder_naming.py`

**Step 1: Crear script de prueba**

```python
#!/usr/bin/env python3
"""
Script de prueba manual para verificar parsing y formateo de nombres de carpetas.
"""

import sys
import os

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.folderNamingFunctions import parse_filename_extended, format_movie_root_folder, format_series_root_folder

# Casos de prueba
test_cases = [
    # Películas
    {
        'filename': "The.Matrix.1999.1080p.BluRay.x264.DTS-FGT.mkv",
        'type': 'movie',
        'api_title': 'The Matrix',
        'api_year': 1999,
    },
    {
        'filename': "Inception.2010.2160p.UHD.BluRay.x265.HDR.DTS-HD.MA.5.1-RARBG.mkv",
        'type': 'movie',
        'api_title': 'Inception',
        'api_year': 2010,
    },
    {
        'filename': "Interstellar.2014.720p.WEB-DL.x264.AAC-YTS.mp4",
        'type': 'movie',
        'api_title': 'Interstellar',
        'api_year': 2014,
    },
    
    # Series
    {
        'filename': "Breaking.Bad.S01E01.1080p.WEB-DL.DD5.1.H.264-NTb.mkv",
        'type': 'series',
        'api_title': 'Breaking Bad',
        'api_year': 2008,
    },
    {
        'filename': "Game.of.Thrones.S08E06.The.Iron.Throne.2160p.WEB-DL.DDP5.1.HEVC-NTb.mkv",
        'type': 'series',
        'api_title': 'Game of Thrones',
        'api_year': 2011,
    },
    {
        'filename': "The.Office.US.S03E15.720p.BluRay.x264-DEMAND.mkv",
        'type': 'series',
        'api_title': 'The Office',
        'api_year': 2005,
    },
]

print("=" * 80)
print("TEST DE PARSING Y FORMATEO DE CARPETAS")
print("=" * 80)

for test in test_cases:
    filename = test['filename']
    media_type = test['type']
    api_title = test['api_title']
    api_year = test['api_year']
    
    print(f"\nArchivo original: {filename}")
    print(f"Tipo: {media_type}")
    print("-" * 80)
    
    # Parse
    parsed = parse_filename_extended(filename)
    print(f"Metadata parseada:")
    for key, value in parsed.items():
        if value:
            print(f"  {key}: {value}")
    
    # Formatear carpeta
    if media_type == 'series':
        folder_name = format_series_root_folder(parsed, title_override=api_title, year_override=api_year)
    else:
        folder_name = format_movie_root_folder(parsed, title_override=api_title, year_override=api_year)
    
    print(f"\nCarpeta formateada: {folder_name}")
    print(f"Archivo mantiene nombre: {filename}")

print("\n" + "=" * 80)
print("FIN DE TESTS")
print("=" * 80)
```

**Step 2: Hacer ejecutable y correr**

Run: `chmod +x tests/test_folder_naming.py && python3 tests/test_folder_naming.py`
Expected: Output mostrando parsing y formateo de carpetas para cada caso

**Step 3: Commit**

```bash
git add tests/test_folder_naming.py
git commit -m "test: agregar script de prueba para formateo de carpetas"
```

---

## Task 6: Actualizar README con nueva funcionalidad

**Objetivo:** Documentar la nueva variable de entorno y funcionalidad

**Archivos:**
- Modify: `README.md`

**Step 1: Agregar documentación de ENHANCED_FOLDER_STRUCTURE**

Después de la línea 96 (después de ENABLE_METADATA), agregar:

```markdown
`ENHANCED_FOLDER_STRUCTURE` This option enables enhanced folder naming with technical metadata extracted from filenames. When enabled, folders will include resolution and quality information in their names, making it easier to organize and identify content at a glance. For movies: "Title (Year) [1080p BluRay]/". For series: "Title (Year) [1080p]/". **Important:** This only changes folder names - the actual video file names remain unchanged. The default is `false` to maintain compatibility with existing setups. This is optional.
```

**Step 2: Verificar que el README se ve bien**

Run: `head -100 README.md | tail -20`
Expected: Ver la nueva documentación

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: documentar variable ENHANCED_FOLDER_STRUCTURE en README"
```

---

## Task 7: Prueba de integración completa

**Objetivo:** Verificar que todo funciona correctamente con el sistema completo

**Archivos:**
- Test: Sistema completo

**Step 1: Verificar que todos los imports funcionan**

Run: `python3 -c "from functions.folderNamingFunctions import *; from functions.torboxFunctions import *; print('Imports OK')"`
Expected: "Imports OK"

**Step 2: Verificar que la configuración se lee correctamente**

Run: `python3 -c "from library.app import ENHANCED_FOLDER_STRUCTURE; print(f'ENHANCED_FOLDER_STRUCTURE: {ENHANCED_FOLDER_STRUCTURE}')"`
Expected: "ENHANCED_FOLDER_STRUCTURE: False" (o True si está configurado)

**Step 3: Ejecutar test de formateo de carpetas**

Run: `python3 tests/test_folder_naming.py`
Expected: Output sin errores mostrando todos los casos parseados

**Step 4: Verificar que no hay errores de sintaxis en archivos modificados**

Run: `python3 -m py_compile functions/*.py library/*.py`
Expected: Sin errores

---

## Resumen de Cambios

### Archivos Nuevos:
- `functions/folderNamingFunctions.py` - Módulo de parsing y formateo de carpetas
- `tests/test_folder_naming.py` - Script de pruebas manuales

### Archivos Modificados:
- `library/app.py` - Agregar variable ENHANCED_FOLDER_STRUCTURE
- `.env.example` - Documentar nueva variable
- `functions/torboxFunctions.py` - Integrar parsing y formateo mejorado de carpetas
- `README.md` - Documentar nueva funcionalidad

### Funcionalidad Agregada:
- Parsing extendido con PTN para extraer resolución, codec, audio, calidad
- Formateo mejorado de nombres de **carpetas** con metadata técnica
- **Nombres de archivo mantienen su formato original** (sin cambios)
- Opción configurable vía ENHANCED_FOLDER_STRUCTURE (default: false para compatibilidad)
- Mantiene estructura de carpetas actual (movies/series)
- Compatible con instalaciones existentes

### Ejemplos de Estructura:

**Con ENHANCED_FOLDER_STRUCTURE=false (actual):**
```
movies/
  └── The Matrix (1999)/
      └── The.Matrix.1999.1080p.BluRay.x264.mkv

series/
  └── Breaking Bad (2008)/
      └── Season 01/
          └── Breaking.Bad.S01E01.1080p.WEB-DL.mkv
```

**Con ENHANCED_FOLDER_STRUCTURE=true (mejorado):**
```
movies/
  └── The Matrix (1999) [1080p BluRay]/
      └── The.Matrix.1999.1080p.BluRay.x264.mkv

series/
  └── Breaking Bad (2008) [1080p]/
      └── Season 01/
          └── Breaking.Bad.S01E01.1080p.WEB-DL.mkv
```

### Próximos Pasos Opcionales:
- Agregar categorización por género en carpetas
- Crear estructura por calidad (movies/4K, movies/1080p)
- Agregar metadata de codec en carpetas de series por temporada
- Integrar con NFO files para Jellyfin/Plex
