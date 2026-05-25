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
    
    try:
        os.makedirs(full_path, exist_ok=True)
        with open(f"{full_path}/{file_name}.strm", "w") as file:
            file.write(url)
        logging.debug(f"Created strm file: {full_path}/{file_name}.strm")
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

def runStrm():
    from library.app import ENHANCED_FOLDER_STRUCTURE, FORCE_RECLASSIFY
    from functions.trackingFunctions import scan_current_locations, detect_manual_changes
    from functions.databaseFunctions import updateData
    
    all_downloads = getAllUserDownloads()
    
    # Detectar cambios manuales si no estamos forzando reclasificación
    if ENHANCED_FOLDER_STRUCTURE and not FORCE_RECLASSIFY:
        current_locations = scan_current_locations()
        changes = detect_manual_changes(all_downloads, current_locations)
        
        # Aplicar cambios detectados
        for change in changes:
            record = change['record']
            record['current_category'] = change['new_category']
            record['current_resolution_folder'] = change['new_resolution']
            record['manual_override'] = True
            
            # Actualizar en DB
            updateData(record, record.get('type'))
    
    # Get all existing .strm files
    existing_strm_files = set(glob.glob(os.path.join(MOUNT_PATH, "**", "*.strm"), recursive=True))

    new_strm_files = set()
    for download in all_downloads:
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
                # Remove empty directories
                dir = os.path.dirname(strm_file)
                while dir != MOUNT_PATH and not os.listdir(dir):
                    os.rmdir(dir)
                    dir = os.path.dirname(dir)
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
