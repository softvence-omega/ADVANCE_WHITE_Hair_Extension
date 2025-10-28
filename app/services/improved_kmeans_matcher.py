import json
import numpy as np
from pathlib import Path
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

class ImprovedKMeansMatcher:
    def __init__(self):
        shade_path = Path(__file__).parent.parent / "shade" / "kmeans_shade_signatures.json"
        with open(shade_path, 'r') as f:
            self.shades = json.load(f)
    
    def rgb_to_lab(self, rgb):
        """Convert RGB to LAB color space"""
        rgb_normalized = [x / 255.0 for x in rgb]
        rgb_color = sRGBColor(*rgb_normalized)
        return convert_color(rgb_color, LabColor)
    
    def calculate_delta_e(self, rgb1, rgb2):
        """Calculate Delta E (CIEDE2000) between two RGB colors"""
        lab1 = self.rgb_to_lab(rgb1)
        lab2 = self.rgb_to_lab(rgb2)
        return delta_e_cie2000(lab1, lab2)
    
    def match_with_dominant_colors(self, user_colors):
        """Match using multiple detected colors (for balayage/highlights)"""
        results = {}
        
        for shade_name, shade_data in self.shades.items():
            # Compare user's dominant colors with shade's dominant colors
            total_score = 0
            comparisons = 0
            
            # Get top 3 user colors
            user_top_colors = user_colors[:3] if len(user_colors) >= 3 else user_colors
            
            for user_color_data in user_top_colors:
                user_rgb = user_color_data['rgb']
                user_pct = user_color_data.get('percentage', 33.3)
                
                # Find best match among shade's dominant colors
                min_delta = float('inf')
                for shade_color, shade_pct in shade_data['dominant_colors']:
                    delta = self.calculate_delta_e(user_rgb, shade_color)
                    if delta < min_delta:
                        min_delta = delta
                
                # Weight by percentage
                weighted_score = (100 - min_delta) * (user_pct / 100)
                total_score += weighted_score
                comparisons += 1
            
            # Average score
            results[shade_name] = total_score / comparisons if comparisons > 0 else 0
        
        # Sort by best match
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        best_match = sorted_results[0]
        
        return {
            'matched_shade': best_match[0],
            'shade_rgb': self.shades[best_match[0]]['rgb'],
            'confidence_score': round(best_match[1], 2),
            'top_5_matches': [(name, round(score, 2)) for name, score in sorted_results[:5]]
        }
    
    def match_single_color(self, user_rgb):
        """Match a single RGB color using Delta E"""
        best_match = None
        min_delta = float('inf')
        
        for shade_name, shade_data in self.shades.items():
            shade_rgb = shade_data['rgb']
            delta = self.calculate_delta_e(user_rgb, shade_rgb)
            
            if delta < min_delta:
                min_delta = delta
                best_match = {
                    'matched_shade': shade_name,
                    'shade_rgb': shade_rgb,
                    'delta_e': round(delta, 2)
                }
        
        return best_match
