"""
Improved Matcher - Accurate color matching with clustering
"""
import numpy as np

def lab_distance(lab1, lab2):
    """Calculate Delta E distance in Lab space"""
    dL = lab1[0] - lab2[0]
    da = lab1[1] - lab2[1]
    db = lab1[2] - lab2[2]
    return np.sqrt(dL**2 + da**2 + db**2)

def calculate_shade_signature(shade_colors):
    """Calculate weighted signature for a shade"""
    total_pct = sum(c["percentage"] for c in shade_colors)
    
    # Weighted averages
    avg_brightness = sum(c["brightness"] * c["percentage"] for c in shade_colors) / total_pct
    avg_lab = [
        sum(c["lab"][0] * c["percentage"] for c in shade_colors) / total_pct,
        sum(c["lab"][1] * c["percentage"] for c in shade_colors) / total_pct,
        sum(c["lab"][2] * c["percentage"] for c in shade_colors) / total_pct
    ]
    
    # Brightness range
    brightnesses = [c["brightness"] for c in shade_colors]
    bright_range = max(brightnesses) - min(brightnesses)
    
    return {
        "avg_brightness": avg_brightness,
        "avg_lab": avg_lab,
        "bright_range": bright_range,
        "colors": shade_colors
    }

def match_user_to_shade(user_colors, shade_signature):
    """Match user colors to shade using multiple factors"""
    
    # Calculate user signature
    total_pct = sum(c["percentage"] for c in user_colors)
    user_avg_brightness = sum(c["brightness"] * c["percentage"] for c in user_colors) / total_pct
    user_avg_lab = [
        sum(c["lab"][0] * c["percentage"] for c in user_colors) / total_pct,
        sum(c["lab"][1] * c["percentage"] for c in user_colors) / total_pct,
        sum(c["lab"][2] * c["percentage"] for c in user_colors) / total_pct
    ]
    user_brightnesses = [c["brightness"] for c in user_colors]
    user_bright_range = max(user_brightnesses) - min(user_brightnesses)
    
    # 1. Average Lab distance (40% weight)
    avg_lab_dist = lab_distance(user_avg_lab, shade_signature["avg_lab"])
    if avg_lab_dist < 10:
        lab_score = 100
    elif avg_lab_dist < 20:
        lab_score = 90
    elif avg_lab_dist < 30:
        lab_score = 80
    elif avg_lab_dist < 40:
        lab_score = 70
    else:
        lab_score = max(0, 60 - (avg_lab_dist - 40) * 0.5)
    
    # 2. Brightness similarity (30% weight)
    bright_diff = abs(user_avg_brightness - shade_signature["avg_brightness"])
    if bright_diff < 15:
        bright_score = 100
    elif bright_diff < 30:
        bright_score = 85
    elif bright_diff < 50:
        bright_score = 70
    else:
        bright_score = max(0, 50 - (bright_diff - 50) * 0.5)
    
    # 3. Color-by-color matching (20% weight)
    color_match_score = 0
    for user_color in user_colors:
        user_lab = user_color["lab"]
        user_pct = user_color["percentage"]
        
        # Find closest shade color
        min_dist = min(lab_distance(user_lab, sc["lab"]) for sc in shade_signature["colors"])
        
        if min_dist < 15:
            match = 100
        elif min_dist < 30:
            match = 85
        elif min_dist < 45:
            match = 70
        else:
            match = max(0, 55 - (min_dist - 45) * 0.5)
        
        color_match_score += match * (user_pct / total_pct)
    
    # 4. Brightness range similarity (10% weight)
    range_diff = abs(user_bright_range - shade_signature["bright_range"])
    if range_diff < 20:
        range_score = 100
    elif range_diff < 40:
        range_score = 80
    else:
        range_score = max(0, 60 - (range_diff - 40) * 0.5)
    
    # Weighted final score
    final_score = (
        lab_score * 0.40 +
        bright_score * 0.30 +
        color_match_score * 0.20 +
        range_score * 0.10
    )
    
    return round(final_score, 2)

def find_best_match(user_colors, reference_shades):
    """Find best matching shade from database"""
    
    print("\n" + "="*60)
    print("HAIR COLOR MATCHING")
    print("="*60)
    
    # Show detected colors
    print("\n[1] DETECTED COLORS:")
    total_pct = sum(c["percentage"] for c in user_colors)
    user_avg_brightness = sum(c["brightness"] * c["percentage"] for c in user_colors) / total_pct
    print(f"Average Brightness: {user_avg_brightness:.1f}")
    for i, c in enumerate(user_colors, 1):
        print(f"  {i}. RGB{c['rgb']} - {c['percentage']:.1f}% - Brightness: {c['brightness']:.1f}")
    
    # Pre-calculate signatures for all shades
    print(f"\n[2] LOADING DATABASE: {len(reference_shades)} shades")
    shade_signatures = {}
    for shade_name, shade_colors in reference_shades.items():
        shade_signatures[shade_name] = calculate_shade_signature(shade_colors)
    
    # Match user to each shade
    print("\n[3] MATCHING...")
    scores = {}
    for shade_name, signature in shade_signatures.items():
        scores[shade_name] = match_user_to_shade(user_colors, signature)
    
    # Sort by score
    sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    best_match = next(iter(sorted_scores)) if sorted_scores else None
    
    # Show top 5 matches
    print("\n[4] TOP 5 MATCHES:")
    for i, (shade, score) in enumerate(list(sorted_scores.items())[:5], 1):
        base_name = shade.split("_")[0] if "_" in shade else shade
        print(f"  {i}. {base_name}: {score:.1f}%")
    
    print(f"\n[5] BEST MATCH: {best_match.split('_')[0] if best_match and '_' in best_match else best_match}")
    print(f"    Score: {sorted_scores[best_match]:.1f}%")
    print("="*60 + "\n")
    
    return best_match, sorted_scores
