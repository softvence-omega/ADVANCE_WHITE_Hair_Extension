import json
import numpy as np
from pathlib import Path

class KMeansShadeMatche:
    def __init__(self):
        shade_path = Path(__file__).parent.parent / "shade" / "kmeans_shade_signatures.json"
        with open(shade_path, 'r') as f:
            self.shades = json.load(f)
    
    def euclidean_distance(self, color1, color2):
        """Calculate Euclidean distance between two RGB colors"""
        return np.linalg.norm(np.array(color1) - np.array(color2))
    
    def match_shade(self, user_rgb):
        """Find the closest matching shade using Euclidean distance"""
        best_match = None
        min_distance = float('inf')
        
        for shade_name, shade_data in self.shades.items():
            shade_rgb = shade_data['rgb']
            distance = self.euclidean_distance(user_rgb, shade_rgb)
            
            if distance < min_distance:
                min_distance = distance
                best_match = {
                    'shade_name': shade_name,
                    'shade_rgb': shade_rgb,
                    'distance': round(distance, 2),
                    'dominant_colors': shade_data['dominant_colors']
                }
        
        return best_match
