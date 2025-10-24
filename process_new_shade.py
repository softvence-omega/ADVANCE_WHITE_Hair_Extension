import cv2
import numpy as np
import json
from pathlib import Path
from sklearn.cluster import KMeans

def extract_hair_rgb(image_path):
    """Extract RGB from hair extension sample image"""
    img = cv2.imread(str(image_path))
    if img is None:
        return None
    
    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Reshape to pixels
    pixels = img_rgb.reshape(-1, 3)
    
    # Remove very dark (shadows) and very bright (highlights)
    brightness = np.mean(pixels, axis=1)
    valid_pixels = pixels[(brightness > 15) & (brightness < 240)]
    
    if len(valid_pixels) < 100:
        valid_pixels = pixels
    
    # KMeans clustering to find dominant colors
    n_colors = min(5, len(np.unique(valid_pixels, axis=0)))
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(valid_pixels)
    
    labels = kmeans.labels_
    counts = np.bincount(labels)
    total = len(labels)
    
    # Get colors with percentages
    colors = []
    for i in range(n_colors):
        percentage = (counts[i] / total) * 100
        if percentage >= 3:  # At least 3%
            color = [int(c) for c in kmeans.cluster_centers_[i]]
            colors.append({
                "color": color,
                "percentage": round(percentage, 2)
            })
    
    # Sort by percentage
    colors.sort(key=lambda x: x["percentage"], reverse=True)
    return colors

def process_new_shade_folder():
    """Process new_shade folder images"""
    new_shade_path = Path("new_shade")
    
    if not new_shade_path.exists():
        print("new_shade folder not found!")
        return None
    
    shade_data = {}
    
    print("Processing new_shade folder...")
    
    # Process each image
    for img_file in new_shade_path.glob("*.jpg"):
        shade_name = img_file.stem
        print(f"  Processing: {shade_name}")
        
        colors = extract_hair_rgb(img_file)
        
        if colors:
            shade_data[shade_name] = colors
            
            # Show extracted colors
            avg_brightness = np.mean([
                c["color"][0] * 0.299 + c["color"][1] * 0.587 + c["color"][2] * 0.114 
                for c in colors
            ])
            print(f"    Extracted {len(colors)} colors, avg brightness: {avg_brightness:.1f}")
            for i, c in enumerate(colors):
                print(f"      Color {i+1}: RGB{c['color']} ({c['percentage']}%)")
    
    # Also process PNG files
    for img_file in new_shade_path.glob("*.png"):
        shade_name = img_file.stem
        print(f"  Processing: {shade_name}")
        
        colors = extract_hair_rgb(img_file)
        
        if colors:
            shade_data[shade_name] = colors
            
            avg_brightness = np.mean([
                c["color"][0] * 0.299 + c["color"][1] * 0.587 + c["color"][2] * 0.114 
                for c in colors
            ])
            print(f"    Extracted {len(colors)} colors, avg brightness: {avg_brightness:.1f}")
            for i, c in enumerate(colors):
                print(f"      Color {i+1}: RGB{c['color']} ({c['percentage']}%)")
    
    return shade_data

def main():
    print("Extracting RGB values from new_shade folder...\n")
    
    shade_data = process_new_shade_folder()
    
    if shade_data:
        # Save to JSON
        output_path = Path("app/shade/reference_shades_new.json")
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(shade_data, f, indent=2)
        
        print(f"\nSuccess! Saved {len(shade_data)} shades to {output_path}")
        
        # Show summary
        print("\nShade Summary:")
        for shade_name in sorted(shade_data.keys()):
            colors = shade_data[shade_name]
            avg_brightness = np.mean([
                c["color"][0] * 0.299 + c["color"][1] * 0.587 + c["color"][2] * 0.114 
                for c in colors
            ])
            print(f"  {shade_name}: {len(colors)} colors, brightness: {avg_brightness:.1f}")
    else:
        print("\nNo shades processed!")

if __name__ == "__main__":
    main()