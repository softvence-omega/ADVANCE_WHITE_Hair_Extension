import math
import json
from app.services.hair_color_detector import detect_hair_color

# ----------------------------------------
# Step 1: Helper function to calculate Euclidean distance
def color_distance(c1, c2):
    # Weighted RGB distance for better perceptual matching
    r_diff = (c1[0] - c2[0]) * 0.3
    g_diff = (c1[1] - c2[1]) * 0.59  # Green is most important
    b_diff = (c1[2] - c2[2]) * 0.11
    return math.sqrt(r_diff**2 + g_diff**2 + b_diff**2)

# ----------------------------------------
# Step 2: Matching score calculator
def match_score(user_colors, reference_colors):
    total_score = 0
    total_weight = 0

    for user_color in user_colors:
        user_rgb = user_color["color"]
        user_percentage = user_color["percentage"]
        best_distance = float("inf")
        best_ref_rgb = None

        for ref_color in reference_colors:
            ref_rgb = ref_color["color"]
            dist = color_distance(user_rgb, ref_rgb)
            if dist < best_distance:
                best_distance = dist
                best_ref_rgb = ref_rgb
    
        # Calculate brightness
        user_brightness = (user_rgb[0] * 0.299 + user_rgb[1] * 0.587 + user_rgb[2] * 0.114)
        ref_brightness = (best_ref_rgb[0] * 0.299 + best_ref_rgb[1] * 0.587 + best_ref_rgb[2] * 0.114) if best_ref_rgb else 0
        brightness_diff = abs(user_brightness - ref_brightness)
        
        # Strict matching with brightness priority
        if user_brightness < 40:  # Very dark (black)
            if best_distance < 20 and brightness_diff < 15:
                score = 100
            elif best_distance < 35 and brightness_diff < 25:
                score = 80
            elif best_distance < 50:
                score = 50
            else:
                score = 0
        elif user_brightness < 80:  # Dark brown
            if best_distance < 18 and brightness_diff < 12:
                score = 100
            elif best_distance < 30 and brightness_diff < 20:
                score = 75
            elif best_distance < 45:
                score = 40
            else:
                score = 0
        elif user_brightness < 130:  # Medium
            if best_distance < 15 and brightness_diff < 10:
                score = 100
            elif best_distance < 25 and brightness_diff < 15:
                score = 70
            elif best_distance < 40:
                score = 35
            else:
                score = 0
        else:  # Light
            if best_distance < 12 and brightness_diff < 8:
                score = 100
            elif best_distance < 20 and brightness_diff < 12:
                score = 65
            elif best_distance < 35:
                score = 30
            else:
                score = 0

        weighted_score = score * user_percentage / 100
        total_score += weighted_score
        total_weight += user_percentage / 100

    return total_score / total_weight if total_weight > 0 else 0

# ----------------------------------------
# Step 3: Main function to find best matching shade
def find_best_shade(user_colors, reference_shades):
    scores = {}
    for shade_name, light_types in reference_shades.items():
        # print(f"Processing shade: {shade_name}")
        total = 0
        for light_type in ["closeup", "indoor_light", "natural_light"]:
            if light_type in light_types:
                score = match_score1(user_colors, light_types[light_type])
                total += score
            scores[shade_name] = round(total / 3, 2)  # average score

    sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    best_match = next(iter(sorted_scores))  # First key is the best match

    return best_match, sorted_scores
# ---------------------NEW-------------------
import numpy as np
def match_score1(user_colors, shade_colors):
    """Euclidean distance in RGB, converted into similarity score (0-100)."""
    scores = []
    for uc in user_colors:
        u_color = np.array(uc["color"])
        for sc in shade_colors:
            s_color = np.array(sc["color"])
            dist = np.linalg.norm(u_color - s_color)  # distance
            score = 100 - min(dist, 100)  # normalize
            scores.append(score)
    return np.mean(scores)


def find_best_shade_single(user_colors, reference_shades):
    scores = {}
    for shade_name, shade_colors in reference_shades.items():
        score = match_score(user_colors, shade_colors)
        scores[shade_name] = round(score, 2)

    sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    best_match = next(iter(sorted_scores)) if sorted_scores else None
    print("sorted_scores",sorted_scores)
    return best_match, sorted_scores


def find_best_shade4(user_colors, reference_shades):
    scores = {}
    for shade_name, light_types in reference_shades.items():
        # print(f"Processing shade: {shade_name}")
        total = 0
        for light_type in ["default","closeup", "indoor_light", "natural_light"]:
            if light_type in light_types:
                score = match_score(user_colors, light_types[light_type])
                total += score
            scores[shade_name] = round(total / 4, 2)  # average score

    sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    best_match = next(iter(sorted_scores))  # First key is the best match

    return best_match, sorted_scores

if __name__ == "__main__":
    # ----------------------------------------
    # Run the matcher
    with open("reference_shades.json", "r") as f:
        reference_shades = json.load(f)

    image_path = "img1.png"  # Replace with your image path
    user_colors = detect_hair_color(image_path)

    best, all_scores = find_best_shade(user_colors, reference_shades)

    print("🔍 Closest matching shade:", best)
    print("\n📊 All matching scores:")
    for shade, score in all_scores.items():
        print(f" - {shade}: {round(score, 2)}%")
