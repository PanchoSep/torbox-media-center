# Guía Rápida - Docker Compose

## Configuración Inicial

1. **Edita el archivo `.env` y agrega tu API key de TorBox:**
   ```bash
   nano .env
   ```
   
   Busca la línea `TORBOX_API_KEY=` y agrega tu key:
   ```
   TORBOX_API_KEY=tu_api_key_aqui
   ```

2. **Opcional: Habilita la estructura mejorada de carpetas**
   
   Si quieres usar la nueva funcionalidad con organización por resolución:
   ```
   ENHANCED_FOLDER_STRUCTURE=true
   ```

## Uso con el script de ayuda

```bash
./manage.sh
```

El script te mostrará un menú con opciones para:
- Iniciar el contenedor
- Ver logs
- Detener el contenedor
- Reiniciar
- Ver estado
- Reconstruir imagen

## Uso manual con Docker Compose

### Iniciar el contenedor
```bash
docker compose up -d
```

### Ver logs en tiempo real
```bash
docker compose logs -f
```

### Detener el contenedor
```bash
docker compose down
```

### Reiniciar el contenedor
```bash
docker compose restart
```

### Ver estado
```bash
docker compose ps
```

## Ubicación de archivos

- **Archivos .strm montados:** `./torbox/`
- **Base de datos:** `./db.json` y `./tracking.json`
- **Configuración:** `.env`

## Estructura de carpetas (con ENHANCED_FOLDER_STRUCTURE=true)

```
torbox/
├── movies/
│   ├── 2160/
│   │   └── Inception (2010) [2160p BluRay] {abc123}/
│   ├── 1080/
│   │   └── The Matrix (1999) [1080p BluRay] {def456}/
│   ├── 720/
│   ├── 480/
│   └── unknown/
├── series/
│   └── Breaking Bad (2008) [1080p] {jkl012}/
│       └── Season 01/
├── music/
└── others/
```

## Troubleshooting

### El contenedor no inicia
- Verifica que tu API key esté correctamente configurada en `.env`
- Revisa los logs: `docker compose logs`

### No veo archivos en ./torbox/
- Espera unos minutos, el escaneo inicial puede tardar
- Verifica que tengas archivos en tu cuenta de TorBox
- Revisa los logs para ver si hay errores

### Quiero resetear la estructura de carpetas
1. Detén el contenedor: `docker compose down`
2. Edita `.env` y configura: `FORCE_RECLASSIFY=true`
3. Inicia el contenedor: `docker compose up -d`
4. Después del primer escaneo, vuelve a poner `FORCE_RECLASSIFY=false`

## Más información

Consulta el README.md principal para documentación completa.
