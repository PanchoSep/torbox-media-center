import PTN
import logging
import re
from typing import Dict, Optional, Tuple

# Configurar logger
logger = logging.getLogger(__name__)

# Constantes para tipos de media
MEDIA_TYPE_SERIES = 'series'
MEDIA_TYPE_MOVIES = 'movies'
MEDIA_TYPE_MUSIC = 'music'
MEDIA_TYPE_OTHERS = 'others'

# Constantes para resoluciones
RESOLUTION_2160 = '2160'
RESOLUTION_1080 = '1080'
RESOLUTION_720 = '720'
RESOLUTION_480 = '480'
RESOLUTION_UNKNOWN = 'unknown'


def extract_resolution(filename: str, parsed_data: Dict = None) -> str:
    """
    Extrae la resolución del nombre de archivo.
    
    Args:
        filename: Nombre del archivo a analizar
        parsed_data: Datos ya parseados por PTN (opcional, se parseará si no se provee)
    
    Returns:
        str: Resolución detectada ('2160', '1080', '720', '480', 'unknown')
    
    Examples:
        >>> extract_resolution('Movie.2023.1080p.BluRay.mkv')
        '1080'
        >>> extract_resolution('Series.S01E01.720p.WEB-DL.mkv')
        '720'
    
    Note:
        Si no se puede determinar la resolución, retorna 'unknown'.
    """
    if parsed_data is None:
        try:
            parsed_data = PTN.parse(filename)
        except Exception as e:
            logger.warning(f"Error parsing filename '{filename}': {e}")
            parsed_data = {}
    
    resolution = parsed_data.get('resolution', '')
    
    # Mapear resoluciones conocidas
    if '2160' in resolution or '4K' in resolution or 'UHD' in resolution:
        return RESOLUTION_2160
    elif '1080' in resolution:
        return RESOLUTION_1080
    elif '720' in resolution:
        return RESOLUTION_720
    elif '480' in resolution or 'SD' in resolution:
        return RESOLUTION_480
    else:
        # Intentar extraer con regex del filename completo
        if re.search(r'2160p|4K|UHD', filename, re.IGNORECASE):
            return RESOLUTION_2160
        elif re.search(r'1080p', filename, re.IGNORECASE):
            return RESOLUTION_1080
        elif re.search(r'720p', filename, re.IGNORECASE):
            return RESOLUTION_720
        elif re.search(r'480p|SD', filename, re.IGNORECASE):
            return RESOLUTION_480
    
    logger.info(f"Could not determine resolution for '{filename}', returning 'unknown'")
    return RESOLUTION_UNKNOWN


def classify_media_type(parsed_data: Dict, mimetype: str = None) -> str:
    """
    Clasifica el tipo de media basándose en datos parseados y mimetype.
    
    Args:
        parsed_data: Diccionario con datos parseados del nombre de archivo
        mimetype: Tipo MIME del archivo (opcional)
    
    Returns:
        str: Tipo de media ('series', 'movies', 'music', 'others')
    
    Examples:
        >>> classify_media_type({'season': 1, 'episode': 1})
        'series'
        >>> classify_media_type({'title': 'Movie'}, 'video/mp4')
        'movies'
    
    Note:
        Esta es una clasificación simplista basada en heurísticas básicas:
        - Presencia de season/episode indica serie
        - Mimetype audio/* indica música
        - Mimetype video/* sin season/episode indica película
        - Todo lo demás se clasifica como 'others'
        
        Para clasificación más precisa, considerar usar APIs externas
        (TMDB, TVDB, etc.) o análisis más sofisticado del contenido.
    """
    # Si tiene temporada/episodio, es serie
    if parsed_data.get('season') or parsed_data.get('episode'):
        return MEDIA_TYPE_SERIES
    
    # Si el mimetype indica audio, es música
    if mimetype and mimetype.startswith('audio/'):
        logger.debug(f"Classified as music based on mimetype: {mimetype}")
        return MEDIA_TYPE_MUSIC
    
    # Si el mimetype indica video, probablemente es película
    if mimetype and mimetype.startswith('video/'):
        logger.debug(f"Classified as movie based on mimetype: {mimetype}")
        return MEDIA_TYPE_MOVIES
    
    # Default: others
    logger.info(f"Could not classify media type, defaulting to 'others'. Parsed data: {parsed_data}, mimetype: {mimetype}")
    return MEDIA_TYPE_OTHERS
