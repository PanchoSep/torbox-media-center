import logging
from typing import Optional

def format_movie_folder(title: str, year: Optional[int] = None, resolution: Optional[str] = None, 
                       quality: Optional[str] = None, hash: Optional[str] = None) -> str:
    """
    Formatea nombre de carpeta para película.
    
    :param title: Título de la película
    :param year: Año de lanzamiento
    :param resolution: Resolución (ej: 1080p, 720p, 4K)
    :param quality: Calidad (ej: BluRay, WEB-DL, HDTV)
    :param hash: Hash de Torbox para identificación única
    :return: Nombre de carpeta formateado
    
    Ejemplo: "The Matrix (1999) [1080p BluRay] {abc123}"
    """
    from functions.mediaFunctions import cleanTitle
    
    parts = [title]
    
    if year:
        parts.append(f"({year})")
    
    # Metadata técnica
    tech_parts = []
    if resolution:
        tech_parts.append(resolution)
    if quality:
        tech_parts.append(quality)
    
    if tech_parts:
        parts.append(f"[{' '.join(tech_parts)}]")
    
    # Agregar hash al final
    if hash:
        short_hash = hash[:8] if len(hash) > 8 else hash
        parts.append(f"{{{short_hash}}}")
    
    folder_name = " ".join(parts)
    folder_name = cleanTitle(folder_name)
    
    return folder_name

def format_series_folder(title: str, year: Optional[int] = None, resolution: Optional[str] = None,
                        hash: Optional[str] = None) -> str:
    """
    Formatea nombre de carpeta para serie.
    
    :param title: Título de la serie
    :param year: Año de inicio
    :param resolution: Resolución (ej: 1080p, 720p, 4K)
    :param hash: Hash de Torbox para identificación única
    :return: Nombre de carpeta formateado
    
    Ejemplo: "Breaking Bad (2008) [1080p] {def456}"
    """
    from functions.mediaFunctions import cleanTitle
    
    parts = [title]
    
    if year:
        parts.append(f"({year})")
    
    if resolution:
        parts.append(f"[{resolution}]")
    
    if hash:
        short_hash = hash[:8] if len(hash) > 8 else hash
        parts.append(f"{{{short_hash}}}")
    
    folder_name = " ".join(parts)
    folder_name = cleanTitle(folder_name)
    
    return folder_name
