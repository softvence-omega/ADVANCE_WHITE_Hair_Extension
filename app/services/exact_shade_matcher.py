import json
import numpy as np
from pathlib import Path

class ExactShadeMatcher:
    def __init__(self):
        shade_path = Path(__file__).parent.parent / "shade" / "exact_shade_signatures.json"
        with open(shade_path, 'r') as f:
            self.shades = json.load(f)
    
    def euclidean_distance(self, c1, c2):
        return np.linalg.norm(np.array(c1) - np.array(c2))
    
    def match_shade(self, user_colors):
        results = []
        
        for file_name, shade_data in self.shades.items():
            min_dist = float('inf')
            
            for user_color in user_colors:
                user_rgb = user_color['rgb']
                for shade_color in shade_data['dominant_colors']:
                    shade_rgb = shade_color['rgb']
                    dist = self.euclidean_distance(user_rgb, shade_rgb)
                    min_dist = min(min_dist, dist)
            
            results.append({
                'file_name': file_name,
                'shade_name': shade_data['shade_name'],
                'distance': round(min_dist, 2)
            })
        
        sorted_results = sorted(results, key=lambda x: x['distance'])
        best = sorted_results[0]
        
        return {
            'matched_file': best['file_name'],
            'matched_shade': best['shade_name'],
            'distance': best['distance'],
            'top_5': sorted_results[:5]
        }
