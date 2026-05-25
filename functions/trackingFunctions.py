import logging
from typing import Optional, Dict, List
from tinydb import Query
from functions.databaseFunctions import getDatabase, getDatabaseLock

logger = logging.getLogger(__name__)

def getData(torbox_hash: str, db_type: str = "tracking") -> Optional[dict]:
    """
    Retrieves a single record by hash from the database.
    
    Args:
        torbox_hash: Hash único del torrent en Torbox
        db_type: Tipo de base de datos (default: "tracking")
    
    Returns:
        Dictionary con los datos del registro o None si no existe
    """
    db = getDatabase(db_type)
    db_lock = getDatabaseLock(db_type)
    
    if db is None or db_lock is None:
        logger.error(f"Database connection failed for {db_type}")
        return None
    
    with db_lock:
        try:
            q = Query()
            results = db.search(q.hash == torbox_hash)
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error searching database: {e}")
            return None

def detect_manual_move(torbox_hash: str, current_path: str) -> bool:
    """
    Detecta si el usuario movió manualmente un archivo.
    
    Args:
        torbox_hash: Hash único del torrent en Torbox
        current_path: Ruta actual del archivo en el filesystem
    
    Returns:
        True si el archivo fue movido manualmente, False en caso contrario
    """
    # Buscar registro existente
    existing = getData(torbox_hash)
    
    if not existing:
        # Primera vez que vemos este archivo
        logger.debug(f"No tracking record for {torbox_hash}, assuming first run")
        return False
    
    last_seen = existing.get('last_seen_path')
    
    if not last_seen:
        # No hay registro de ubicación previa
        return False
    
    if last_seen == current_path:
        # El archivo está donde lo dejamos
        return False
    
    # El archivo se movió desde la última vez
    logger.info(f"Manual move detected for {torbox_hash}: {last_seen} -> {current_path}")
    return True

def update_tracking(torbox_hash: str, category: str, resolution_folder: Optional[str], 
                   current_path: str, manual_override: bool = False) -> tuple[bool, str]:
    """
    Actualiza el tracking de un archivo en la base de datos.
    
    Args:
        torbox_hash: Hash único del torrent
        category: Categoría (movies, series, music, others)
        resolution_folder: Carpeta de resolución (2160, 1080, 720, 480, unknown, None)
        current_path: Ruta actual del archivo
        manual_override: Si True, marca que el usuario movió el archivo manualmente
    
    Returns:
        tuple[bool, str]: (success, message)
    """
    # Validar parámetros
    if not torbox_hash or not isinstance(torbox_hash, str):
        return False, "Invalid torbox_hash parameter"
    
    if not category or category not in ['movies', 'series', 'music', 'others']:
        return False, f"Invalid category: {category}"
    
    if not current_path or not isinstance(current_path, str):
        return False, "Invalid current_path parameter"
    
    db = getDatabase("tracking")
    db_lock = getDatabaseLock("tracking")
    
    if db is None or db_lock is None:
        return False, "Database connection failed"
    
    data = {
        'hash': torbox_hash,
        'current_category': category,
        'current_resolution_folder': resolution_folder,
        'last_seen_path': current_path,
        'manual_override': manual_override
    }
    
    with db_lock:
        try:
            q = Query()
            existing = db.search(q.hash == torbox_hash)
            
            if existing:
                # Actualizar registro existente
                db.update(data, q.hash == torbox_hash)
                logger.debug(f"Updated tracking for {torbox_hash}: {category}/{resolution_folder}")
                return True, "Tracking updated successfully"
            else:
                # Insertar nuevo registro
                db.insert(data)
                logger.debug(f"Inserted tracking for {torbox_hash}: {category}/{resolution_folder}")
                return True, "Tracking inserted successfully"
        except Exception as e:
            logger.error(f"Failed to update tracking for {torbox_hash}: {e}")
            return False, f"Error updating tracking: {e}"

def scan_current_locations() -> Dict[str, Dict]:
    """
    Escanea el filesystem y retorna ubicaciones actuales de archivos .strm
    
    Returns:
        Dict con hash como key y info de ubicación como value
    """
    import os
    import glob
    import re
    from library.filesystem import MOUNT_PATH
    
    locations = {}
    
    # Buscar todos los .strm recursivamente
    strm_files = glob.glob(os.path.join(MOUNT_PATH, "**", "*.strm"), recursive=True)
    
    for strm_path in strm_files:
        # Extraer información de la ruta
        rel_path = os.path.relpath(strm_path, MOUNT_PATH)
        parts = rel_path.split(os.sep)
        
        if len(parts) < 2:
            continue
        
        category = parts[0]  # movies, series, music, others
        
        # Extraer hash del nombre de carpeta
        folder_name = parts[-2] if len(parts) > 1 else None
        hash_match = None
        if folder_name:
            match = re.search(r'\{([a-f0-9]+)\}', folder_name)
            if match:
                hash_match = match.group(1)
        
        if hash_match:
            resolution_folder = None
            if category == 'movies' and len(parts) >= 3:
                resolution_folder = parts[1]  # 2160, 1080, etc.
            
            locations[hash_match] = {
                'path': strm_path,
                'category': category,
                'resolution_folder': resolution_folder,
                'folder_name': folder_name,
            }
    
    return locations

def detect_manual_changes(db_data: List[Dict], current_locations: Dict) -> List[Dict]:
    """
    Detecta cambios manuales comparando DB con filesystem actual.
    
    Args:
        db_data: Lista de registros de la base de datos
        current_locations: Dict de ubicaciones actuales del filesystem
        
    Returns:
        Lista de registros que necesitan actualización
    """
    changes = []
    
    for record in db_data:
        hash = record.get('folder_hash', '')[:8]  # Primeros 8 chars
        
        if not hash:
            continue
        
        # Ubicación esperada según DB
        db_category = record.get('current_category', 'movies')
        db_resolution = record.get('current_resolution_folder')
        
        # Ubicación actual en filesystem
        current = current_locations.get(hash)
        
        if not current:
            # Archivo no encontrado, podría estar eliminado
            continue
        
        # Comparar ubicaciones
        if (current['category'] != db_category or 
            current['resolution_folder'] != db_resolution):
            
            logger.info(f"Cambio manual detectado para {hash}: "
                        f"{db_category}/{db_resolution} -> "
                        f"{current['category']}/{current['resolution_folder']}")
            
            changes.append({
                'record': record,
                'new_category': current['category'],
                'new_resolution': current['resolution_folder'],
                'manual_override': True,
            })
    
    return changes
