"""
Local test script - Run this to test the matching system
"""
from app.services.hair_color_detector import detect_hair_color
from app.services.dynamic_matcher import find_best_match
from app.services.shade_code_mapper import get_color_code, get_tone_type, get_description
import json

def test_image(image_path):
    print(f"\n{'='*60}")
    print(f"Testing: {image_path}")
    print('='*60)
    
    try:
        # Detect hair colors
        print("\n[1/3] Detecting hair colors...")
        user_colors = detect_hair_color(input_path=image_path, original_path=image_path)
        
        print(f"\nDetected {len(user_colors)} colors:")
        for i, c in enumerate(user_colors, 1):
            print(f"  {i}. RGB{c['rgb']} - {c['percentage']:.1f}% - Brightness: {c['brightness']:.1f}")
        
        # Load shade database
        print("\n[2/3] Loading shade database...")
        with open("app/shade/final_shades.json", "r") as f:
            shade_data = json.load(f)
        print(f"Loaded {len(shade_data)} shades")
        
        # Match
        print("\n[3/3] Finding best match...")
        best_match, all_scores = find_best_match(user_colors, shade_data)
        
        # Extract base shade
        base_shade = best_match.split("_")[0] if best_match and "_" in best_match else best_match
        
        # Results
        print(f"\n{'='*60}")
        print("RESULTS:")
        print('='*60)
        print(f"✓ Matched Shade: {base_shade}")
        print(f"✓ Color Code: {get_color_code(base_shade)}")
        print(f"✓ Tone Type: {get_tone_type(base_shade)}")
        print(f"✓ Description: {get_description(base_shade)}")
        print(f"✓ Match Score: {all_scores[best_match]:.2f}%")
        
        print(f"\nTop 5 Matches:")
        for i, (shade, score) in enumerate(list(all_scores.items())[:5], 1):
            base = shade.split("_")[0] if "_" in shade else shade
            print(f"  {i}. {base}: {score:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test with your images
    test_images = [
        "3h.png",  # Should match: Rooted Golden Brown or similar
        "4h.png",  # Should match: Honey Blonde or similar
    ]
    
    for img in test_images:
        try:
            test_image(img)
        except FileNotFoundError:
            print(f"\n⚠️  Image not found: {img}")
        except Exception as e:
            print(f"\n❌ Failed: {e}")
    
    print(f"\n{'='*60}")
    print("Testing complete!")
    print('='*60)
