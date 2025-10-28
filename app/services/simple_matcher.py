"""
Simple and Effective Shade Matcher
"""
import numpy as np

def lab_distance(lab1, lab2):
    """Calculate color distance in Lab space"""
    dL = lab1[0] - lab2[0]
    da = lab1[1] - lab2[1]
    db = lab1[2] - lab2[2]
    return np.sqrt(dL**2 + da**2 + db**2)

def match_shade(user_colors, shade_colors):
    """Match user colors to shade colors"""
    total_score = 0
    
    for user_color in user_colors:
        user_lab = user_color["lab"]
        user_pct = user_color["percentage"]
        
        # Find closest shade color
        min_distance = float('inf')
        for shade_color in shade_colors:
            shade_lab = shade_color["lab"]
            distance = lab_distance(user_lab, shade_lab)
            if distance < min_distance:
                min_distance = distance
        
        # Convert distance to score (closer = higher score)
        if min_distance < 10:
            color_score = 100
        elif min_distance < 20:
            color_score = 95
        elif min_distance < 30:
            color_score = 85
        elif min_distance < 40:
            color_score = 75
        elif min_distance < 50:
            color_score = 65
        else:
            color_score = max(0, 60 - (min_distance - 50) * 0.5)
        
        total_score += color_score * (user_pct / 100)
    
    return round(total_score, 2)

def find_best_match(user_colors, reference_shades):
    """Find best matching shade"""
    scores = {}
    
    for shade_name, shade_colors in reference_shades.items():
        scores[shade_name] = match_shade(user_colors, shade_colors)
    
    # Sort by score
    sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    best_match = next(iter(sorted_scores)) if sorted_scores else None
    
    return best_match, sorted_scores
