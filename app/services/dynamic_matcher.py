"""
Dynamic Shade Matcher - Pure color science, no hardcoded rules
"""
import numpy as np

def lab_distance(lab1, lab2):
    """Delta E distance"""
    dL = lab1[0] - lab2[0]
    da = lab1[1] - lab2[1]
    db = lab1[2] - lab2[2]
    return np.sqrt(dL**2 + da**2 + db**2)

def color_distribution_similarity(user_colors, shade_colors):
    """Compare color distributions using percentages"""
    # Sort by brightness
    user_sorted = sorted(user_colors, key=lambda x: x["brightness"])
    shade_sorted = sorted(shade_colors, key=lambda x: x["brightness"])
    
    # Compare darkest to darkest, lightest to lightest
    total_score = 0
    comparisons = min(len(user_sorted), len(shade_sorted))
    
    for i in range(comparisons):
        user_c = user_sorted[i]
        shade_c = shade_sorted[i]
        
        # Lab distance
        dist = lab_distance(user_c["lab"], shade_c["lab"])
        
        # Convert distance to score (0-100)
        if dist < 10:
            score = 100
        elif dist < 20:
            score = 95 - (dist - 10) * 0.5
        elif dist < 40:
            score = 90 - (dist - 20) * 1.0
        else:
            score = max(0, 70 - (dist - 40) * 0.5)
        
        # Weight by percentage
        weight = (user_c["percentage"] + shade_c["percentage"]) / 200
        total_score += score * weight
    
    return total_score

def brightness_profile_match(user_colors, shade_colors):
    """Match brightness distribution pattern"""
    # Get brightness stats
    user_brightnesses = [c["brightness"] for c in user_colors]
    shade_brightnesses = [c["brightness"] for c in shade_colors]
    
    user_min = min(user_brightnesses)
    user_max = max(user_brightnesses)
    user_avg = sum(c["brightness"] * c["percentage"] for c in user_colors) / sum(c["percentage"] for c in user_colors)
    
    shade_min = min(shade_brightnesses)
    shade_max = max(shade_brightnesses)
    shade_avg = sum(c["brightness"] * c["percentage"] for c in shade_colors) / sum(c["percentage"] for c in shade_colors)
    
    # Compare ranges
    range_diff = abs((user_max - user_min) - (shade_max - shade_min))
    range_score = max(0, 100 - range_diff * 0.5)
    
    # Compare averages
    avg_diff = abs(user_avg - shade_avg)
    avg_score = max(0, 100 - avg_diff * 0.8)
    
    # Compare min/max positions
    min_diff = abs(user_min - shade_min)
    max_diff = abs(user_max - shade_max)
    position_score = max(0, 100 - (min_diff + max_diff) * 0.3)
    
    return (range_score * 0.3 + avg_score * 0.4 + position_score * 0.3)

def tone_harmony(user_colors, shade_colors):
    """Check if tones are harmonious"""
    user_tones = set(c["tone"] for c in user_colors)
    shade_tones = set(c["tone"] for c in shade_colors)
    
    # Intersection over union
    intersection = len(user_tones & shade_tones)
    union = len(user_tones | shade_tones)
    
    return (intersection / union * 100) if union > 0 else 0

def saturation_match(user_colors, shade_colors):
    """Compare saturation levels"""
    user_avg_sat = sum(c["saturation"] * c["percentage"] for c in user_colors) / sum(c["percentage"] for c in user_colors)
    shade_avg_sat = sum(c["saturation"] * c["percentage"] for c in shade_colors) / sum(c["percentage"] for c in shade_colors)
    
    sat_diff = abs(user_avg_sat - shade_avg_sat)
    return max(0, 100 - sat_diff * 200)

def match_shade(user_colors, shade_colors):
    """Pure dynamic matching - no hardcoded rules"""
    
    # 1. Color distribution similarity (most important)
    dist_score = color_distribution_similarity(user_colors, shade_colors)
    
    # 2. Brightness profile matching
    bright_score = brightness_profile_match(user_colors, shade_colors)
    
    # 3. Tone harmony
    tone_score = tone_harmony(user_colors, shade_colors)
    
    # 4. Saturation matching
    sat_score = saturation_match(user_colors, shade_colors)
    
    # Weighted combination
    final_score = (
        dist_score * 0.50 +      # Color accuracy
        bright_score * 0.35 +    # Brightness pattern
        tone_score * 0.10 +      # Tone harmony
        sat_score * 0.05         # Saturation
    )
    
    return round(final_score, 2)

def find_best_match(user_colors, reference_shades):
    """Find best match dynamically"""
    
    scores = {}
    for shade_name, shade_colors in reference_shades.items():
        scores[shade_name] = match_shade(user_colors, shade_colors)
    
    # Sort by score
    sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    best_match = next(iter(sorted_scores)) if sorted_scores else None
    
    return best_match, sorted_scores
