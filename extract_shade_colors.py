import os
import json
import cv2
import numpy as np
from pathlib import Path
try:
    from sklearn.cluster import KMeans
except:
    from scipy.cluster.vq import kmeans, vq
    KMeans = None

def extract_hair_color_from_image(image_path):
    """Extract dominant colors from hair extension image"""
    img = cv2.imread(str(image_path))
    if img is None:
        return None
    
    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Reshape to pixels
    pixels = img_rgb.reshape(-1, 3).astype(np.float32)
    
    # Aggressive filtering for accurate color extraction
    brightness = pixels[:, 0] * 0.299 + pixels[:, 1] * 0.587 + pixels[:, 2] * 0.114
    max_vals = np.max(pixels, axis=1)
    min_vals = np.min(pixels, axis=1)
    saturation = (max_vals - min_vals) / (max_vals + 1)
    
    # Remove shadows, highlights, and grey tones
    valid_mask = (brightness > 15) & (brightness < 235) & (saturation > 0.08)
    valid_pixels = pixels[valid_mask]
    
    if len(valid_pixels) < 100:
        valid_pixels = pixels[(brightness > 20) & (brightness < 230)]
    
    # KMeans clustering with more colors for better accuracy
    n_colors = min(7, len(np.unique(valid_pixels.astype(int), axis=0)))
    
    if KMeans:
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(valid_pixels)
        labels = kmeans.labels_
        centers = kmeans.cluster_centers_
    else:
        centers = [np.mean(valid_pixels, axis=0)]
        labels = np.zeros(len(valid_pixels))
        n_colors = 1
    
    counts = np.bincount(labels.astype(int))
    total = len(labels)
    
    colors = []
    for i in range(n_colors):
        percentage = (counts[i] / total) * 100
        if percentage >= 3:  # At least 3% to reduce noise
            color = [max(0, min(255, int(c))) for c in centers[i]]
            
            # Calculate color properties
            r, g, b = color
            brightness = r * 0.299 + g * 0.587 + b * 0.114
            max_c = max(color)
            min_c = min(color)
            sat = (max_c - min_c) / (max_c + 1) if max_c > 0 else 0
            
            # Skip grey/white colors
            if not (brightness > 90 and sat < 0.15):
                colors.append({
                    "color": color,
                    "percentage": round(percentage, 2)
                })
    
    # Sort by percentage
    colors.sort(key=lambda x: x["percentage"], reverse=True)
    return colors

def process_all_shade_folders():
    """Process all shade folders with detailed color analysis"""
    base_folders = ["data", "new_data", "new_shade", "New4_Data"]
    all_shades = {}
    
    for base_folder in base_folders:
        base_path = Path(base_folder)
        if not base_path.exists():
            continue
        
        print(f"\nProcessing {base_folder}...")
        
        # Check if it has subdirectories (shade folders)
        subdirs = [d for d in base_path.iterdir() if d.is_dir()]
        
        if subdirs:
            # Process each shade folder
            for shade_dir in subdirs:
                shade_name = shade_dir.name
                
                # Skip if already processed from another folder
                if shade_name in all_shades:
                    continue
                
                print(f"  Processing shade: {shade_name}")
                
                all_colors = []
                image_details = []
                
                # Process all images in shade folder
                for ext in ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]:
                    for img_file in shade_dir.glob(ext):
                        colors = extract_hair_color_from_image(img_file)
                        if colors:
                            all_colors.extend(colors)
                            image_details.append(f"{img_file.name}: {len(colors)} colors")
                
                if all_colors:
                    # Combine similar colors
                    combined = combine_colors(all_colors)
                    all_shades[shade_name] = combined
                    
                    # Calculate shade properties
                    avg_brightness = np.mean([c["color"][0] * 0.299 + c["color"][1] * 0.587 + c["color"][2] * 0.114 for c in combined])
                    main_color = combined[0]["color"]
                    is_warm = main_color[0] > main_color[1] and main_color[0] > main_color[2]
                    
                    print(f"    ✓ {len(combined)} colors | Brightness: {avg_brightness:.1f} | Warm: {is_warm}")
                    print(f"      Main RGB: {main_color}")
        else:
            # Single image per shade
            for img_file in base_path.glob("*.jpg"):
                shade_name = img_file.stem
                if shade_name in all_shades:
                    continue
                    
                colors = extract_hair_color_from_image(img_file)
                if colors:
                    all_shades[shade_name] = colors
                    main_color = colors[0]["color"]
                    avg_brightness = np.mean([c["color"][0] * 0.299 + c["color"][1] * 0.587 + c["color"][2] * 0.114 for c in colors])
                    is_warm = main_color[0] > main_color[1]
                    print(f"  {shade_name}: {len(colors)} colors | Brightness: {avg_brightness:.1f} | Warm: {is_warm}")
    
    return all_shades

def combine_colors(colors, threshold=20):
    """Combine similar colors with hue awareness"""
    if not colors:
        return []
    
    combined = []
    for color in colors:
        rgb = color["color"]
        percentage = color["percentage"]
        
        merged = False
        for existing in combined:
            existing_rgb = existing["color"]
            
            # Calculate RGB distance
            dist = np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb, existing_rgb)))
            
            # Calculate hue difference for warm tones
            r1, g1, b1 = rgb
            r2, g2, b2 = existing_rgb
            is_warm1 = r1 > g1 and r1 > b1
            is_warm2 = r2 > g2 and r2 > b2
            
            # Don't merge if one is warm and other is not
            if is_warm1 != is_warm2 and dist > 15:
                continue
            
            if dist < threshold:
                # Merge with weighted average
                total_weight = existing["percentage"] + percentage
                new_rgb = [
                    int((existing_rgb[i] * existing["percentage"] + rgb[i] * percentage) / total_weight)
                    for i in range(3)
                ]
                existing["color"] = new_rgb
                existing["percentage"] = total_weight
                merged = True
                break
        
        if not merged:
            combined.append({"color": rgb, "percentage": percentage})
    
    # Normalize percentages
    total = sum(c["percentage"] for c in combined)
    if total > 0:
        for c in combined:
            c["percentage"] = round((c["percentage"] / total) * 100, 2)
    
    # Sort by percentage, keep top colors
    combined.sort(key=lambda x: x["percentage"], reverse=True)
    return combined[:5]

def main():
    print("Extracting RGB colors from hair extension samples...")
    
    all_shades = process_all_shade_folders()
    
    if all_shades:
        # Save to JSON
        output_path = Path("app/shade/reference_shades_new.json")
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(all_shades, f, indent=2)
        
        print(f"\nSuccess! Saved {len(all_shades)} shades to {output_path}")
        
        # Show summary
        print("\nShade Summary:")
        for shade_name, colors in all_shades.items():
            avg_brightness = np.mean([c["color"][0] * 0.299 + c["color"][1] * 0.587 + c["color"][2] * 0.114 for c in colors])
            print(f"  {shade_name}: {len(colors)} colors, brightness: {avg_brightness:.1f}")
    else:
        print("\nNo shades processed!")

if __name__ == "__main__":
    main()