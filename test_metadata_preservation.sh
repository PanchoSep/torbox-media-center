#!/bin/bash

echo "========================================="
echo "PRUEBA DE PRESERVACIÓN DE METADATA"
echo "========================================="
echo ""

# Seleccionar una película para la prueba
MOVIE_FOLDER="torbox/movies/2160/Avatar Fire And Ash (2025) [2160p WEB-DL] {9409c61a}"

echo "Paso 1: Verificar que la carpeta existe"
echo "----------------------------------------"
if [ -d "$MOVIE_FOLDER" ]; then
    echo "✓ Carpeta encontrada: $MOVIE_FOLDER"
    ls -la "$MOVIE_FOLDER"
else
    echo "✗ Carpeta no encontrada"
    exit 1
fi

echo ""
echo "Paso 2: Simular metadata de Jellyfin"
echo "-------------------------------------"
# Crear archivos típicos que Jellyfin genera
touch "$MOVIE_FOLDER/poster.jpg"
touch "$MOVIE_FOLDER/fanart.jpg"
touch "$MOVIE_FOLDER/movie.nfo"
touch "$MOVIE_FOLDER/subtitle.srt"
echo "✓ Archivos de metadata creados:"
ls -la "$MOVIE_FOLDER"

echo ""
echo "Paso 3: Forzar refresh"
echo "----------------------"
./force-refresh.sh

echo ""
echo "Paso 4: Verificar que la metadata se preservó"
echo "----------------------------------------------"
if [ -f "$MOVIE_FOLDER/poster.jpg" ] && [ -f "$MOVIE_FOLDER/fanart.jpg" ] && [ -f "$MOVIE_FOLDER/movie.nfo" ] && [ -f "$MOVIE_FOLDER/subtitle.srt" ]; then
    echo "✓ ÉXITO: Todos los archivos de metadata se preservaron"
    ls -la "$MOVIE_FOLDER"
else
    echo "✗ FALLO: Algunos archivos de metadata se perdieron"
    ls -la "$MOVIE_FOLDER"
    exit 1
fi

echo ""
echo "Paso 5: Verificar que el .strm sigue existiendo"
echo "------------------------------------------------"
if [ -f "$MOVIE_FOLDER"/*.strm ]; then
    echo "✓ Archivo .strm presente"
else
    echo "✗ Archivo .strm no encontrado"
    exit 1
fi

echo ""
echo "========================================="
echo "RESULTADO: METADATA PRESERVADA ✓"
echo "========================================="
echo ""
echo "Limpiando archivos de prueba..."
rm -f "$MOVIE_FOLDER/poster.jpg" "$MOVIE_FOLDER/fanart.jpg" "$MOVIE_FOLDER/movie.nfo" "$MOVIE_FOLDER/subtitle.srt"
echo "✓ Limpieza completada"
