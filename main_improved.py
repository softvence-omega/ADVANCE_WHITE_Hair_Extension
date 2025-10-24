"""
Run this to create perfect shade database and test matching
"""
import subprocess
import sys

def main():
    print("=" * 60)
    print("STEP 1: Creating Perfect Shade Database")
    print("=" * 60)
    
    result = subprocess.run([sys.executable, "create_perfect_shade_db.py"], 
                          capture_output=False)
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("[OK] Database created successfully!")
        print("=" * 60)
        print("\nNow update your route to use perfect_matcher:")
        print("\nIn app/routes/hair_extension.py, change:")
        print("  from app.services.advanced_color_matcher import find_best_match_advanced")
        print("To:")
        print("  from app.services.perfect_matcher import find_perfect_match")
        print("\nAnd change:")
        print("  shade_data = load_shades_rgb(Settings.New_SHADE_PATH)")
        print("  best, all_scores = find_best_match_advanced(user_rgb, shade_data)")
        print("To:")
        print("  shade_data = load_shades_rgb(Settings.PERFECT_SHADE_PATH)")
        print("  best, all_scores = find_perfect_match(user_rgb, shade_data)")
    else:
        print("\n[ERROR] Error creating database!")

if __name__ == "__main__":
    main()
