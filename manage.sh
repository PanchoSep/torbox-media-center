#!/bin/bash

# Script de ayuda para TorBox Media Center

echo "=========================================="
echo "TorBox Media Center - Docker Compose"
echo "=========================================="
echo ""

# Verificar si existe .env
if [ ! -f .env ]; then
    echo "❌ Error: No se encontró el archivo .env"
    echo "Por favor copia .env.example a .env y configura tu TORBOX_API_KEY"
    exit 1
fi

# Verificar si TORBOX_API_KEY está configurado
if ! grep -q "TORBOX_API_KEY=.\+" .env; then
    echo "⚠️  Advertencia: TORBOX_API_KEY parece estar vacío en .env"
    echo "Por favor edita .env y agrega tu API key de TorBox"
    echo ""
    read -p "¿Deseas continuar de todos modos? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Menú de opciones
echo "Selecciona una opción:"
echo "1) Iniciar contenedor (docker compose up -d)"
echo "2) Ver logs (docker compose logs -f)"
echo "3) Detener contenedor (docker compose down)"
echo "4) Reiniciar contenedor (docker compose restart)"
echo "5) Ver estado (docker compose ps)"
echo "6) Reconstruir imagen (docker compose up -d --build)"
echo "7) Salir"
echo ""
read -p "Opción: " option

case $option in
    1)
        echo "Iniciando contenedor..."
        docker compose up -d
        echo ""
        echo "✅ Contenedor iniciado"
        echo "Los archivos .strm estarán disponibles en: ./torbox/"
        ;;
    2)
        echo "Mostrando logs (Ctrl+C para salir)..."
        docker compose logs -f
        ;;
    3)
        echo "Deteniendo contenedor..."
        docker compose down
        echo "✅ Contenedor detenido"
        ;;
    4)
        echo "Reiniciando contenedor..."
        docker compose restart
        echo "✅ Contenedor reiniciado"
        ;;
    5)
        docker compose ps
        ;;
    6)
        echo "Reconstruyendo imagen..."
        docker compose up -d --build
        echo "✅ Imagen reconstruida y contenedor iniciado"
        ;;
    7)
        echo "Saliendo..."
        exit 0
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac
