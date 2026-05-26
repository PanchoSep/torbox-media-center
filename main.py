from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from functions.appFunctions import bootUp, getMountMethod, getAllUserDownloadsFresh, getMountRefreshTime
from functions.databaseFunctions import closeAllDatabases
import logging
from sys import platform
import threading
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)

def start_web_interface():
    """Inicia la interfaz web en un thread separado"""
    try:
        web_port = int(os.getenv('WEB_INTERFACE_PORT', '5000'))
        from web.app import start_web_server
        logging.info(f"Starting web interface on port {web_port}")
        start_web_server(port=web_port, host='0.0.0.0')
    except Exception as e:
        logging.error(f"Failed to start web interface: {e}")

if __name__ == "__main__":
    bootUp()
    mount_method = getMountMethod()

    if mount_method == "strm":
        scheduler = BlockingScheduler()
    elif mount_method == "fuse":
        if platform == "win32":
            logging.error("The FUSE mount method is not supported on Windows. Please use the STRM mount method or run this application on a Linux system.")
            exit(1)
        scheduler = BackgroundScheduler()
    else:
        logging.error("Invalid mount method specified.")
        exit(1)

    # Iniciar interfaz web en thread separado (siempre activo)
    web_enabled = os.getenv('WEB_INTERFACE_ENABLED', 'true').lower() == 'true'
    if web_enabled:
        web_thread = threading.Thread(target=start_web_interface, daemon=True, name="WebInterface")
        web_thread.start()
        logging.info("Web interface thread started")

    user_downloads = getAllUserDownloadsFresh()

    scheduler.add_job(
        getAllUserDownloadsFresh,
        "interval",
        hours=getMountRefreshTime(),
        id="get_all_user_downloads_fresh",
    )

    try:
        logging.info("Starting scheduler and mounting...")
        if mount_method == "strm":
            from functions.stremFilesystemFunctions import runStrm
            runStrm()
            scheduler.add_job(
                runStrm,
                "interval",
                minutes=5,
                id="run_strm",
            )
            scheduler.start()
        elif mount_method == "fuse":
            from functions.fuseFilesystemFunctions import runFuse
            scheduler.start()
            runFuse()
    except (KeyboardInterrupt, SystemExit):
        if mount_method == "fuse":
            from functions.fuseFilesystemFunctions import unmountFuse
            unmountFuse()
        elif mount_method == "strm":
            from functions.stremFilesystemFunctions import unmountStrm
            unmountStrm()
        closeAllDatabases()
        exit(0)