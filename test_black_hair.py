from app.services.hair_color_detector import detect_hair_color
from app.services.improved_shade_matcher import find_best_shade_improved, detect_black_hair_specifically
import json

# Test with a black hair image
def test_black_hair_detection(image_path):
    print("🧪 Testing Black Hair Detection...")
    
    # Detect hair colors
    user_colors = detect_hair_color(image_path)
    print(f"Detected colors: {user_colors}")
    
    # Check if black hair
    is_black = detect_black_hair_specifically(user_colors)
    print(f"Is black hair: {is_black}")
    
    # Load reference shades
    with open("app/shade/reference_shades_new.json", "r") as f:
        shade_data = json.load(f)
    
    # Find best match
    best_match, scores = find_best_shade_improved(user_colors, shade_data)
    
    print(f"\n🎯 Best match: {best_match}")
    print("Top 5 matches:")
    for i, (shade, score) in enumerate(list(scores.items())[:5]):
        print(f"  {i+1}. {shade}: {score}%")

if __name__ == "__main__":
    # Replace with your black hair image path
    test_black_hair_detection("your_black_hair_image.jpg")