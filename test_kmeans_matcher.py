from app.services.kmeans_matcher import KMeansShadeMatche

# Test the matcher
matcher = KMeansShadeMatche()

# Test with some sample RGB values
test_colors = [
    ([130, 95, 61], "Autumn-like color"),
    ([70, 65, 62], "Dark/Black color"),
    ([197, 179, 150], "Blonde color"),
    ([149, 84, 46], "Copper color")
]

print("Testing KMeans Shade Matcher\n" + "="*50)

for rgb, description in test_colors:
    result = matcher.match_shade(rgb)
    print(f"\nTest: {description}")
    print(f"Input RGB: {rgb}")
    print(f"Matched Shade: {result['shade_name']}")
    print(f"Shade RGB: {result['shade_rgb']}")
    print(f"Distance: {result['distance']}")
