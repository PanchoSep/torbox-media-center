# ✅ TorBox Media Center - Instalación Completada

## Estado del Sistema

**Contenedor:** ✅ Corriendo
**Archivos .strm creados:** 11 archivos
**Ubicación:** /root/torbox-media-center/torbox/

## Configuración Actual

```
TORBOX_API_KEY: 9608caab-15c1-4154-91cd-49fa85deb9a6
MOUNT_METHOD: strm
MOUNT_PATH: /torbox
MOUNT_REFRESH_TIME: ultra_fast (cada 1 hora)
ENABLE_METADATA: false (sin rate limiting)
ENHANCED_FOLDER_STRUCTURE: false (estructura original)
```

## Estructura de Carpetas

```
torbox/
├── movies/     (11 películas)
└── series/     (vacío por ahora)
```

## Comandos Útiles

### Ver estado del contenedor
```bash
cd /root/torbox-media-center
docker compose ps
```

### Ver logs en tiempo real
```bash
docker compose logs -f
```

### Reiniciar contenedor
```bash
docker compose restart
```

### Detener contenedor
```bash
docker compose down
```

### Iniciar contenedor
```bash
docker compose up -d
```

### Ver archivos .strm creados
```bash
find torbox/ -name "*.strm"
```

### Usar el script de ayuda
```bash
./manage.sh
```

## Habilitar Estructura Mejorada (Opcional)

Si quieres usar la nueva funcionalidad con organización por resolución:

1. Edita `.env`:
   ```bash
   nano .env
   ```

2. Cambia:
   ```
   ENHANCED_FOLDER_STRUCTURE=true
   ```

3. Reinicia el contenedor:
   ```bash
   docker compose restart
   ```

Esto organizará tus películas en:
```
torbox/
├── movies/
│   ├── 2160/
│   ├── 1080/
│   ├── 720/
│   ├── 480/
│   └── unknown/
├── series/
├── music/
└── others/
```

## Próximos Pasos

1. **Configura tu media server** (Jellyfin/Emby/Plex) para que apunte a:
   `/root/torbox-media-center/torbox/`

2. **Escanea la biblioteca** en tu media server

3. **Disfruta** de tu contenido de TorBox

## Soporte

- Documentación completa: README.md
- Guía Docker: DOCKER_SETUP.md
- Logs: `docker compose logs -f`

---
Instalado el: 2026-05-26
