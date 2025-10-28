import json
import numpy as np
from pathlib import Path

class EuclideanMatcher:
    def __init__(self):
        shade_path = Path(__file__).parent.parent / "shade" / "kmeans_shade_signatures.json"
        with open(shade_path, 'r') as f:
            self.shades = json.load(f)
    
    def euclidean_distance(self, c1, c2):
        return np.linalg.norm(np.array(c1) - np.array(c2))
    
    def match_shade(self, user_colors):
        results = {}
        
        for shade_name, shade_data in self.shades.items():
            all_distances = []
            
            for user_color in user_colors:
                user_rgb = user_color['rgb']
                for shade_rgb in shade_data['dominant_colors']:
                    all_distances.append(self.euclidean_distance(user_rgb, shade_rgb))
            
            results[shade_name] = min(all_distances)
        
        sorted_results = sorted(results.items(), key=lambda x: x[1])
        
        return {
            'matched_shade': sorted_results[0][0],
            'distance': round(sorted_results[0][1], 2),
            'top_5': [(name, round(dist, 2)) for name, dist in sorted_results[:5]]
        }
