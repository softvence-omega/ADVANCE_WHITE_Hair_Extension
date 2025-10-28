import json
import numpy as np

# Load JSON
with open("app/shade/exact_shade_signatures.json") as f:
    shades = json.load(f)

# Test file
test_file = "Autumn_CloseUp.jpg"

# Get colors from JSON
test_colors = shades[test_file]['dominant_colors']
print(f"Testing: {test_file}")
print(f"Colors in JSON: {[c['rgb'] for c in test_colors[:3]]}")

# Simulate user upload (same colors)
user_colors = test_colors

# Match
def euclidean_distance(c1, c2):
    return np.linalg.norm(np.array(c1) - np.array(c2))

results = []
for file_name, shade_data in shades.items():
    all_distances = []
    for user_color in user_colors:
        user_rgb = user_color['rgb']
        for shade_color in shade_data['dominant_colors']:
            shade_rgb = shade_color['rgb']
            all_distances.append(euclidean_distance(user_rgb, shade_rgb))
    
    results.append({
        'file_name': file_name,
        'shade_name': shade_data['shade_name'],
        'distance': round(min(all_distances), 2)
    })

sorted_results = sorted(results, key=lambda x: x['distance'])

print("\nTop 5 matches:")
for r in sorted_results[:5]:
    print(f"{r['file_name']}: {r['distance']}")
