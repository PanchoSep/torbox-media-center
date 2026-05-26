#!/bin/bash
echo "Forzando refresh de TorBox Media Center..."
docker compose exec torbox-media-center python3 -c "from functions.stremFilesystemFunctions import runStrm; runStrm()"
echo "✓ Refresh completado"
