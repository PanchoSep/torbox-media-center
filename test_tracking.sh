#!/bin/bash

echo "=== PRUEBA DE TRACKING MANUAL ==="
echo ""
echo "Paso 1: Ver estructura actual"
find torbox/movies -type d -maxdepth 2 | sort

echo ""
echo "Paso 2: Mover una película de 1080 a 2160 manualmente"
echo "Moviendo: Megan is Missing (2011) [1080p Blu-ray] {90bda865}"
mv "torbox/movies/1080/Megan is Missing (2011) [1080p Blu-ray] {90bda865}" \
   "torbox/movies/2160/"

echo ""
echo "Paso 3: Verificar que se movió"
find torbox/movies -type d -name "*Megan*"

echo ""
echo "Paso 4: Esperar 5 segundos y verificar que NO se movió de vuelta"
sleep 5
find torbox/movies -type d -name "*Megan*"

echo ""
echo "=== RESULTADO ==="
if [ -d "torbox/movies/2160/Megan is Missing (2011) [1080p Blu-ray] {90bda865}" ]; then
    echo "✓ ÉXITO: La carpeta se mantuvo en 2160/ donde la movimos"
else
    echo "✗ FALLO: La carpeta fue movida de vuelta automáticamente"
fi
