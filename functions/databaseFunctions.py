from tinydb import TinyDB
import threading
import logging

db_connections = {}
db_locks = {}
global_lock = threading.Lock()

def getDatabase(name: str = "db"):
    """
    Returns the TinyDB database instance with thread-safe storage.
    Uses a connection pool pattern to avoid creating multiple connections.
    """
    global db_connections, db_locks # global cause I'm lazy
    
    with global_lock:
        if name not in db_connections:
            try:
                db_connections[name] = TinyDB(f"{name}.json")
                db_locks[name] = threading.Lock()
            except Exception as e:
                logging.error(f"Error connecting to the database: {e}")
                return None
    
    return db_connections[name]

def getDatabaseLock(name: str = "db"):
    """
    Returns the lock for the specified database.
    """
    global db_locks
    
    getDatabase(name)
    return db_locks.get(name)

def clearDatabase(type: str):
    """
    Clears the entire database with thread safety.
    """
    db = getDatabase(type)
    db_lock = getDatabaseLock(type)
    
    if db is None or db_lock is None:
        return False, "Database connection failed."
    
    with db_lock:
        try:
            db.truncate()
            return True, "Database cleared successfully."
        except Exception as e:
            return False, f"Error clearing the database: {e}"
    
def insertData(data: dict, type: str):
    """
    Inserts data into the database with thread safety.
    
    Expected fields for media tracking (all optional):
    - current_category: str - Current category (movies, series, music, others). None if not determined yet.
    - current_resolution_folder: str - Current resolution folder (2160, 1080, 720, 480, unknown, None)
    - manual_override: bool - True if user manually moved the file, False if moved automatically
    - last_seen_path: str - Last physical path detected for the file
    """
    db = getDatabase(type)
    db_lock = getDatabaseLock(type)
    
    if db is None or db_lock is None:
        return False, "Database connection failed."
    
    with db_lock:
        try:
            db.insert(data)
            return True, "Data inserted successfully."
        except Exception as e:
            return False, f"Error inserting data. {e}"

def updateData(data: dict, type: str):
    """
    Updates data in the database with thread safety.
    Uses folder_hash as the unique identifier.
    
    Args:
        data: Dictionary containing the data to update (must include 'folder_hash')
        type: Database type (e.g., 'db', 'tracking')
    
    Returns:
        tuple: (success: bool, message: str)
    """
    from tinydb import Query
    
    db = getDatabase(type)
    db_lock = getDatabaseLock(type)
    
    if db is None or db_lock is None:
        return False, "Database connection failed."
    
    folder_hash = data.get('folder_hash')
    if not folder_hash:
        return False, "folder_hash is required for update"
    
    with db_lock:
        try:
            q = Query()
            result = db.update(data, q.folder_hash == folder_hash)
            if result:
                return True, f"Data updated successfully ({result} records)."
            else:
                return False, "No matching record found to update."
        except Exception as e:
            return False, f"Error updating data: {e}"
    
def getAllData(type: str):
    """
    Retrieves all data from the database with thread safety.
    """
    db = getDatabase(type)
    db_lock = getDatabaseLock(type)
    
    if db is None or db_lock is None:
        return None, False, "Database connection failed."
    
    with db_lock:
        try:
            data = db.all()
            return data, True, "Data retrieved successfully."
        except Exception as e:
            return None, False, f"Error retrieving data. {e}"

def closeDatabase(name: str = "db"):
    """
    Closes a database connection and removes it from the cache.
    """
    global db_connections, db_locks
    
    with global_lock:
        if name in db_connections:
            try:
                db_connections[name].close()
                del db_connections[name]
                del db_locks[name]
                return True, "Database closed successfully."
            except Exception as e:
                return False, f"Error closing database: {e}"
        return True, "Database was not open."

def closeAllDatabases():
    """
    Closes all database connections.
    """
    global db_connections, db_locks
    
    with global_lock:
        closed_count = 0
        for name in list(db_connections.keys()):
            try:
                db_connections[name].close()
                closed_count += 1
            except Exception as e:
                logging.error(f"Error closing database {name}: {e}")
        
        db_connections.clear()
        db_locks.clear()
        return True, f"Closed {closed_count} database connections."