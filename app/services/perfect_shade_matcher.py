"""
Perfect Shade Matcher - Accurate matching for all hair colors
Uses Lab color space + RGB distance + smart weighting
"""
import numpy as np

def rgb_to_lab(rgb):
    """Convert RGB to Lab color space"""
    r, g, b = [x / 255.0 for x in rgb]
    
    # RGB to XYZ
    r = ((r + 0.055) / 1.055) ** 2.4 if r > 0.04045 else r / 12.92
    g = ((g + 0.055) / 1.055) ** 2.4 if g > 0.04045 else g / 12.92
    b = ((b + 0.055) / 1.055) ** 2.4 if b > 0.04045 else b / 12.92
    
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505
    
    # XYZ to Lab
    x, y, z = x / 0.95047, y / 1.00000, z / 1.08883
    x = x ** (1/3) if x > 0.008856 else (7.787 * x) + (16/116)
    y = y ** (1/3) if y > 0.008856 else (7.787 * y) + (16/116)
    z = z ** (1/3) if z > 0.008856 else (7.787 * z) + (16/116)
    
    L = (116 * y) - 16
    a = 500 * (x - y)
    b = 200 * (y - z)
    
    return [L, a, b]

def calculate_color_distance(user_color, shade_color):
    """Calculate Delta E distance between two colors"""
    lab1 = rgb_to_lab(user_color)
    lab2 = rgb_to_lab(shade_color)
    
    dL = lab1[0] - lab2[0]
    da = lab1[1] - lab2[1]
    db = lab1[2] - lab2[2]
    
    return np.sqrt(dL**2 + da**2 + db**2)

def match_colors(user_colors, shade_colors):
    """Match user colors to shade colors with smart weighting"""
    
    total_score = 0
    
    # Sort user colors by percentage (dominant first)
    user_colors_sorted = sorted(user_colors, key=lambda x: x['percentage'], reverse=True)
    
    for user_color in user_colors_sorted:
        user_rgb = user_color.get("color", user_color.get("rgb", [0, 0, 0]))
        user_pct = user_color["percentage"]
        
        # Find best matching shade color
        best_distance = float('inf')
        
        for shade_color in shade_colors:
            shade_rgb = shade_color.get("color", shade_color.get("rgb", [0, 0, 0]))
            
            # Calculate Delta E distance
            distance = calculate_color_distance(user_rgb, shade_rgb)
            
            if distance < best_distance:
                best_distance = distance
        
        # Convert distance to score (lower distance = higher score)
        if best_distance < 5:
            color_score = 100
        elif best_distance < 10:
            color_score = 95
        elif best_distance < 15:
            color_score = 90
        elif best_distance < 20:
            color_score = 85
        elif best_distance < 30:
            color_score = 75
        elif best_distance < 40:
            color_score = 65
        elif best_distance < 50:
            color_score = 50
        else:
            color_score = max(0, 40 - (best_distance - 50) * 0.5)
        
        # Weight by percentage
        total_score += color_score * (user_pct / 100)
    
    return round(total_score, 2)

def find_perfect_match(user_colors, reference_shades):
    """Find the best matching shade"""
    
    scores = {}
    
    # Calculate score for each shade
    for shade_name, shade_colors in reference_shades.items():
        score = match_colors(user_colors, shade_colors)
        scores[shade_name] = score
    
    # Sort by score
    sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    
    # Get best match
    best_match = next(iter(sorted_scores)) if sorted_scores else None
    
    # Get base shade name (without variant)
    best_base = None
    if best_match and "_" in best_match:
        best_base = best_match.split("_")[0]
    
    return best_match, sorted_scores, best_base
