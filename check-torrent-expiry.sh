#!/bin/bash

if [ -z "$1" ]; then
    echo "Uso: $0 <torrent_id>"
    echo ""
    echo "Para ver los IDs de tus torrents:"
    echo "  docker compose exec torbox-media-center python3 -c \"from tinydb import TinyDB; db = TinyDB('torrents.json'); [print(f\\\"{r['item_id']}: {r['metadata_title']}\\\") for r in db.all()]\""
    exit 1
fi

TORRENT_ID=$1

echo "Reactivando torrent ID: $TORRENT_ID"
echo "Esto puede ayudar a mantener el archivo en caché..."

docker compose exec torbox-media-center python3 -c "
import httpx
from library.torbox import TORBOX_API_KEY

# Obtener info del torrent
response = httpx.get(
    f'https://api.torbox.app/v1/api/torrents/mylist',
    params={'bypass_cache': True, 'id': $TORRENT_ID},
    headers={'Authorization': f'Bearer {TORBOX_API_KEY}'},
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    if data.get('data'):
        torrent = data['data'][0]
        print(f\"Nombre: {torrent['name']}\")
        print(f\"Cached: {torrent['cached']}\")
        print(f\"Cached at: {torrent.get('cached_at', 'N/A')}\")
        print(f\"Expires at: {torrent.get('expires_at', 'N/A')}\")
        print(f\"Active: {torrent['active']}\")
        print(f\"Download state: {torrent['download_state']}\")
        print('')
        
        if torrent.get('expires_at'):
            print('⚠️  Este torrent tiene fecha de vencimiento')
        else:
            print('✓ Este torrent no tiene fecha de vencimiento configurada')
    else:
        print('Torrent no encontrado')
else:
    print(f'Error: {response.status_code}')
"
