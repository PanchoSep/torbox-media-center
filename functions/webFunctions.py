import logging
import os
import shutil
import glob
import re
from typing import Optional, Dict, List, Tuple
from functions.trackingFunctions import update_tracking, getData
from functions.databaseFunctions import getDatabase, getDatabaseLock
from functions.stremFilesystemFunctions import generateFolderPath
from functions.folderNamingFunctions import format_movie_folder, format_series_folder
from library.filesystem import MOUNT_PATH
from tinydb import Query
import threading

# Lock global para operaciones de base de datos
db_lock = threading.Lock()

logger = logging.getLogger(__name__)

def scanLibrary() -> Dict[str, List[Dict]]:
    """
    Escanea el filesystem y retorna todos los archivos organizados por categoría.
    
    Returns:
        Dict con categorías como keys y listas de archivos como values
    """
    library = {
        'movies': [],
        'series': [],
        'music': [],
        'others': []
    }
    
    # Buscar todos los .strm recursivamente
    strm_files = glob.glob(os.path.join(MOUNT_PATH, "**", "*.strm"), recursive=True)
    
    for strm_path in strm_files:
        # Extraer información de la ruta
        rel_path = os.path.relpath(strm_path, MOUNT_PATH)
        parts = rel_path.split(os.sep)
        
        if len(parts) < 2:
            continue
        
        category = parts[0]  # movies, series, music, others
        
        if category not in library:
            continue
        
        # Extraer hash del nombre de carpeta
        folder_name = parts[-2] if len(parts) > 1 else None
        hash_match = None
        title = "Unknown"
        year = None
        resolution = None
        format_type = None
        
        if folder_name:
            # Extraer hash
            match = re.search(r'\{([a-f0-9]+)\}', folder_name)
            if match:
                hash_match = match.group(1)
            
            # Extraer título y año: "Title (Year) [Resolution Format] {hash}"
            title_match = re.match(r'^(.+?)\s*\((\d{4})\)', folder_name)
            if title_match:
                title = title_match.group(1).strip()
                year = int(title_match.group(2))
            else:
                # Sin año, solo título
                title_match = re.match(r'^(.+?)\s*\[', folder_name)
                if title_match:
                    title = title_match.group(1).strip()
            
            # Extraer resolución y formato: [1080p Blu-ray]
            format_match = re.search(r'\[([^\]]+)\]', folder_name)
            if format_match:
                format_str = format_match.group(1)
                # Separar resolución y formato
                parts_format = format_str.split(maxsplit=1)
                if len(parts_format) >= 1:
                    resolution = parts_format[0].rstrip('p')  # "1080p" -> "1080"
                if len(parts_format) >= 2:
                    format_type = parts_format[1]
        
        if not hash_match:
            continue
        
        # Determinar carpeta de resolución (solo para movies)
        resolution_folder = None
        if category == 'movies' and len(parts) >= 3:
            resolution_folder = parts[1]  # 2160, 1080, etc.
        
        # Buscar tracking info
        tracking_data = getData(hash_match, "tracking")
        added_at = tracking_data.get('added_at', 0) if tracking_data else 0
        
        # Buscar información de expiración en las bases de datos de torrents/usenet/webdl
        expires_at = None
        created_at = None
        for db_type in ['torrents', 'usenet', 'webdl']:
            db = getDatabase(db_type)
            db_lock = getDatabaseLock(db_type)
            if db and db_lock:
                with db_lock:
                    q = Query()
                    results = db.search(q.folder_hash == hash_match)
                    if results:
                        expires_at = results[0].get('expires_at')
                        created_at = results[0].get('created_at')
                        break
        
        # Contar archivos en la carpeta
        folder_path = os.path.dirname(strm_path)
        file_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
        
        # Obtener nombre del archivo .strm
        strm_filename = os.path.basename(strm_path)
        
        file_info = {
            'hash': hash_match,
            'title': title,
            'year': year,
            'category': category,
            'resolution': resolution_folder or resolution or 'unknown',
            'format': format_type or 'Unknown',
            'folder_name': folder_name,
            'current_path': folder_path,
            'strm_path': strm_path,
            'strm_filename': strm_filename,
            'file_count': file_count,
            'added_at': added_at,
            'expires_at': expires_at,
            'created_at': created_at
        }
        
        library[category].append(file_info)
    
    # Ordenar por fecha de agregado (más recientes primero)
    for category in library:
        library[category].sort(key=lambda x: x['added_at'], reverse=True)
    
    return library


def moveContent(hash: str, to_category: str, to_resolution: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
    """
    Mueve un archivo a una nueva categoría/resolución.
    
    Args:
        hash: Hash único del archivo (primeros 8 caracteres)
        to_category: Categoría destino (movies/series/music/others)
        to_resolution: Resolución destino (2160/1080/720/480/unknown) - solo para movies
    
    Returns:
        Tuple[bool, str, Optional[str]]: (success, message, new_path)
    """
    # Validar categoría
    valid_categories = ['movies', 'series', 'music', 'others']
    if to_category not in valid_categories:
        return False, f"Categoría inválida: {to_category}", None
    
    # Validar resolución si es movies
    if to_category == 'movies':
        valid_resolutions = ['2160', '1080', '720', '480', 'unknown']
        if to_resolution and to_resolution not in valid_resolutions:
            return False, f"Resolución inválida: {to_resolution}", None
        if not to_resolution:
            to_resolution = 'unknown'
    else:
        to_resolution = None
    
    # Buscar carpeta actual por hash
    current_folder = None
    current_category = None
    
    for category in ['movies', 'series', 'music', 'others']:
        pattern = os.path.join(MOUNT_PATH, category, "**", f"*{{{hash}}}*")
        matches = glob.glob(pattern, recursive=True)
        
        for match in matches:
            if os.path.isdir(match):
                current_folder = match
                current_category = category
                break
        
        if current_folder:
            break
    
    if not current_folder:
        return False, f"No se encontró archivo con hash: {hash}", None
    
    # Construir ruta destino
    folder_name = os.path.basename(current_folder)
    
    if to_category == 'movies' and to_resolution:
        dest_base = os.path.join(MOUNT_PATH, to_category, to_resolution)
    else:
        dest_base = os.path.join(MOUNT_PATH, to_category)
    
    dest_folder = os.path.join(dest_base, folder_name)
    
    # Verificar que destino no existe
    if os.path.exists(dest_folder):
        return False, f"La carpeta destino ya existe: {dest_folder}", None
    
    # Crear carpeta base si no existe
    os.makedirs(dest_base, exist_ok=True)
    
    try:
        # Mover carpeta completa (preserva metadata, subtítulos, etc.)
        shutil.move(current_folder, dest_folder)
        logger.info(f"Moved {current_folder} -> {dest_folder}")
        
        # Actualizar tracking con nuevo path
        # Buscar el archivo .strm en la nueva ubicación
        import time
        time.sleep(0.1)  # Pequeño delay para que el filesystem se sincronice
        
        strm_files = []
        # Buscar recursivamente
        for root, dirs, files in os.walk(dest_folder):
            for file in files:
                if file.endswith('.strm'):
                    strm_files.append(os.path.join(root, file))
        
        if strm_files:
            strm_path = strm_files[0]
            logger.info(f"Found strm file for tracking update: {strm_path}")
            # Leer contenido del .strm
            try:
                with open(strm_path, 'r', encoding='utf-8') as f:
                    strm_content = f.read().strip()
                
                success, msg = update_tracking(hash, strm_path, strm_content)
                if success:
                    logger.info(f"Updated tracking for {hash}: {msg}")
                else:
                    logger.warning(f"Failed to update tracking: {msg}")
            except Exception as e:
                logger.warning(f"Failed to read strm file for tracking update: {e}")
        else:
            logger.warning(f"No strm files found in {dest_folder} for tracking update")
        
        return True, f"Archivo movido exitosamente a {to_category}/{to_resolution or ''}", dest_folder
        
    except Exception as e:
        logger.error(f"Error moving folder: {e}")
        return False, f"Error al mover archivo: {str(e)}", None


def deleteContent(hash: str) -> Tuple[bool, str]:
    """
    Elimina un archivo del filesystem y su tracking.
    
    Args:
        hash: Hash único del archivo (primeros 8 caracteres)
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    # Buscar carpeta por hash
    current_folder = None
    
    for category in ['movies', 'series', 'music', 'others']:
        pattern = os.path.join(MOUNT_PATH, category, "**", f"*{{{hash}}}*")
        matches = glob.glob(pattern, recursive=True)
        
        for match in matches:
            if os.path.isdir(match):
                current_folder = match
                break
        
        if current_folder:
            break
    
    if not current_folder:
        return False, f"No se encontró archivo con hash: {hash}"
    
    try:
        # Eliminar carpeta completa
        shutil.rmtree(current_folder)
        logger.info(f"Deleted folder: {current_folder}")
        
        # Eliminar de tracking
        db = getDatabase("tracking")
        db_lock_tracking = getDatabaseLock("tracking")
        
        if db and db_lock_tracking:
            with db_lock_tracking:
                q = Query()
                db.remove(q.hash == hash)
                logger.debug(f"Removed tracking for {hash}")
        
        return True, "Archivo eliminado exitosamente"
        
    except Exception as e:
        logger.error(f"Error deleting folder: {e}")
        return False, f"Error al eliminar archivo: {str(e)}"


def moveBulk(hashes: List[str], to_category: str, to_resolution: Optional[str] = None) -> Tuple[bool, str, List[str], List[str]]:
    """
    Mueve múltiples archivos a una nueva categoría/resolución.
    
    Args:
        hashes: Lista de hashes únicos
        to_category: Categoría destino
        to_resolution: Resolución destino (solo para movies)
    
    Returns:
        Tuple[bool, str, List[str], List[str]]: (success, message, moved, failed)
    """
    moved = []
    failed = []
    
    for hash in hashes:
        success, msg, new_path = moveContent(hash, to_category, to_resolution)
        if success:
            moved.append(hash)
        else:
            failed.append(hash)
            logger.warning(f"Failed to move {hash}: {msg}")
    
    total = len(hashes)
    moved_count = len(moved)
    failed_count = len(failed)
    
    if moved_count == total:
        return True, f"{moved_count} archivos movidos exitosamente", moved, failed
    elif moved_count > 0:
        return True, f"{moved_count}/{total} archivos movidos, {failed_count} fallaron", moved, failed
    else:
        return False, f"No se pudo mover ningún archivo", moved, failed


def deleteBulk(hashes: List[str]) -> Tuple[bool, str, List[str], List[str]]:
    """
    Elimina múltiples archivos del filesystem.
    
    Args:
        hashes: Lista de hashes únicos
    
    Returns:
        Tuple[bool, str, List[str], List[str]]: (success, message, deleted, failed)
    """
    deleted = []
    failed = []
    
    for hash in hashes:
        success, msg = deleteContent(hash)
        if success:
            deleted.append(hash)
        else:
            failed.append(hash)
            logger.warning(f"Failed to delete {hash}: {msg}")
    
    total = len(hashes)
    deleted_count = len(deleted)
    failed_count = len(failed)
    
    if deleted_count == total:
        return True, f"{deleted_count} archivos eliminados exitosamente", deleted, failed
    elif deleted_count > 0:
        return True, f"{deleted_count}/{total} archivos eliminados, {failed_count} fallaron", deleted, failed
    else:
        return False, f"No se pudo eliminar ningún archivo", deleted, failed


def getStats() -> Dict:
    """
    Obtiene estadísticas de la biblioteca.
    
    Returns:
        Dict con estadísticas
    """
    library = scanLibrary()
    
    total_files = sum(len(files) for files in library.values())
    
    by_category = {cat: len(files) for cat, files in library.items()}
    
    by_resolution = {}
    for file in library['movies']:
        res = file['resolution']
        by_resolution[res] = by_resolution.get(res, 0) + 1
    
    return {
        'total_files': total_files,
        'by_category': by_category,
        'by_resolution': by_resolution
    }
