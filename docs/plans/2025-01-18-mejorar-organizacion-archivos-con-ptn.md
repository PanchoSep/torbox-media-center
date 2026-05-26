# Mejorar Organización de Archivos con PTN - Plan de Implementación

> **Para Hermes:** Usa el skill subagent-driven-development para implementar este plan tarea por tarea.

**Objetivo:** Mejorar la organización de archivos .strm usando PTN (Parse Torrent Name) de forma más completa para extraer metadata adicional (resolución, codec, audio, grupo de release) y crear una estructura de carpetas más detallada y compatible con Plex/Jellyfin/Emby.

**Arquitectura:** 
- Expandir el uso de PTN para extraer todos los campos disponibles (resolución, codec, audio, calidad, grupo)
- Crear funciones de formateo de nombres de archivo más robustas
- Agregar opción de estructura de carpetas mejorada (opcional vía variable de entorno)
- Mantener compatibilidad con estructura actual por defecto

**Tech Stack:** 
- PTN (ya instalado)
- Python 3.6+
- Estructura actual del proyecto

---

## Task 1: Crear módulo de parsing mejorado

**Objetivo:** Crear un nuevo módulo que encapsule toda la lógica de parsing de nombres de archivos con PTN

**Archivos:**
- Create: `functions/parsingFunctions.py`
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
        - container: Contenedor (mkv, mp4, avi)
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
            'container': parsed.get('container'),
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
            'container': None,
            'excess': [],
        }
```

**Step 2: Verificar que el archivo se creó correctamente**

Run: `ls -la functions/parsingFunctions.py`
Expected: Archivo existe

**Step 3: Commit**

```bash
git add functions/parsingFunctions.py
git commit -m "feat: agregar módulo de parsing extendido con PTN"
```

---

## Task 2: Agregar función de formateo de nombres mejorado

**Objetivo:** Crear funciones para formatear nombres de archivo con metadata adicional

**Archivos:**
- Modify: `functions/parsingFunctions.py`

**Step 1: Agregar función de formateo para películas**

```python
def format_movie_filename(parsed_data: Dict, extension: str = '.mkv') -> str:
    """
    Formatea nombre de archivo para película.
    
    Formato: "Title (Year) [Resolution] [Quality] [Codec] [Audio].ext"
    Ejemplo: "The Matrix (1999) [1080p] [BluRay] [x264] [DTS].mkv"
    
    Args:
        parsed_data: Dict con metadata parseada
        extension: Extensión del archivo
        
    Returns:
        Nombre de archivo formateado
    """
    title = parsed_data.get('title', 'Unknown')
    year = parsed_data.get('year')
    resolution = parsed_data.get('resolution')
    quality = parsed_data.get('quality')
    codec = parsed_data.get('codec')
    audio = parsed_data.get('audio')
    
    # Construir nombre base
    parts = [title]
    
    if year:
        parts.append(f"({year})")
    
    # Agregar metadata técnica si está disponible
    if resolution:
        parts.append(f"[{resolution}]")
    
    if quality:
        parts.append(f"[{quality}]")
        
    if codec:
        parts.append(f"[{codec}]")
        
    if audio:
        parts.append(f"[{audio}]")
    
    filename = " ".join(parts) + extension
    
    # Limpiar caracteres inválidos
    from functions.mediaFunctions import cleanTitle
    filename = cleanTitle(filename)
    
    return filename
```

**Step 2: Agregar función de formateo para series**

```python
def format_series_filename(parsed_data: Dict, extension: str = '.mkv') -> str:
    """
    Formatea nombre de archivo para episodio de serie.
    
    Formato: "Title SxxExx [Resolution] [Quality] [Codec].ext"
    Ejemplo: "Breaking Bad S01E01 [1080p] [WEB-DL] [x264].mkv"
    
    Args:
        parsed_data: Dict con metadata parseada
        extension: Extensión del archivo
        
    Returns:
        Nombre de archivo formateado
    """
    from functions.mediaFunctions import constructSeriesTitle
    
    title = parsed_data.get('title', 'Unknown')
    season = parsed_data.get('season')
    episode = parsed_data.get('episode')
    resolution = parsed_data.get('resolution')
    quality = parsed_data.get('quality')
    codec = parsed_data.get('codec')
    
    # Construir nombre base con SxxExx
    parts = [title]
    
    series_code = constructSeriesTitle(season=season, episode=episode)
    if series_code:
        parts.append(series_code)
    
    # Agregar metadata técnica
    if resolution:
        parts.append(f"[{resolution}]")
    
    if quality:
        parts.append(f"[{quality}]")
        
    if codec:
        parts.append(f"[{codec}]")
    
    filename = " ".join(parts) + extension
    
    # Limpiar caracteres inválidos
    from functions.mediaFunctions import cleanTitle
    filename = cleanTitle(filename)
    
    return filename
```

**Step 3: Agregar función de formateo de carpeta raíz**

```python
def format_root_folder(parsed_data: Dict, media_type: str) -> str:
    """
    Formatea nombre de carpeta raíz para película o serie.
    
    Para películas: "Title (Year)"
    Para series: "Title (Year)"
    
    Args:
        parsed_data: Dict con metadata parseada
        media_type: 'movie', 'series', o 'anime'
        
    Returns:
        Nombre de carpeta formateado
    """
    title = parsed_data.get('title', 'Unknown')
    year = parsed_data.get('year')
    
    if year:
        folder_name = f"{title} ({year})"
    else:
        folder_name = title
    
    # Limpiar caracteres inválidos
    from functions.mediaFunctions import cleanTitle
    folder_name = cleanTitle(folder_name)
    
    return folder_name
```

**Step 4: Verificar sintaxis**

Run: `python3 -m py_compile functions/parsingFunctions.py`
Expected: Sin errores

**Step 5: Commit**

```bash
git add functions/parsingFunctions.py
git commit -m "feat: agregar funciones de formateo de nombres mejorado"
```

---

## Task 3: Agregar variable de entorno para habilitar formato mejorado

**Objetivo:** Agregar configuración opcional para usar el nuevo formato sin romper instalaciones existentes

**Archivos:**
- Modify: `library/app.py`
- Modify: `.env.example`

**Step 1: Leer archivo actual de configuración**

Run: `cat library/app.py`

**Step 2: Agregar variable de entorno ENHANCED_NAMING**

Agregar después de las variables existentes en `library/app.py`:

```python
ENHANCED_NAMING = os.getenv("ENHANCED_NAMING", "false").lower() == "true"
```

**Step 3: Actualizar .env.example**

Agregar al final de `.env.example`:

```bash
# ENHANCED_NAMING - Habilita nombres de archivo mejorados con metadata técnica
# Si está habilitado, los archivos incluirán resolución, codec, audio, etc.
# Formato películas: "Title (Year) [1080p] [BluRay] [x264].mkv"
# Formato series: "Title S01E01 [1080p] [WEB-DL] [x264].mkv"
# Default: false (mantiene compatibilidad con estructura actual)
ENHANCED_NAMING=false
```

**Step 4: Verificar sintaxis**

Run: `python3 -m py_compile library/app.py`
Expected: Sin errores

**Step 5: Commit**

```bash
git add library/app.py .env.example
git commit -m "feat: agregar variable ENHANCED_NAMING para formato mejorado"
```

---

## Task 4: Integrar parsing mejorado en torboxFunctions.py

**Objetivo:** Reemplazar el uso básico de PTN con las nuevas funciones de parsing

**Archivos:**
- Modify: `functions/torboxFunctions.py`

**Step 1: Agregar import del nuevo módulo**

En la sección de imports (después de línea 7), agregar:

```python
from functions.parsingFunctions import parse_filename_extended, format_movie_filename, format_series_filename, format_root_folder
from library.app import ENHANCED_NAMING
```

**Step 2: Modificar función process_file para usar parsing extendido**

Reemplazar línea 52:
```python
title_data = PTN.parse(file.get("short_name"))
```

Por:
```python
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

## Task 5: Actualizar searchMetadata para usar formato mejorado

**Objetivo:** Modificar la función searchMetadata para generar nombres con el nuevo formato cuando ENHANCED_NAMING está habilitado

**Archivos:**
- Modify: `functions/torboxFunctions.py:135-193`

**Step 1: Modificar generación de nombres de archivo para series**

Reemplazar líneas 167-170:
```python
if data.get("type") == "anime" or data.get("type") == "series":
    series_season_episode = constructSeriesTitle(season=title_data.get("season", None), episode=title_data.get("episode", None))
    file_name = f"{title} {series_season_episode}{extension}"
    base_metadata["metadata_foldername"] = constructSeriesTitle(season=title_data.get("season", 1), folder=True)
```

Por:
```python
if data.get("type") == "anime" or data.get("type") == "series":
    if ENHANCED_NAMING:
        # Usar formato mejorado con metadata técnica
        enhanced_data = {
            'title': title,
            'season': title_data.get("season"),
            'episode': title_data.get("episode"),
            'resolution': title_data.get("resolution"),
            'quality': title_data.get("quality"),
            'codec': title_data.get("codec"),
        }
        file_name = format_series_filename(enhanced_data, extension)
    else:
        # Formato original
        series_season_episode = constructSeriesTitle(season=title_data.get("season", None), episode=title_data.get("episode", None))
        file_name = f"{title} {series_season_episode}{extension}"
    
    base_metadata["metadata_foldername"] = constructSeriesTitle(season=title_data.get("season", 1), folder=True)
```

**Step 2: Modificar generación de nombres de archivo para películas**

Reemplazar líneas 173-174:
```python
elif data.get("type") == "movie":
    file_name = f"{title} ({base_metadata['metadata_years']}){extension}"
```

Por:
```python
elif data.get("type") == "movie":
    if ENHANCED_NAMING:
        # Usar formato mejorado con metadata técnica
        enhanced_data = {
            'title': title,
            'year': base_metadata['metadata_years'],
            'resolution': title_data.get("resolution"),
            'quality': title_data.get("quality"),
            'codec': title_data.get("codec"),
            'audio': title_data.get("audio"),
        }
        file_name = format_movie_filename(enhanced_data, extension)
    else:
        # Formato original
        file_name = f"{title} ({base_metadata['metadata_years']}){extension}"
```

**Step 3: Verificar sintaxis**

Run: `python3 -m py_compile functions/torboxFunctions.py`
Expected: Sin errores

**Step 4: Commit**

```bash
git add functions/torboxFunctions.py
git commit -m "feat: integrar formato mejorado en searchMetadata"
```

---

## Task 6: Agregar tests manuales con nombres de ejemplo

**Objetivo:** Crear script de prueba para verificar el parsing y formateo

**Archivos:**
- Create: `tests/test_parsing.py`

**Step 1: Crear script de prueba**

```python
#!/usr/bin/env python3
"""
Script de prueba manual para verificar parsing y formateo de nombres.
"""

import sys
import os

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.parsingFunctions import parse_filename_extended, format_movie_filename, format_series_filename, format_root_folder

# Casos de prueba
test_cases = [
    # Películas
    "The.Matrix.1999.1080p.BluRay.x264.DTS-FGT.mkv",
    "Inception.2010.2160p.UHD.BluRay.x265.HDR.DTS-HD.MA.5.1-RARBG.mkv",
    "Interstellar.2014.720p.WEB-DL.x264.AAC-YTS.mp4",
    
    # Series
    "Breaking.Bad.S01E01.1080p.WEB-DL.DD5.1.H.264-NTb.mkv",
    "Game.of.Thrones.S08E06.The.Iron.Throne.2160p.WEB-DL.DDP5.1.HEVC-NTb.mkv",
    "The.Office.US.S03E15.720p.BluRay.x264-DEMAND.mkv",
]

print("=" * 80)
print("TEST DE PARSING Y FORMATEO")
print("=" * 80)

for filename in test_cases:
    print(f"\nOriginal: {filename}")
    print("-" * 80)
    
    # Parse
    parsed = parse_filename_extended(filename)
    print(f"Parsed data:")
    for key, value in parsed.items():
        if value:
            print(f"  {key}: {value}")
    
    # Determinar tipo
    is_series = parsed.get('season') is not None or parsed.get('episode') is not None
    
    # Formatear
    extension = os.path.splitext(filename)[1]
    if is_series:
        formatted = format_series_filename(parsed, extension)
        media_type = 'series'
    else:
        formatted = format_movie_filename(parsed, extension)
        media_type = 'movie'
    
    root_folder = format_root_folder(parsed, media_type)
    
    print(f"\nFormateado:")
    print(f"  Root folder: {root_folder}")
    print(f"  Filename: {formatted}")
    print(f"  Media type: {media_type}")

print("\n" + "=" * 80)
print("FIN DE TESTS")
print("=" * 80)
```

**Step 2: Hacer ejecutable y correr**

Run: `chmod +x tests/test_parsing.py && python3 tests/test_parsing.py`
Expected: Output mostrando parsing y formateo de cada caso

**Step 3: Commit**

```bash
git add tests/test_parsing.py
git commit -m "test: agregar script de prueba para parsing y formateo"
```

---

## Task 7: Actualizar README con nueva funcionalidad

**Objetivo:** Documentar la nueva variable de entorno y funcionalidad

**Archivos:**
- Modify: `README.md`

**Step 1: Agregar documentación de ENHANCED_NAMING**

Después de la línea 96 (después de ENABLE_METADATA), agregar:

```markdown
`ENHANCED_NAMING` This option enables enhanced file naming with technical metadata. When enabled, files will include resolution, codec, audio format, and quality in their names. For movies: "Title (Year) [1080p] [BluRay] [x264] [DTS].mkv". For series: "Title S01E01 [1080p] [WEB-DL] [x264].mkv". This provides better organization and makes it easier to identify file quality at a glance. The default is `false` to maintain compatibility with existing setups. This is optional.
```

**Step 2: Verificar que el README se ve bien**

Run: `head -100 README.md | tail -20`
Expected: Ver la nueva documentación

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: documentar variable ENHANCED_NAMING en README"
```

---

## Task 8: Prueba de integración completa

**Objetivo:** Verificar que todo funciona correctamente con el sistema completo

**Archivos:**
- Test: Sistema completo

**Step 1: Verificar que todos los imports funcionan**

Run: `python3 -c "from functions.parsingFunctions import *; from functions.torboxFunctions import *; print('Imports OK')"`
Expected: "Imports OK"

**Step 2: Verificar que la configuración se lee correctamente**

Run: `python3 -c "from library.app import ENHANCED_NAMING; print(f'ENHANCED_NAMING: {ENHANCED_NAMING}')"`
Expected: "ENHANCED_NAMING: False" (o True si está configurado)

**Step 3: Ejecutar test de parsing**

Run: `python3 tests/test_parsing.py`
Expected: Output sin errores mostrando todos los casos parseados

**Step 4: Verificar que no hay errores de sintaxis en archivos modificados**

Run: `python3 -m py_compile functions/*.py library/*.py`
Expected: Sin errores

---

## Resumen de Cambios

### Archivos Nuevos:
- `functions/parsingFunctions.py` - Módulo de parsing y formateo mejorado
- `tests/test_parsing.py` - Script de pruebas manuales

### Archivos Modificados:
- `library/app.py` - Agregar variable ENHANCED_NAMING
- `.env.example` - Documentar nueva variable
- `functions/torboxFunctions.py` - Integrar parsing y formateo mejorado
- `README.md` - Documentar nueva funcionalidad

### Funcionalidad Agregada:
- Parsing extendido con PTN para extraer resolución, codec, audio, calidad, grupo
- Formateo mejorado de nombres de archivo con metadata técnica
- Opción configurable vía ENHANCED_NAMING (default: false para compatibilidad)
- Mantiene estructura de carpetas actual (movies/series)
- Compatible con instalaciones existentes

### Próximos Pasos Opcionales:
- Agregar más opciones de formato (ej: incluir grupo de release)
- Crear estructura de carpetas por calidad (ej: movies/1080p, movies/4K)
- Agregar soporte para múltiples idiomas en nombres
- Integrar con sistema de metadata de Jellyfin/Plex para NFO files
