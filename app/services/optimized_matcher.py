"""
Optimized Shade Matcher - Uses comprehensive color analysis
"""
import numpy as np

def lab_distance(lab1, lab2):
    """Calculate Delta E distance in Lab space"""
    dL = lab1[0] - lab2[0]
    da = lab1[1] - lab2[1]
    db = lab1[2] - lab2[2]
    return np.sqrt(dL**2 + da**2 + db**2)

def match_shade(user_colors, shade_colors):
    """Match user colors to shade colors with weighted scoring"""
    
    # Calculate weighted averages for user
    total_pct = sum(c["percentage"] for c in user_colors)
    user_brightness = sum(c["brightness"] * c["percentage"] for c in user_colors) / total_pct
    user_hue = sum(c["hue"] * c["percentage"] for c in user_colors) / total_pct
    user_saturation = sum(c["saturation"] * c["percentage"] for c in user_colors) / total_pct
    user_bright_range = max(c["brightness"] for c in user_colors) - min(c["brightness"] for c in user_colors)
    
    # Calculate weighted averages for shade
    shade_total_pct = sum(c["percentage"] for c in shade_colors)
    shade_brightness = sum(c["brightness"] * c["percentage"] for c in shade_colors) / shade_total_pct
    shade_hue = sum(c["hue"] * c["percentage"] for c in shade_colors) / shade_total_pct
    shade_saturation = sum(c["saturation"] * c["percentage"] for c in shade_colors) / shade_total_pct
    shade_bright_range = max(c["brightness"] for c in shade_colors) - min(c["brightness"] for c in shade_colors)
    
    # 1. Brightness matching (most important)
    brightness_diff = abs(user_brightness - shade_brightness)
    if brightness_diff < 15:
        brightness_score = 100
    elif brightness_diff < 30:
        brightness_score = 85
    elif brightness_diff < 50:
        brightness_score = 70
    elif brightness_diff < 80:
        brightness_score = 50
    else:
        brightness_score = max(0, 30 - (brightness_diff - 80) * 0.5)
    
    # 2. Lab distance matching
    lab_score = 0
    for user_color in user_colors:
        user_lab = user_color["lab"]
        user_pct = user_color["percentage"]
        
        best_dist = float('inf')
        for shade_color in shade_colors:
            shade_lab = shade_color["lab"]
            dist = lab_distance(user_lab, shade_lab)
            if dist < best_dist:
                best_dist = dist
        
        if best_dist < 10:
            color_score = 100
        elif best_dist < 20:
            color_score = 90
        elif best_dist < 30:
            color_score = 80
        elif best_dist < 40:
            color_score = 70
        else:
            color_score = max(0, 60 - (best_dist - 40) * 0.8)
        
        lab_score += color_score * (user_pct / total_pct)
    
    # 3. Hue matching
    hue_diff = min(abs(user_hue - shade_hue), 360 - abs(user_hue - shade_hue))
    if hue_diff < 15:
        hue_score = 100
    elif hue_diff < 30:
        hue_score = 85
    elif hue_diff < 50:
        hue_score = 70
    else:
        hue_score = max(0, 50 - (hue_diff - 50) * 0.5)
    
    # 4. Saturation matching
    sat_diff = abs(user_saturation - shade_saturation)
    if sat_diff < 0.1:
        sat_score = 100
    elif sat_diff < 0.2:
        sat_score = 85
    elif sat_diff < 0.3:
        sat_score = 70
    else:
        sat_score = max(0, 50 - (sat_diff - 0.3) * 100)
    
    # 5. Tone matching
    user_tones = [c["tone"] for c in user_colors]
    shade_tones = [c["tone"] for c in shade_colors]
    tone_match = len(set(user_tones) & set(shade_tones)) / len(set(user_tones))
    tone_score = tone_match * 100
    
    # 6. Undertone matching
    user_undertones = [c.get("undertone", "neutral") for c in user_colors]
    shade_undertones = [c.get("undertone", "neutral") for c in shade_colors]
    undertone_match = len(set(user_undertones) & set(shade_undertones)) / len(set(user_undertones))
    undertone_score = undertone_match * 100
    
    # 7. Brightness range matching (for rooted/balayage detection)
    range_diff = abs(user_bright_range - shade_bright_range)
    if range_diff < 20:
        range_score = 100
    elif range_diff < 40:
        range_score = 85
    elif range_diff < 60:
        range_score = 70
    else:
        range_score = max(0, 50 - (range_diff - 60) * 0.5)
    
    # Weighted final score
    final_score = (
        brightness_score * 0.30 +
        lab_score * 0.25 +
        range_score * 0.20 +
        hue_score * 0.12 +
        sat_score * 0.08 +
        tone_score * 0.03 +
        undertone_score * 0.02
    )
    
    return round(final_score, 2)

def find_best_match(user_colors, reference_shades):
    """Find best matching shade"""
    
    # Calculate user characteristics
    total_pct = sum(c["percentage"] for c in user_colors)
    user_brightness = sum(c["brightness"] * c["percentage"] for c in user_colors) / total_pct
    brightnesses = [c["brightness"] for c in user_colors]
    
    # Detect rooted/balayage hair - more sensitive detection
    brightness_range = max(brightnesses) - min(brightnesses)
    has_roots = brightness_range > 60 and min(brightnesses) < 80
    is_very_light = user_brightness > 160
    
    scores = {}
    for shade_name, shade_colors in reference_shades.items():
        score = match_shade(user_colors, shade_colors)
        
        # Calculate shade average brightness
        shade_total_pct = sum(c["percentage"] for c in shade_colors)
        shade_avg_brightness = sum(c["brightness"] * c["percentage"] for c in shade_colors) / shade_total_pct
        
        # Penalize brown shades for blonde hair (brightness > 110)
        if user_brightness > 110:
            if any(x in shade_name.lower() for x in ["brown", "chocolate", "coffee", "espresso", "mocha"]) and "blonde" not in shade_name.lower():
                if shade_avg_brightness < 100:
                    score *= 0.75  # Strong penalty for dark browns
                elif shade_avg_brightness < 120:
                    score *= 0.85  # Medium penalty for medium browns
        
        # Boost blonde shades for blonde hair
        if user_brightness > 120:
            if any(x in shade_name.lower() for x in ["blonde", "honey", "sandy", "champagne", "beige"]):
                score *= 1.15
        
        # Boost for rooted shades when hair has roots
        if has_roots and any(x in shade_name for x in ["Rooted", "Balayage", "Ombre"]):
            score *= 1.12
        
        # Boost light shades for very light hair
        if is_very_light and any(x in shade_name for x in ["Platinum", "Silver", "Champagne", "Ivory", "lvory"]):
            score *= 1.10
        
        scores[shade_name] = score
    
    # Sort and return
    sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    best_match = next(iter(sorted_scores)) if sorted_scores else None
    
    return best_match, sorted_scores
