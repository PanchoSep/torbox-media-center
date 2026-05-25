from typing import Optional
from functions.mediaFunctions import cleanTitle


def format_movie_folder(title: str, year: Optional[int] = None, resolution: Optional[str] = None, 
                       quality: Optional[str] = None, hash: Optional[str] = None) -> str:
    """
    Formatea nombre de carpeta para película.
    
    Formato: "Title (Year) [Resolution Quality] {Hash}"
    - Movies incluyen tanto resolution como quality en los corchetes
    - El hash se trunca a 8 caracteres para mantener nombres cortos
    
    :param title: Título de la película (no puede estar vacío)
    :param year: Año de lanzamiento
    :param resolution: Resolución (ej: 1080p, 720p, 4K)
    :param quality: Calidad (ej: BluRay, WEB-DL, HDTV)
    :param hash: Hash de Torbox para identificación única
    :return: Nombre de carpeta formateado y sanitizado para filesystem
    :raises ValueError: Si title está vacío
    
    Ejemplo: "The Matrix (1999) [1080p BluRay] {abc123}"
    """
    if not title or not title.strip():
        raise ValueError("title no puede estar vacío")
    
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
    
    Formato: "Title (Year) [Resolution] {Hash}"
    - Series solo incluyen resolution en los corchetes (sin quality)
    - El hash se trunca a 8 caracteres para mantener nombres cortos
    
    :param title: Título de la serie (no puede estar vacío)
    :param year: Año de inicio
    :param resolution: Resolución (ej: 1080p, 720p, 4K)
    :param hash: Hash de Torbox para identificación única
    :return: Nombre de carpeta formateado y sanitizado para filesystem
    :raises ValueError: Si title está vacío
    
    Ejemplo: "Breaking Bad (2008) [1080p] {def456}"
    """
    if not title or not title.strip():
        raise ValueError("title no puede estar vacío")
    
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
