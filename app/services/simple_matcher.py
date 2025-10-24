"""
Simple and Accurate Matcher
- Direct RGB comparison
- Weighted by percentage
- No complex logic
"""
import numpy as np

def calculate_rgb_distance(rgb1, rgb2):
    """Simple Euclidean distance"""
    return np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

def simple_match(user_colors, shade_colors):
    """Simple matching - just compare colors"""
    
    total_score = 0
    
    # Compare each user color with all shade colors
    for user_color in user_colors:
        user_rgb = user_color.get("color", user_color.get("rgb", [0, 0, 0]))
        user_pct = user_color["percentage"]
        
        best_distance = float('inf')
        
        # Find closest shade color
        for shade_color in shade_colors:
            shade_rgb = shade_color.get("color", shade_color.get("rgb", [0, 0, 0]))
            
            distance = calculate_rgb_distance(user_rgb, shade_rgb)
            
            if distance < best_distance:
                best_distance = distance
        
        # Convert distance to score (0-100)
        if best_distance < 10:
            color_score = 100
        elif best_distance < 20:
            color_score = 95
        elif best_distance < 30:
            color_score = 85
        elif best_distance < 50:
            color_score = 70
        elif best_distance < 80:
            color_score = 50
        else:
            color_score = max(0, 30 - (best_distance - 80) * 0.3)
        
        # Weight by percentage
        total_score += color_score * (user_pct / 100)
    
    return round(total_score, 2)

def find_simple_match(user_colors, reference_shades):
    """Find best match using simple method"""
    scores = {}
    variant_scores = {}
    
    for shade_name, shade_colors in reference_shades.items():
        score = simple_match(user_colors, shade_colors)
        scores[shade_name] = score
        
        # Track variants
        if "_" in shade_name:
            base = shade_name.split("_")[0]
            variant = shade_name.replace(base + "_", "")
            
            if base not in variant_scores:
                variant_scores[base] = {}
            variant_scores[base][variant] = score
        else:
            variant_scores[shade_name] = {"main": score}
    
    sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    best_match = next(iter(sorted_scores)) if sorted_scores else None
    
    # Best variant
    best_variant = None
    if best_match and "_" in best_match:
        base = best_match.split("_")[0]
        if base in variant_scores:
            best_var = max(variant_scores[base], key=variant_scores[base].get)
            best_variant = f"{base}_{best_var}"
    
    return best_match, sorted_scores, best_variant, variant_scores
