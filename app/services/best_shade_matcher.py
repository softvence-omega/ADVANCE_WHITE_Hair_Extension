import math
import json
from app.services.hair_color_detector import detect_hair_color

# ----------------------------------------
# Step 1: Helper function to calculate Euclidean distance
def color_distance(c1, c2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

# ----------------------------------------
# Step 2: Matching score calculator
def match_score(user_colors, reference_colors):
    total_score = 0

    for user_color in user_colors:
        user_rgb = user_color["color"]
        best_distance = float("inf")

        for ref_color in reference_colors:
            # print(f"ref{i}---------, {ref_color}")
            ref_rgb = ref_color["color"]
            dist = color_distance(user_rgb, ref_rgb)
            if dist < best_distance:
                best_distance = dist
    

        # scoring logic based on distance
        if best_distance < 20:
            score = 100
        elif best_distance < 50:
            score = 60
        elif best_distance < 80:
            score = 30
        else:
            score = 0

        # weighted by % presence in user's hair color
        total_score += (score * user_color["percentage"]) / 100

    return total_score

# ----------------------------------------
# Step 3: Main function to find best matching shade
def find_best_shade(user_colors, reference_shades):
    scores = {}
    for shade_name, light_types in reference_shades.items():
        # print(f"Processing shade: {shade_name}")
        total = 0
        for light_type in ["closeup", "indoor_light", "natural_light"]:
            if light_type in light_types:
                score = match_score(user_colors, light_types[light_type])
                total += score
            scores[shade_name] = round(total / 3, 2)  # average score

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
