# Preservación de Metadata de Jellyfin

## Problema Resuelto

Anteriormente, cuando Jellyfin descargaba metadata (posters, fanart, NFO) o subtítulos y los guardaba junto a los archivos .strm, estos se perdían cada vez que:
- Se reiniciaba el contenedor
- Se ejecutaba un refresh
- Se eliminaba un torrent

## Solución Implementada

El sistema ahora preserva automáticamente todos los archivos adicionales que no sean .strm durante el proceso de limpieza.

### Comportamiento

**Antes:**
```
1. Jellyfin descarga poster.jpg, fanart.jpg, movie.nfo
2. Se ejecuta un refresh
3. La carpeta se limpia completamente
4. Se pierden todos los archivos de metadata
5. Jellyfin tiene que volver a descargarlos
```

**Ahora:**
```
1. Jellyfin descarga poster.jpg, fanart.jpg, movie.nfo
2. Se ejecuta un refresh
3. El sistema detecta archivos adicionales
4. Solo se actualiza el archivo .strm
5. La metadata se preserva ✓
```

### Archivos Preservados

El sistema preserva cualquier archivo que no sea .strm, incluyendo:
- **Metadata de Jellyfin:** poster.jpg, fanart.jpg, backdrop.jpg, logo.png, etc.
- **Archivos NFO:** movie.nfo, tvshow.nfo, episode.nfo
- **Subtítulos:** .srt, .sub, .ass, .ssa, .vtt
- **Otros archivos:** cualquier archivo adicional que agregues manualmente

### Limpieza Inteligente

El sistema solo elimina carpetas que están **completamente vacías**:

```python
# Ejemplo de lógica
if carpeta_tiene_archivos:
    preservar_carpeta()  # Mantener metadata
else:
    eliminar_carpeta()   # Limpiar carpetas vacías
```

## Prueba

Para verificar que funciona:

```bash
cd /root/torbox-media-center
./test_metadata_preservation.sh
```

Este script:
1. Crea archivos de metadata simulados
2. Fuerza un refresh
3. Verifica que los archivos se preservaron
4. Limpia los archivos de prueba

## Logging

El sistema registra en los logs cuando preserva carpetas:

```
DEBUG: Preserving directory with metadata: torbox/movies/2160/Avatar (2009) [2160p BluRay] {abc123}/ (5 files)
```

Esto te permite verificar que la preservación está funcionando correctamente.

## Beneficios

1. **Ahorro de ancho de banda:** Jellyfin no tiene que volver a descargar metadata
2. **Mejor rendimiento:** No hay re-escaneo completo después de cada refresh
3. **Metadata personalizada:** Puedes agregar tus propias imágenes y se preservarán
4. **Subtítulos persistentes:** Los subtítulos descargados se mantienen

## Compatibilidad

Esta funcionalidad es compatible con:
- ✓ Jellyfin
- ✓ Plex
- ✓ Emby
- ✓ Kodi
- ✓ Cualquier media server que guarde metadata junto a los archivos

## Commit

`87a708b` - feat: preservar metadata y subtítulos de Jellyfin durante refresh

## Fecha

2026-05-26
