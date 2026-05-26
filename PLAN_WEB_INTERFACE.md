# Plan: Interfaz Web de Administración

## 📋 Objetivo

Crear una interfaz web simple que permita administrar la ubicación de películas y series, permitiendo:
- Mover contenido entre categorías (movies ↔ series ↔ music ↔ others)
- Cambiar resolución de películas (2160 ↔ 1080 ↔ 720 ↔ 480 ↔ unknown)
- Ver estado actual de todos los archivos
- Aplicar cambios de forma inmediata

## 🎯 Características Principales

### 1. Vista de Biblioteca
- **Lista de todos los archivos** organizados por categoría
- **Información mostrada:**
  - Título completo con año
  - Categoría actual (movies/series/music/others)
  - Resolución actual (solo para movies)
  - Formato (BluRay, WEB-DL, etc.)
  - Hash único
  - Ruta actual en filesystem

### 2. Acciones por Archivo
- **Selección múltiple:** Checkbox para seleccionar varios archivos
- **Cambiar categoría:** Dropdown con opciones (movies/series/music/others)
- **Cambiar resolución:** Dropdown con opciones (2160/1080/720/480/unknown) - solo visible para movies
- **Botón "Aplicar":** Ejecuta el movimiento inmediatamente
- **Botón "Eliminar":** Elimina el archivo/carpeta del filesystem
- **Indicador visual:** Muestra si el archivo tiene `manual_override: true`

### 3. Acciones Globales
- **Forzar refresh:** Ejecuta `getAllUserDownloadsFresh()` manualmente
- **Ver estadísticas:** Cantidad de archivos por categoría/resolución
- **Filtros:** Por categoría, resolución, o búsqueda por título
- **Acciones masivas:** Mover o eliminar múltiples archivos seleccionados
- **Seleccionar todo:** Checkbox para seleccionar todos los archivos visibles

## 🏗️ Arquitectura Técnica

### Stack Propuesto
```
Backend: Flask (ligero, simple, ya usan httpx)
Frontend: HTML + Vanilla JS + CSS (sin frameworks pesados)
Base de datos: TinyDB existente (tracking.json)
```

### Estructura de Archivos
```
torbox-media-center/
├── web/
│   ├── __init__.py
│   ├── app.py                    # Flask app principal
│   ├── routes.py                 # Endpoints API
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css         # Estilos
│   │   └── js/
│   │       └── app.js            # Lógica frontend
│   └── templates/
│       └── index.html            # UI principal
├── functions/
│   └── webFunctions.py           # Lógica de movimiento de archivos
└── requirements.txt              # Agregar Flask
```

## 📝 Implementación Detallada

### Fase 1: Backend API (Flask)

#### Endpoints necesarios:

**1. GET /api/library**
```json
{
  "movies": [
    {
      "hash": "9409c61a",
      "title": "Avatar Fire And Ash",
      "year": 2025,
      "category": "movies",
      "resolution": "2160",
      "format": "WEB-DL",
      "folder_name": "Avatar Fire And Ash (2025) [2160p WEB-DL] {9409c61a}",
      "current_path": "/torbox/movies/2160/Avatar Fire And Ash (2025) [2160p WEB-DL] {9409c61a}",
      "manual_override": false,
      "file_count": 1
    }
  ],
  "series": [],
  "music": [],
  "others": [],
  "stats": {
    "total": 11,
    "by_category": {"movies": 11, "series": 0, "music": 0, "others": 0},
    "by_resolution": {"2160": 10, "1080": 1, "720": 0, "480": 0, "unknown": 0}
  }
}
```

**2. POST /api/move**
```json
Request:
{
  "hash": "9409c61a",
  "from_category": "movies",
  "from_resolution": "2160",
  "to_category": "series",
  "to_resolution": null
}

Response:
{
  "success": true,
  "message": "Archivo movido exitosamente",
  "new_path": "/torbox/movies/series/Avatar Fire And Ash (2025) [2160p WEB-DL] {9409c61a}"
}
```

**3. POST /api/refresh**
```json
Response:
{
  "success": true,
  "message": "Refresh iniciado",
  "files_processed": 11
}
```

**4. DELETE /api/delete**
```json
Request:
{
  "hashes": ["9409c61a", "a0e5c271"]
}

Response:
{
  "success": true,
  "message": "2 archivos eliminados exitosamente",
  "deleted": ["9409c61a", "a0e5c271"],
  "failed": []
}
```

**5. POST /api/move-bulk**
```json
Request:
{
  "hashes": ["9409c61a", "a0e5c271"],
  "to_category": "series",
  "to_resolution": null
}

Response:
{
  "success": true,
  "message": "2 archivos movidos exitosamente",
  "moved": ["9409c61a", "a0e5c271"],
  "failed": []
}
```

**6. GET /api/stats**
```json
{
  "total_files": 11,
  "by_category": {"movies": 11, "series": 0, "music": 0, "others": 0},
  "by_resolution": {"2160": 10, "1080": 1},
  "manual_overrides": 0,
  "last_refresh": "2026-05-26T01:54:00Z"
}
```

### Fase 2: Lógica de Movimiento

**Función principal: `moveContent()`**

```python
def moveContent(hash: str, to_category: str, to_resolution: str = None) -> tuple[bool, str]:
    """
    Mueve un archivo a una nueva categoría/resolución.
    
    Pasos:
    1. Buscar archivo actual por hash en filesystem
    2. Validar categoría y resolución destino
    3. Construir nuevo nombre de carpeta
    4. Mover carpeta completa (preservando metadata)
    5. Actualizar tracking con manual_override=True
    6. Retornar resultado
    """
```

**Consideraciones:**
- Usar `shutil.move()` para mover carpetas completas
- Preservar todos los archivos (metadata, subtítulos, .strm)
- Actualizar base de datos tracking.json
- Marcar `manual_override: true`
- Validar que destino existe
- Manejar conflictos de nombres (hash previene esto)

### Fase 3: Frontend

#### Diseño UI (Simple y Funcional)

```
┌─────────────────────────────────────────────────────────────┐
│  TorBox Media Center - Administración                       │
│  ┌─────────────┬──────────┬──────────┐                     │
│  │ 📊 Stats    │ 🔄 Refresh│ 🔍 Buscar│                     │
│  └─────────────┴──────────┴──────────┘                     │
├─────────────────────────────────────────────────────────────┤
│  Filtros: [Todas ▼] [Todas resoluciones ▼]                 │
├─────────────────────────────────────────────────────────────┤
│  📁 Movies (11)                                             │
│  ├─ 2160p (10)                                              │
│  │  ┌───────────────────────────────────────────────────┐  │
│  │  │ Avatar Fire And Ash (2025) [2160p WEB-DL]        │  │
│  │  │ Categoría: [Movies ▼] Resolución: [2160p ▼]      │  │
│  │  │ [Aplicar] 🔒 Manual Override                      │  │
│  │  └───────────────────────────────────────────────────┘  │
│  │  ┌───────────────────────────────────────────────────┐  │
│  │  │ Crime 101 (2026) [2160p WEB-DL]                  │  │
│  │  │ Categoría: [Movies ▼] Resolución: [2160p ▼]      │  │
│  │  │ [Aplicar]                                         │  │
│  │  └───────────────────────────────────────────────────┘  │
│  └─ 1080p (1)                                               │
│     ┌───────────────────────────────────────────────────┐  │
│     │ Megan is Missing (2011) [1080p Blu-ray]          │  │
│     │ Categoría: [Movies ▼] Resolución: [1080p ▼]      │  │
│     │ [Aplicar]                                         │  │
│     └───────────────────────────────────────────────────┘  │
│  📁 Series (0)                                              │
│  📁 Music (0)                                               │
│  📁 Others (0)                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Características UI:
- **Responsive:** Funciona en móvil y desktop
- **Feedback visual:** Loading spinners, mensajes de éxito/error
- **Confirmación:** Modal para cambios importantes
- **Indicadores:** Badge para manual_override
- **Búsqueda en tiempo real:** Filtrar por título
- **Agrupación:** Por categoría y resolución

### Fase 4: Integración con Docker

**Modificar docker-compose.yaml:**
```yaml
services:
  torbox-media-center:
    ports:
      - "5000:5000"  # Puerto para web UI
    environment:
      - WEB_INTERFACE_ENABLED=true
      - WEB_INTERFACE_PORT=5000
```

**Modificar main.py:**
```python
# Iniciar web server en thread separado si está habilitado
if os.getenv('WEB_INTERFACE_ENABLED', 'false').lower() == 'true':
    from web.app import start_web_server
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
```

## 🔒 Seguridad

### Consideraciones:
1. **Sin autenticación inicial** (uso local/Docker)
2. **Validación de inputs:** Sanitizar categorías y resoluciones
3. **Rate limiting:** Prevenir spam de requests
4. **CORS:** Solo localhost si es necesario
5. **Futuro:** Agregar autenticación básica (usuario/contraseña)

## 📦 Dependencias Nuevas

```txt
Flask==3.0.0
flask-cors==4.0.0  # Si necesitas CORS
```

## 🧪 Testing

### Tests a crear:
1. **test_web_api.py** - Tests de endpoints
2. **test_move_content.py** - Tests de lógica de movimiento
3. **test_integration.py** - Tests end-to-end

### Casos de prueba:
- ✅ Mover movie de 2160 a 1080
- ✅ Mover movie a series (sin resolución)
- ✅ Mover series a movies (asignar resolución)
- ✅ Preservar metadata durante movimiento
- ✅ Actualizar tracking correctamente
- ✅ Manejar errores (archivo no existe, destino inválido)

## 📊 Plan de Implementación

### Tareas (Orden sugerido):

#### Sprint 1: Backend Core (2-3 horas)
1. ✅ Crear estructura de carpetas web/
2. ✅ Instalar Flask y dependencias
3. ✅ Crear webFunctions.py con lógica de movimiento
4. ✅ Implementar función scanLibrary()
5. ✅ Implementar función moveContent()
6. ✅ Crear tests unitarios

#### Sprint 2: API REST (1-2 horas)
7. ✅ Crear Flask app básica
8. ✅ Implementar GET /api/library
9. ✅ Implementar POST /api/move
10. ✅ Implementar POST /api/refresh
11. ✅ Implementar GET /api/stats
12. ✅ Agregar manejo de errores

#### Sprint 3: Frontend (2-3 horas)
13. ✅ Crear HTML base con estructura
14. ✅ Crear CSS para diseño responsive
15. ✅ Implementar JavaScript para cargar biblioteca
16. ✅ Implementar formularios de movimiento
17. ✅ Agregar feedback visual (loading, success, error)
18. ✅ Implementar búsqueda y filtros

#### Sprint 4: Integración (1 hora)
19. ✅ Integrar web server con main.py
20. ✅ Actualizar docker-compose.yaml
21. ✅ Actualizar .env.example
22. ✅ Probar en contenedor Docker

#### Sprint 5: Documentación (30 min)
23. ✅ Actualizar README.md
24. ✅ Crear WEB_INTERFACE.md con guía de uso
25. ✅ Agregar screenshots

## 🎨 Mejoras Futuras (Opcional)

1. **Drag & Drop:** Arrastrar archivos entre categorías
2. **Edición masiva:** Seleccionar múltiples archivos
3. **Historial:** Ver movimientos anteriores
4. **Previsualización:** Ver poster/metadata antes de mover
5. **Autenticación:** Login con usuario/contraseña
6. **Temas:** Dark mode / Light mode
7. **Notificaciones:** WebSocket para updates en tiempo real
8. **API externa:** Permitir control desde otras apps

## 📈 Métricas de Éxito

- ✅ Interfaz carga en < 2 segundos
- ✅ Movimiento de archivo completa en < 1 segundo
- ✅ UI funciona en móvil y desktop
- ✅ Sin errores en consola del navegador
- ✅ Preserva metadata durante movimientos
- ✅ Tracking actualizado correctamente

## 🚀 Comandos Útiles

```bash
# Desarrollo local
cd /root/torbox-media-center
python -m web.app  # Iniciar solo web server

# Con Docker
docker compose up --build

# Acceder a la interfaz
http://localhost:5000
```

## 📝 Notas Importantes

1. **No interferir con scheduler:** Web server corre en thread separado
2. **Preservar metadata:** Mover carpetas completas, no solo .strm
3. **Actualizar tracking:** Siempre marcar manual_override=True
4. **Validar destinos:** Asegurar que carpetas de destino existen
5. **Feedback al usuario:** Mostrar progreso y resultados claramente

## ❓ Preguntas para el Usuario

1. ✅ **Edición masiva:** Sí, seleccionar y mover/eliminar múltiples archivos
2. ✅ **Web server:** Siempre activo (integrado con main.py)
3. ✅ **Eliminación:** Sí, poder eliminar archivos desde la interfaz
4. ✅ **Puerto:** 5000 está bien
5. ❓ **Diseño:** ¿Prefieres minimalista o con más información visual?
6. ❓ **Autenticación:** ¿Necesitas login/password o está bien sin autenticación (uso local)?

---

**Tiempo estimado total:** 6-9 horas de desarrollo
**Complejidad:** Media
**Prioridad:** Alta (mejora significativa de UX)
