#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.classificationFunctions import extract_resolution, classify_media_type
from functions.folderNamingFunctions import format_movie_folder, format_series_folder
import PTN

test_cases = [
    "The.Matrix.1999.1080p.BluRay.x264.DTS-FGT.mkv",
    "Inception.2010.2160p.UHD.BluRay.x265.HDR.mkv",
    "Breaking.Bad.S01E01.1080p.WEB-DL.mkv",
    "Game.of.Thrones.S08E06.720p.mkv",
]

print("=" * 80)
print("TEST DE CLASIFICACIÓN Y FORMATEO")
print("=" * 80)

for filename in test_cases:
    print(f"\nArchivo: {filename}")
    print("-" * 80)
    
    parsed = PTN.parse(filename)
    resolution = extract_resolution(filename, parsed)
    media_type = classify_media_type(parsed, 'video/x-matroska')
    
    print(f"Resolución: {resolution}")
    print(f"Tipo: {media_type}")
    
    if media_type == 'movies':
        folder = format_movie_folder(
            title=parsed.get('title', 'Unknown'),
            year=parsed.get('year'),
            resolution=parsed.get('resolution'),
            quality=parsed.get('quality'),
            hash='abc123def456'
        )
        print(f"Carpeta: movies/{resolution}/{folder}/")
    else:
        folder = format_series_folder(
            title=parsed.get('title', 'Unknown'),
            year=parsed.get('year'),
            resolution=parsed.get('resolution'),
            hash='abc123def456'
        )
        print(f"Carpeta: series/{folder}/Season XX/")

print("\n" + "=" * 80)
