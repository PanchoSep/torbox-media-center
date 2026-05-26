from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import logging
import os
from functions.webFunctions import scanLibrary, moveContent, deleteContent, moveBulk, deleteBulk, getStats
from functions.appFunctions import getAllUserDownloadsFresh

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuración
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

@app.route('/')
def index():
    """Página principal de la interfaz web"""
    return render_template('index.html')

@app.route('/api/library', methods=['GET'])
def get_library():
    """
    GET /api/library
    Retorna todos los archivos organizados por categoría
    """
    try:
        library = scanLibrary()
        stats = getStats()
        
        return jsonify({
            'success': True,
            'library': library,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error getting library: {e}")
        return jsonify({
            'success': False,
            'message': f"Error al obtener biblioteca: {str(e)}"
        }), 500

@app.route('/api/move', methods=['POST'])
def move_file():
    """
    POST /api/move
    Mueve un archivo a una nueva categoría/resolución
    
    Body:
    {
        "hash": "9409c61a",
        "to_category": "series",
        "to_resolution": null
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se recibieron datos'
            }), 400
        
        hash = data.get('hash')
        to_category = data.get('to_category')
        to_resolution = data.get('to_resolution')
        
        if not hash or not to_category:
            return jsonify({
                'success': False,
                'message': 'Faltan parámetros requeridos: hash, to_category'
            }), 400
        
        success, message, new_path = moveContent(hash, to_category, to_resolution)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'new_path': new_path
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"Error moving file: {e}")
        return jsonify({
            'success': False,
            'message': f"Error al mover archivo: {str(e)}"
        }), 500

@app.route('/api/delete', methods=['DELETE'])
def delete_file():
    """
    DELETE /api/delete
    Elimina uno o más archivos
    
    Body:
    {
        "hashes": ["9409c61a", "a0e5c271"]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se recibieron datos'
            }), 400
        
        hashes = data.get('hashes', [])
        
        if not hashes or not isinstance(hashes, list):
            return jsonify({
                'success': False,
                'message': 'Se requiere una lista de hashes'
            }), 400
        
        if len(hashes) == 1:
            # Eliminar un solo archivo
            success, message = deleteContent(hashes[0])
            return jsonify({
                'success': success,
                'message': message,
                'deleted': [hashes[0]] if success else [],
                'failed': [] if success else [hashes[0]]
            })
        else:
            # Eliminar múltiples archivos
            success, message, deleted, failed = deleteBulk(hashes)
            return jsonify({
                'success': success,
                'message': message,
                'deleted': deleted,
                'failed': failed
            })
            
    except Exception as e:
        logger.error(f"Error deleting file(s): {e}")
        return jsonify({
            'success': False,
            'message': f"Error al eliminar archivo(s): {str(e)}"
        }), 500

@app.route('/api/move-bulk', methods=['POST'])
def move_bulk():
    """
    POST /api/move-bulk
    Mueve múltiples archivos a una nueva categoría/resolución
    
    Body:
    {
        "hashes": ["9409c61a", "a0e5c271"],
        "to_category": "series",
        "to_resolution": null
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se recibieron datos'
            }), 400
        
        hashes = data.get('hashes', [])
        to_category = data.get('to_category')
        to_resolution = data.get('to_resolution')
        
        if not hashes or not isinstance(hashes, list):
            return jsonify({
                'success': False,
                'message': 'Se requiere una lista de hashes'
            }), 400
        
        if not to_category:
            return jsonify({
                'success': False,
                'message': 'Falta parámetro requerido: to_category'
            }), 400
        
        success, message, moved, failed = moveBulk(hashes, to_category, to_resolution)
        
        return jsonify({
            'success': success,
            'message': message,
            'moved': moved,
            'failed': failed
        })
            
    except Exception as e:
        logger.error(f"Error moving files: {e}")
        return jsonify({
            'success': False,
            'message': f"Error al mover archivos: {str(e)}"
        }), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_library():
    """
    POST /api/refresh
    Fuerza un refresh manual de la biblioteca
    """
    try:
        logger.info("Manual refresh triggered from web interface")
        user_downloads = getAllUserDownloadsFresh()
        
        # Ejecutar runStrm para actualizar archivos
        from functions.stremFilesystemFunctions import runStrm
        runStrm()
        
        return jsonify({
            'success': True,
            'message': 'Refresh completado exitosamente'
        })
            
    except Exception as e:
        logger.error(f"Error refreshing library: {e}")
        return jsonify({
            'success': False,
            'message': f"Error al refrescar biblioteca: {str(e)}"
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    GET /api/stats
    Retorna estadísticas de la biblioteca
    """
    try:
        stats = getStats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'success': False,
            'message': f"Error al obtener estadísticas: {str(e)}"
        }), 500

def start_web_server(port=5000, host='0.0.0.0'):
    """
    Inicia el servidor web Flask
    
    Args:
        port: Puerto para el servidor (default: 5000)
        host: Host para el servidor (default: 0.0.0.0)
    """
    logger.info(f"Starting web interface on http://{host}:{port}")
    app.run(host=host, port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    start_web_server()
