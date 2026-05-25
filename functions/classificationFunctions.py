import PTN
import logging
import re
from typing import Dict, Optional, Tuple

def extract_resolution(filename: str, parsed_data: Dict = None) -> str:
    """Extrae la resolución del nombre de archivo."""
    if parsed_data is None:
        parsed_data = PTN.parse(filename)
    
    resolution = parsed_data.get('resolution', '')
    
    # Mapear resoluciones conocidas
    if '2160' in resolution or '4K' in resolution or 'UHD' in resolution:
        return '2160'
    elif '1080' in resolution:
        return '1080'
    elif '720' in resolution:
        return '720'
    elif '480' in resolution or 'SD' in resolution:
        return '480'
    else:
        # Intentar extraer con regex del filename completo
        if re.search(r'2160p|4K|UHD', filename, re.IGNORECASE):
            return '2160'
        elif re.search(r'1080p', filename, re.IGNORECASE):
            return '1080'
        elif re.search(r'720p', filename, re.IGNORECASE):
            return '720'
        elif re.search(r'480p|SD', filename, re.IGNORECASE):
            return '480'
    
    return 'unknown'

def classify_media_type(parsed_data: Dict, mimetype: str = None) -> str:
    """Clasifica el tipo de media."""
    # Si tiene temporada/episodio, es serie
    if parsed_data.get('season') or parsed_data.get('episode'):
        return 'series'
    
    # Si el mimetype indica audio, es música
    if mimetype and mimetype.startswith('audio/'):
        return 'music'
    
    # Si el mimetype indica video, probablemente es película
    if mimetype and mimetype.startswith('video/'):
        return 'movies'
    
    # Default: others
    return 'others'
