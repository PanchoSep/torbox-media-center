# 🌐 Interfaz Web de Administración

## 📋 Descripción

La interfaz web de TorBox Media Center te permite administrar tu biblioteca de medios de forma visual e intuitiva. Puedes mover archivos entre categorías, cambiar resoluciones, eliminar contenido y realizar acciones masivas, todo desde tu navegador.

## ✨ Características

### 🎯 Gestión Individual
- **Mover archivos** entre categorías (movies ↔ series ↔ music ↔ others)
- **Cambiar resolución** de películas (2160p ↔ 1080p ↔ 720p ↔ 480p ↔ unknown)
- **Eliminar archivos** del filesystem
- **Ver información** detallada (título, año, formato, resolución, cantidad de archivos)
- **Indicador visual** de archivos con cambios manuales (🔒 Manual)

### 📦 Acciones Masivas
- **Seleccionar múltiples archivos** con checkboxes
- **Seleccionar todos** los archivos de una categoría
- **Mover en lote** varios archivos a la vez
- **Eliminar en lote** múltiples archivos
- **Contador de selección** en tiempo real

### 🔍 Búsqueda y Filtros
- **Búsqueda por título** en tiempo real
- **Filtrar por categoría** (Movies, Series, Music, Others)
- **Filtrar por resolución** (2160p, 1080p, 720p, 480p, Unknown)
- **Combinación de filtros** para búsquedas precisas

### 📊 Información y Control
- **Estadísticas** de la biblioteca (total de archivos, por categoría, por resolución)
- **Refresh manual** para actualizar la biblioteca
- **Feedback visual** con notificaciones toast
- **Confirmaciones** para acciones destructivas

## 🚀 Acceso

### URL de Acceso
```
http://localhost:8080
```

Si estás accediendo desde otra máquina en tu red:
```
http://<IP_DEL_SERVIDOR>:8080
```

### Configuración

La interfaz web está habilitada por defecto. Puedes configurarla en el archivo `.env`:

```bash
# Habilitar/deshabilitar interfaz web
WEB_INTERFACE_ENABLED=true

# Puerto de la interfaz web
WEB_INTERFACE_PORT=8080
```

## 📖 Guía de Uso

### 1. Vista Principal

Al abrir la interfaz verás:
- **Header** con título y subtítulo
- **Toolbar** con botones de Refresh, Estadísticas y búsqueda
- **Filtros** por categoría y resolución
- **Biblioteca** organizada por categorías y resoluciones

### 2. Mover un Archivo Individual

1. Localiza el archivo en la biblioteca
2. Selecciona la **categoría destino** en el dropdown
3. Si es Movies, selecciona la **resolución destino**
4. Haz clic en **"Aplicar"**
5. El archivo se moverá inmediatamente y la base de datos se actualizará

**Ejemplo:**
```
Mover "Avatar Fire And Ash (2025)" de Movies/2160 a Series
→ Categoría: Series
→ Aplicar
✓ Archivo movido exitosamente
```

### 3. Eliminar un Archivo

1. Localiza el archivo en la biblioteca
2. Haz clic en el botón **"🗑️ Eliminar"**
3. Confirma la acción en el modal
4. El archivo y su carpeta se eliminarán del filesystem

**⚠️ Advertencia:** Esta acción no se puede deshacer.

### 4. Selección Múltiple

#### Seleccionar archivos individuales:
1. Marca los **checkboxes** de los archivos que quieras seleccionar
2. Aparecerá la barra de **acciones masivas** en la parte superior
3. El contador mostrará cuántos archivos tienes seleccionados

#### Seleccionar todos de una categoría:
1. En el header de cada categoría hay un checkbox **"Seleccionar todos"**
2. Marca ese checkbox para seleccionar todos los archivos visibles de esa categoría
3. Funciona con filtros activos (solo selecciona los archivos filtrados)

### 5. Mover Múltiples Archivos

1. Selecciona los archivos que quieras mover
2. En la barra de acciones masivas, selecciona la **categoría destino**
3. Si es Movies, selecciona la **resolución destino**
4. Haz clic en **"📁 Mover"**
5. Confirma la acción en el modal
6. Todos los archivos se moverán y verás un resumen del resultado

**Ejemplo:**
```
Seleccionados: 5 archivos
→ Mover a: Series
→ Confirmar
✓ 5 archivos movidos exitosamente
```

### 6. Eliminar Múltiples Archivos

1. Selecciona los archivos que quieras eliminar
2. En la barra de acciones masivas, haz clic en **"🗑️ Eliminar"**
3. Confirma la acción en el modal
4. Todos los archivos se eliminarán

**⚠️ Advertencia:** Esta acción no se puede deshacer.

### 7. Búsqueda

1. Escribe en el campo de búsqueda en la parte superior derecha
2. La biblioteca se filtrará en tiempo real
3. Busca por **título** o **año**
4. La búsqueda funciona en combinación con los filtros

**Ejemplo:**
```
Buscar: "avatar"
→ Muestra solo archivos que contengan "avatar" en el título
```

### 8. Filtros

#### Filtrar por categoría:
```
Categoría: Movies
→ Muestra solo películas
```

#### Filtrar por resolución:
```
Resolución: 2160p
→ Muestra solo contenido en 4K
```

#### Combinar filtros:
```
Categoría: Movies
Resolución: 1080p
Buscar: "2025"
→ Muestra solo películas de 1080p del año 2025
```

### 9. Refresh Manual

1. Haz clic en el botón **"🔄 Refresh"**
2. El sistema ejecutará `getAllUserDownloadsFresh()` y `runStrm()`
3. Verás una notificación cuando termine
4. La biblioteca se recargará automáticamente

**Uso:** Cuando agregues nuevos torrents a TorBox y quieras verlos inmediatamente.

### 10. Estadísticas

1. Haz clic en el botón **"📊 Estadísticas"**
2. Verás un modal con:
   - Total de archivos
   - Archivos por categoría
   - Archivos por resolución (Movies)
   - Cantidad de manual overrides

**Ejemplo:**
```
Total: 11 archivos

Por categoría:
• Movies: 11
• Series: 0
• Music: 0
• Others: 0

Resoluciones (Movies):
• 2160p: 10
• 1080p: 1

Manual overrides: 2
```

## 🎨 Interfaz

### Indicadores Visuales

- **🔒 Manual**: Badge amarillo que indica que el archivo tiene `manual_override: true`
- **Borde azul**: Archivo seleccionado
- **Fondo azul claro**: Archivo seleccionado (hover)
- **Spinner**: Operación en progreso

### Notificaciones Toast

- **Verde** (✓): Operación exitosa
- **Rojo** (✗): Error
- **Azul** (ℹ): Información

### Confirmaciones

Las acciones destructivas (eliminar) siempre piden confirmación en un modal.

## 🔧 Integración con Docker

La interfaz web se inicia automáticamente cuando arrancas el contenedor:

```bash
docker compose up -d
```

Logs del web server:
```bash
docker compose logs -f torbox-media-center | grep "web"
```

Verificar que está corriendo:
```bash
curl http://localhost:5000
```

## 📱 Responsive

La interfaz es completamente responsive y funciona en:
- **Desktop** (1400px+)
- **Tablet** (768px - 1400px)
- **Móvil** (< 768px)

En móvil, los controles se apilan verticalmente para mejor usabilidad.

## 🔒 Seguridad

### Estado Actual
- **Sin autenticación**: La interfaz es accesible sin login
- **Uso local**: Diseñada para uso en red local/Docker
- **Validación de inputs**: Todos los inputs son validados en backend

### Recomendaciones
1. **No expongas el puerto 5000 a internet** sin autenticación
2. Usa un **reverse proxy** (nginx, Caddy) si necesitas acceso externo
3. Considera agregar **autenticación básica** en el reverse proxy

## 🐛 Troubleshooting

### La interfaz no carga

1. Verifica que el contenedor está corriendo:
   ```bash
   docker compose ps
   ```

2. Verifica los logs:
   ```bash
   docker compose logs torbox-media-center
   ```

3. Verifica que el puerto está expuesto:
   ```bash
   docker compose port torbox-media-center 5000
   ```

### No veo mis archivos

1. Haz clic en **"🔄 Refresh"**
2. Verifica que `ENHANCED_FOLDER_STRUCTURE=true` en `.env`
3. Verifica los logs del contenedor

### Error al mover archivos

1. Verifica permisos del filesystem
2. Verifica que la carpeta destino existe
3. Revisa los logs del backend

### La búsqueda no funciona

1. Refresca la página (F5)
2. Limpia los filtros
3. Verifica la consola del navegador (F12)

## 🚀 Comandos Útiles

### Reiniciar solo el contenedor
```bash
docker compose restart torbox-media-center
```

### Ver logs en tiempo real
```bash
docker compose logs -f torbox-media-center
```

### Reconstruir con cambios
```bash
docker compose up -d --build
```

### Acceder al contenedor
```bash
docker compose exec torbox-media-center bash
```

## 📊 API Endpoints

La interfaz web consume estos endpoints:

- `GET /api/library` - Lista todos los archivos
- `POST /api/move` - Mueve un archivo
- `DELETE /api/delete` - Elimina uno o más archivos
- `POST /api/move-bulk` - Mueve múltiples archivos
- `POST /api/refresh` - Fuerza refresh manual
- `GET /api/stats` - Obtiene estadísticas

Puedes consumir estos endpoints desde otras aplicaciones si lo necesitas.

## 💡 Tips y Trucos

1. **Usa filtros combinados** para encontrar archivos específicos rápidamente
2. **Selecciona todos** de una categoría para mover en lote
3. **Busca por año** para organizar estrenos recientes
4. **Verifica el badge 🔒** para saber qué archivos moviste manualmente
5. **Usa Ctrl+F5** para forzar recarga si algo no se actualiza

## 🎯 Casos de Uso

### Reorganizar películas por resolución
1. Filtrar: Categoría = Movies, Resolución = 2160p
2. Seleccionar todas
3. Mover a: Movies / 1080p

### Mover series mal clasificadas
1. Buscar: "serie_name"
2. Seleccionar archivo
3. Categoría: Series
4. Aplicar

### Limpiar contenido antiguo
1. Buscar: "2020"
2. Seleccionar archivos no deseados
3. Eliminar en lote

### Organizar música
1. Filtrar: Categoría = Others
2. Buscar archivos de música
3. Mover a: Music

## 📝 Notas Importantes

1. **Actualización inmediata**: Todos los cambios se aplican inmediatamente en el filesystem y la base de datos
2. **Manual override**: Los archivos movidos desde la interfaz se marcan con `manual_override: true`
3. **Preservación de metadata**: Al mover archivos, se preservan todos los archivos adicionales (metadata, subtítulos)
4. **Sin deshacer**: Las eliminaciones son permanentes, no hay papelera de reciclaje
5. **Refresh automático**: El sistema sigue haciendo refresh según `MOUNT_REFRESH_TIME`, pero respeta tus cambios manuales

## 🆘 Soporte

Si encuentras problemas:
1. Revisa esta documentación
2. Verifica los logs del contenedor
3. Abre un issue en GitHub con detalles del error

---

**Versión:** 1.0.0  
**Última actualización:** 2026-05-26
