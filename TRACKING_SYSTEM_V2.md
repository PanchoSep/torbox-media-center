# Sistema de Tracking V2 - Simplificado

## Cambios Principales

### Antes (V1)
El sistema guardaba:
- `hash` - Hash del torrent
- `current_category` - Categoría (movies/series/music/others)
- `current_resolution_folder` - Resolución (2160/1080/720/480/unknown)
- `last_seen_path` - Última ubicación conocida
- `manual_override` - Si fue movido manualmente
- `added_at` - Timestamp de creación

**Problema:** Guardaba información redundante que ya está en el path y en la base de datos principal.

### Ahora (V2)
El sistema solo guarda:
- `hash` - Hash del torrent (primeros 8 chars)
- `last_seen_path` - Ruta completa del archivo .strm
- `strm_content` - Contenido del archivo .strm (URL)
- `added_at` - Timestamp de primera vez
- `updated_at` - Timestamp de última actualización

**Ventajas:**
- Más simple y directo
- No duplica información
- Solo actualiza cuando el contenido realmente cambió
- Más eficiente en cada refresh

## Flujo de Trabajo

### En cada refresh (`runStrm()`):

1. Para cada download de TorBox:
   - Genera el path del .strm
   - Extrae el hash (primeros 8 chars del `folder_hash`)
   - Llama a `should_update_strm(hash, path, content)`

2. `should_update_strm()` verifica:
   - ¿Existe registro en tracking? → No → **Crear archivo**
   - ¿El contenido cambió? → Sí → **Actualizar archivo**
   - ¿El archivo existe físicamente? → No → **Recrear archivo**
   - Todo igual → **Skip (no hace nada)**

3. Si necesita actualización:
   - Escribe el archivo .strm
   - Llama a `update_tracking(hash, path, content)`
   - Guarda/actualiza el registro en tracking.json

### Cuando se mueve desde la web:

1. Mueve la carpeta físicamente
2. Busca el .strm en la nueva ubicación
3. Lee su contenido
4. Actualiza tracking con el nuevo path y contenido

## Estructura de tracking.json

```json
[
  {
    "hash": "abc12345",
    "last_seen_path": "/mnt/strm/movies/2160/Movie Title (2024) [2160p Blu-ray] {abc12345}/Movie Title.strm",
    "strm_content": "http://torbox.app/download/xyz...",
    "added_at": 1716691200.0,
    "updated_at": 1716691200.0
  }
]
```

## Funciones Principales

### `trackingFunctions.py`

- `getData(torbox_hash)` - Busca un registro por hash
- `update_tracking(hash, path, content)` - Actualiza/inserta tracking
- `should_update_strm(hash, path, content)` - Determina si debe actualizar
- `read_strm_content(path)` - Lee contenido de un .strm

### `stremFilesystemFunctions.py`

- `generateStremFile()` - Ahora usa tracking para evitar reescrituras innecesarias

### `webFunctions.py`

- `scanLibrary()` - Ya no muestra `manual_override`
- `moveContent()` - Actualiza tracking con nuevo path

## Migración

Para limpiar la base de datos antigua:

```bash
# Detener el contenedor
docker compose down

# Eliminar tracking.json antiguo
rm tracking.json

# Reiniciar (se recreará automáticamente)
docker compose up -d
```

El sistema detectará que no hay tracking y creará registros nuevos en el primer refresh.

## Beneficios

1. **Menos escrituras:** Solo actualiza cuando el contenido cambió
2. **Más simple:** No guarda información redundante
3. **Más rápido:** Comparación directa de strings
4. **Más confiable:** El path es la fuente de verdad
5. **Más limpio:** Menos campos en la base de datos

## Compatibilidad

- ✅ Web interface sigue funcionando igual
- ✅ Mover archivos actualiza tracking correctamente
- ✅ Refresh detecta cambios de contenido
- ✅ No afecta la estructura de carpetas
- ✅ No afecta las bases de datos principales (torrents.json, usenet.json, webdl.json)

---

**Fecha:** 2026-05-26  
**Versión:** 2.0.0  
**Estado:** ✅ Implementado
