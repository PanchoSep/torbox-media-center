import logging
from typing import Optional
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
