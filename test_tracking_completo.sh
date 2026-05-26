#!/bin/bash

echo "========================================="
echo "PRUEBA COMPLETA DE TRACKING MANUAL"
echo "========================================="
echo ""

# Buscar el hash de Megan is Missing
HASH="90bda865"

echo "Paso 1: Estado inicial en la base de datos"
echo "-------------------------------------------"
docker compose exec torbox-media-center python3 -c "
from tinydb import TinyDB, Query
db = TinyDB('torrents.json')
q = Query()
records = db.search(q.folder_hash.search('$HASH'))
if records:
    r = records[0]
    print(f\"Título: {r.get('metadata_title')}\")
    print(f\"Categoría: {r.get('current_category')}\")
    print(f\"Resolución: {r.get('current_resolution_folder')}\")
    print(f\"Manual override: {r.get('manual_override')}\")
else:
    print('No encontrado en BD')
"

echo ""
echo "Paso 2: Ubicación actual en filesystem"
echo "---------------------------------------"
find torbox/movies -type d -name "*Megan*"

echo ""
echo "Paso 3: Mover manualmente de 2160 a 1080"
echo "-----------------------------------------"
if [ -d "torbox/movies/2160/Megan is Missing (2011) [1080p Blu-ray] {90bda865}" ]; then
    mv "torbox/movies/2160/Megan is Missing (2011) [1080p Blu-ray] {90bda865}" \
       "torbox/movies/1080/"
    echo "✓ Movido a 1080/"
else
    echo "✗ No está en 2160/, verificando ubicación..."
    find torbox/movies -type d -name "*Megan*"
fi

echo ""
echo "Paso 4: Forzar refresh para detectar cambio"
echo "--------------------------------------------"
docker compose exec torbox-media-center python3 -c "from functions.stremFilesystemFunctions import runStrm; runStrm()"
echo "✓ Refresh ejecutado"

echo ""
echo "Paso 5: Verificar detección de cambio manual en BD"
echo "----------------------------------------------------"
docker compose exec torbox-media-center python3 -c "
from tinydb import TinyDB, Query
db = TinyDB('torrents.json')
q = Query()
records = db.search(q.folder_hash.search('$HASH'))
if records:
    r = records[0]
    print(f\"Categoría: {r.get('current_category')}\")
    print(f\"Resolución: {r.get('current_resolution_folder')}\")
    print(f\"Manual override: {r.get('manual_override')}\")
    if r.get('manual_override') == True:
        print('✓ CAMBIO MANUAL DETECTADO')
    else:
        print('✗ NO SE DETECTÓ EL CAMBIO MANUAL')
else:
    print('✗ No encontrado en BD')
"

echo ""
echo "Paso 6: Verificar que NO se movió de vuelta"
echo "--------------------------------------------"
find torbox/movies -type d -name "*Megan*"

echo ""
echo "Paso 7: Forzar otro refresh"
echo "----------------------------"
docker compose exec torbox-media-center python3 -c "from functions.stremFilesystemFunctions import runStrm; runStrm()"
echo "✓ Segundo refresh ejecutado"

echo ""
echo "Paso 8: Verificar que SIGUE en la ubicación manual"
echo "---------------------------------------------------"
LOCATION=$(find torbox/movies -type d -name "*Megan*")
echo "Ubicación: $LOCATION"

if [[ "$LOCATION" == *"1080"* ]]; then
    echo "✓ ÉXITO: Se respetó la ubicación manual"
else
    echo "✗ FALLO: Se movió de vuelta automáticamente"
fi

echo ""
echo "========================================="
echo "RESUMEN"
echo "========================================="
docker compose exec torbox-media-center python3 -c "
from tinydb import TinyDB, Query
db = TinyDB('torrents.json')
q = Query()
records = db.search(q.folder_hash.search('$HASH'))
if records:
    r = records[0]
    print(f\"Estado final en BD:\")
    print(f\"  - Categoría: {r.get('current_category')}\")
    print(f\"  - Resolución: {r.get('current_resolution_folder')}\")
    print(f\"  - Manual override: {r.get('manual_override')}\")
"
LOCATION=$(find torbox/movies -type d -name "*Megan*")
echo "Estado final en filesystem:"
echo "  - Ubicación: $LOCATION"
