import os
import glob
import logging
from library.app import RAW_MODE
from library.filesystem import MOUNT_PATH
from functions.appFunctions import getAllUserDownloads

def generateFolderPath(data: dict) -> str | None:
    """
    Genera la ruta de carpeta para un download.
    Soporta estructura mejorada con resoluciones.
    """
    from library.app import ENHANCED_FOLDER_STRUCTURE
    
    if RAW_MODE:
        original_path = data.get("path")
        if original_path:
            return os.path.dirname(original_path)
        return None
    
    if not ENHANCED_FOLDER_STRUCTURE:
        # Estructura original
        root_folder = data.get("metadata_rootfoldername", None)
        metadata_foldername = data.get("metadata_foldername", None)
        
        if not root_folder:
            return None
        
        if data.get("metadata_mediatype") == "series":
            if not metadata_foldername:
                return None
            return os.path.join(root_folder, metadata_foldername)
        elif data.get("metadata_mediatype") == "movie":
            return root_folder
        elif data.get("metadata_mediatype") == "anime":
            if not metadata_foldername:
                return None
            return os.path.join(root_folder, metadata_foldername)
        
        return root_folder
    
    # Nueva estructura mejorada
    category = data.get("current_category", "movies")
    root_folder = data.get("metadata_rootfoldername")
    
    if not root_folder:
        return None
    
    # Para películas, agregar subcarpeta de resolución
    if category == "movies":
        resolution_folder = data.get("current_resolution_folder", "unknown")
        folder_path = os.path.join(resolution_folder, root_folder)
    else:
        folder_path = root_folder
    
    # Para series, agregar carpeta de temporada
    if data.get("metadata_mediatype") in ["series", "anime"]:
        metadata_foldername = data.get("metadata_foldername")
        if metadata_foldername:
            folder_path = os.path.join(folder_path, metadata_foldername)
    
    return folder_path

def generateStremFile(file_path: str, url: str, type: str, file_name: str, download=None):
    from library.app import ENHANCED_FOLDER_STRUCTURE
    from functions.trackingFunctions import should_update_strm, update_tracking, getData
    
    # Obtener hash del download (primeros 8 chars del folder_hash)
    torbox_hash = None
    if download:
        folder_hash = download.get("folder_hash", "")
        if folder_hash:
            torbox_hash = folder_hash[:8]
    
    # Verificar si ya existe en tracking y usar ese path
    existing_tracking = None
    if torbox_hash:
        existing_tracking = getData(torbox_hash)
    
    if existing_tracking and existing_tracking.get('last_seen_path'):
        # Usar el path guardado en tracking
        strm_file_path = existing_tracking['last_seen_path']
        full_path = os.path.dirname(strm_file_path)
        logging.debug(f"Using tracked path for {torbox_hash}: {strm_file_path}")
    else:
        # Generar path nuevo (primera vez o no encontrado)
        if RAW_MODE:
            if download:
                original_path = download.get("path")
                if original_path:
                    full_path = os.path.join(MOUNT_PATH, os.path.dirname(original_path))
                else:
                    full_path = os.path.join(MOUNT_PATH, file_path)
            else:
                full_path = os.path.join(MOUNT_PATH, file_path)
        elif ENHANCED_FOLDER_STRUCTURE and download:
            # Nueva estructura con categorías
            category = download.get("current_category", "movies")
            full_path = os.path.join(MOUNT_PATH, category, file_path)
        else:
            # Estructura original
            if type == "movie":
                type = "movies"
            elif type == "series":
                type = "series"
            elif type == "anime":
                type = "series"
            full_path = os.path.join(MOUNT_PATH, type, file_path)
        
        strm_file_path = f"{full_path}/{file_name}.strm"
        logging.debug(f"Generated new path for {torbox_hash}: {strm_file_path}")
    
    # Verificar si necesita actualización
    if torbox_hash and not should_update_strm(torbox_hash, strm_file_path, url):
        logging.debug(f"Skipped strm file (unchanged): {strm_file_path}")
        return True
    
    try:
        os.makedirs(full_path, exist_ok=True)
        with open(strm_file_path, "w") as file:
            file.write(url)
        
        # Actualizar tracking
        if torbox_hash:
            update_tracking(torbox_hash, strm_file_path, url)
        
        logging.debug(f"Created/updated strm file: {strm_file_path}")
        return True
    except FileNotFoundError as e:
        logging.error(f"Error creating strm file (likely bad naming scheme of file): {e}")
        return False
    except OSError as e:
        logging.error(f"Error creating strm file (likely bad or missing permissions): {e}")
        return False
    except Exception as e:
        logging.error(f"Error creating strm file: {e}")
        return False

def ensureFolderStructure():
    """
    Crea la estructura de carpetas base al inicio.
    """
    from library.app import ENHANCED_FOLDER_STRUCTURE
    
    if ENHANCED_FOLDER_STRUCTURE:
        # Estructura mejorada: movies con resoluciones, series, music, others
        base_folders = [
            os.path.join(MOUNT_PATH, "movies"),
            os.path.join(MOUNT_PATH, "series"),
            os.path.join(MOUNT_PATH, "music"),
            os.path.join(MOUNT_PATH, "others"),
        ]
        
        # Subcarpetas de resolución para movies
        resolution_folders = [
            os.path.join(MOUNT_PATH, "movies", "2160"),
            os.path.join(MOUNT_PATH, "movies", "1080"),
            os.path.join(MOUNT_PATH, "movies", "720"),
            os.path.join(MOUNT_PATH, "movies", "480"),
            os.path.join(MOUNT_PATH, "movies", "unknown"),
        ]
        
        all_folders = base_folders + resolution_folders
    else:
        # Estructura original: solo movies y series
        all_folders = [
            os.path.join(MOUNT_PATH, "movies"),
            os.path.join(MOUNT_PATH, "series"),
        ]
    
    # Crear todas las carpetas
    for folder in all_folders:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            logging.info(f"Created folder: {folder}")

def runStrm():
    from functions.trackingFunctions import getData
    
    # Asegurar que la estructura de carpetas existe
    ensureFolderStructure()
    
    all_downloads = getAllUserDownloads()
    
    # Get all existing .strm files
    existing_strm_files = set(glob.glob(os.path.join(MOUNT_PATH, "**", "*.strm"), recursive=True))

    new_strm_files = set()
    for download in all_downloads:
        # Obtener hash del download
        folder_hash = download.get("folder_hash", "")
        torbox_hash = folder_hash[:8] if folder_hash else None
        
        # Verificar si existe en tracking y usar ese path
        if torbox_hash:
            existing_tracking = getData(torbox_hash)
            if existing_tracking and existing_tracking.get('last_seen_path'):
                # Usar el path del tracking (respeta movimientos manuales)
                strm_path = existing_tracking['last_seen_path']
                new_strm_files.add(strm_path)
                # Extraer file_path relativo desde el strm_path completo
                # El strm_path es algo como /torbox/music/folder/file.strm
                # Necesitamos extraer la parte después de /torbox/category/
                relative_path = os.path.relpath(os.path.dirname(strm_path), MOUNT_PATH)
                # Remover la categoría del inicio (movies, series, music, others)
                path_parts = relative_path.split(os.sep)
                if len(path_parts) > 1:
                    file_path = os.path.join(*path_parts[1:])
                else:
                    file_path = ""
                generateStremFile(file_path, download.get("download_link"), download.get("metadata_mediatype"), download.get("metadata_filename"), download)
                continue
        
        # Si no está en tracking, generar path desde metadata
        file_path = generateFolderPath(download)
        if file_path is None:
            continue
        if RAW_MODE:
            strm_path = os.path.join(MOUNT_PATH, file_path, f"{download.get('metadata_filename')}.strm")
        else:
            type = download.get("metadata_mediatype")
            if type == "movie":
                type = "movies"
            elif type == "series":
                type = "series"
            elif type == "anime":
                type = "series"
            strm_path = os.path.join(MOUNT_PATH, type, file_path, f"{download.get('metadata_filename')}.strm")
        new_strm_files.add(strm_path)
        generateStremFile(file_path, download.get("download_link"), download.get("metadata_mediatype"), download.get("metadata_filename"), download)

    # Remove .strm files for deleted downloads
    for strm_file in existing_strm_files:
        if strm_file not in new_strm_files:
            try:
                os.remove(strm_file)
                logging.debug(f"Removed stale .strm file: {strm_file}")
                # Remove empty directories, but preserve folders with metadata/subtitles
                dir = os.path.dirname(strm_file)
                while dir != MOUNT_PATH:
                    try:
                        # Check if directory has any files (metadata, subtitles, NFO, etc.)
                        remaining_files = os.listdir(dir)
                        if not remaining_files:
                            # Completely empty, safe to remove
                            os.rmdir(dir)
                            logging.debug(f"Removed empty directory: {dir}")
                            dir = os.path.dirname(dir)
                        else:
                            # Has other files (metadata, subtitles), preserve it
                            logging.debug(f"Preserving directory with metadata: {dir} ({len(remaining_files)} files)")
                            break
                    except OSError:
                        # Directory not empty or other error, stop cleanup
                        break
            except Exception as e:
                logging.error(f"Error removing .strm file: {e}")

    logging.debug(f"Updated {len(all_downloads)} strm files.")

def unmountStrm():
    """
    Deletes all strm files and any subfolders in the mount path for cleaning up.
    """
    folders = [
        MOUNT_PATH,
        os.path.join(MOUNT_PATH, "movies"),
        os.path.join(MOUNT_PATH, "series"),
    ]
    for folder in folders:
        if os.path.exists(folder):
            logging.debug(f"Folder {folder} already exists. Deleting...")
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                if os.path.isdir(item_path):
                    import shutil
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
