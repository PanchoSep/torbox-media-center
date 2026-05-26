import logging
import os
from typing import Optional, Dict
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

def update_tracking(torbox_hash: str, strm_path: str, strm_content: str) -> tuple[bool, str]:
    """
    Actualiza el tracking de un archivo en la base de datos.
    Solo actualiza si el contenido del .strm cambió.
    
    Args:
        torbox_hash: Hash único del torrent (primeros 8 chars)
        strm_path: Ruta completa del archivo .strm
        strm_content: Contenido del archivo .strm
    
    Returns:
        tuple[bool, str]: (success, message)
    """
    import time
    
    # Validar parámetros
    if not torbox_hash or not isinstance(torbox_hash, str):
        return False, "Invalid torbox_hash parameter"
    
    if not strm_path or not isinstance(strm_path, str):
        return False, "Invalid strm_path parameter"
    
    if not strm_content or not isinstance(strm_content, str):
        return False, "Invalid strm_content parameter"
    
    db = getDatabase("tracking")
    db_lock = getDatabaseLock("tracking")
    
    if db is None or db_lock is None:
        return False, "Database connection failed"
    
    with db_lock:
        try:
            q = Query()
            existing = db.search(q.hash == torbox_hash)
            
            if existing:
                # Registro existe - comparar contenido
                old_content = existing[0].get('strm_content', '')
                old_path = existing[0].get('last_seen_path', '')
                
                # Solo actualizar si cambió el contenido o el path
                if old_content != strm_content or old_path != strm_path:
                    data = {
                        'hash': torbox_hash,
                        'last_seen_path': strm_path,
                        'strm_content': strm_content,
                        'added_at': existing[0].get('added_at', time.time()),
                        'updated_at': time.time()
                    }
                    db.update(data, q.hash == torbox_hash)
                    logger.debug(f"Updated tracking for {torbox_hash}: content or path changed")
                    return True, "Tracking updated (content/path changed)"
                else:
                    # No cambió nada, skip update
                    logger.debug(f"Skipped update for {torbox_hash}: content unchanged")
                    return True, "Tracking unchanged (skipped)"
            else:
                # Nuevo registro
                data = {
                    'hash': torbox_hash,
                    'last_seen_path': strm_path,
                    'strm_content': strm_content,
                    'added_at': time.time(),
                    'updated_at': time.time()
                }
                db.insert(data)
                logger.debug(f"Inserted tracking for {torbox_hash}")
                return True, "Tracking inserted successfully"
        except Exception as e:
            logger.error(f"Failed to update tracking for {torbox_hash}: {e}")
            return False, f"Error updating tracking: {e}"

def read_strm_content(strm_path: str) -> Optional[str]:
    """
    Lee el contenido de un archivo .strm
    
    Args:
        strm_path: Ruta completa al archivo .strm
    
    Returns:
        Contenido del archivo o None si hay error
    """
    try:
        if os.path.exists(strm_path):
            with open(strm_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        return None
    except Exception as e:
        logger.error(f"Error reading {strm_path}: {e}")
        return None

def should_update_strm(torbox_hash: str, strm_path: str, new_content: str) -> bool:
    """
    Determina si un archivo .strm necesita ser actualizado.
    
    Args:
        torbox_hash: Hash del torrent
        strm_path: Ruta del archivo .strm
        new_content: Nuevo contenido a escribir
    
    Returns:
        True si debe actualizarse, False si no
    """
    # Buscar en tracking
    existing = getData(torbox_hash)
    
    if not existing:
        # Primera vez, debe crearse
        return True
    
    # Comparar contenido guardado con el nuevo
    old_content = existing.get('strm_content', '')
    
    if old_content != new_content:
        logger.info(f"Content changed for {torbox_hash}, will update")
        return True
    
    # Verificar si el archivo existe físicamente
    if not os.path.exists(strm_path):
        logger.info(f"File missing for {torbox_hash}, will recreate")
        return True
    
    # Archivo existe y contenido no cambió
    return False
