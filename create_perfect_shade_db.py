import cv2
import numpy as np
import json
from pathlib import Path
from sklearn.cluster import KMeans

def rgb_to_hsv(rgb):
    """Convert RGB to HSV"""
    r, g, b = [x / 255.0 for x in rgb]
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    diff = max_c - min_c
    
    if diff == 0:
        h = 0
    elif max_c == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_c == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360
    
    s = 0 if max_c == 0 else (diff / max_c)
    v = max_c
    return h, s, v

def analyze_shade_image(image_path):
    """Fast and accurate color extraction"""
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"    [WARN] Could not read: {image_path}")
        return None
    
    # Resize for faster processing
    h, w = img.shape[:2]
    if h > 800 or w > 800:
        scale = 800 / max(h, w)
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pixels = img_rgb.reshape(-1, 3).astype(np.float32)
    
    # Fast filtering
    brightness = pixels[:, 0] * 0.299 + pixels[:, 1] * 0.587 + pixels[:, 2] * 0.114
    max_vals = np.max(pixels, axis=1)
    min_vals = np.min(pixels, axis=1)
    saturation = (max_vals - min_vals) / (max_vals + 1)
    
    # Aggressive filtering for clean colors
    valid_mask = (brightness > 20) & (brightness < 230) & (saturation > 0.1)
    valid_pixels = pixels[valid_mask]
    
    if len(valid_pixels) < 50:
        valid_pixels = pixels[(brightness > 25) & (brightness < 225)]
    
    # Sample for speed if too many pixels
    if len(valid_pixels) > 10000:
        indices = np.random.choice(len(valid_pixels), 10000, replace=False)
        valid_pixels = valid_pixels[indices]
    
    # Cluster into 3 dominant colors (faster)
    n_clusters = min(3, len(np.unique(valid_pixels.astype(int), axis=0)))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=5)
    kmeans.fit(valid_pixels)
    
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_
    counts = np.bincount(labels)
    total = len(labels)
    
    colors = []
    for i in range(n_clusters):
        percentage = (counts[i] / total) * 100
        if percentage >= 5:  # Higher threshold
            rgb = [max(0, min(255, int(c))) for c in centers[i]]
            r, g, b = rgb
            
            # Calculate properties
            brightness_val = r * 0.299 + g * 0.587 + b * 0.114
            h, s, v = rgb_to_hsv(rgb)
            
            # Accurate tone detection
            if h < 30 and s > 0.3 and r > g + 15:
                tone = "warm_orange"  # Copper
            elif 30 <= h < 60 and s > 0.2:
                tone = "warm_brown"   # Autumn
            elif h < 40 and s < 0.2:
                tone = "neutral_brown"
            elif 40 <= h < 80 and s > 0.2:
                tone = "golden"
            elif h >= 180 and h < 270:
                tone = "cool"
            else:
                tone = "neutral"
            
            colors.append({
                "color": rgb,
                "percentage": round(percentage, 2),
                "brightness": round(brightness_val, 2),
                "hue": round(h, 2),
                "saturation": round(s, 3),
                "tone": tone
            })
    
    colors.sort(key=lambda x: x["percentage"], reverse=True)
    return colors

def process_new_shade_folder():
    """Process new_shade folder - direct images"""
    shade_path = Path("new_shade")
    if not shade_path.exists():
        print(f"new_shade folder not found at: {shade_path.absolute()}")
        return {}
    
    print(f"Scanning: {shade_path.absolute()}\n")
    
    all_shades = {}
    
    # Process all images directly in new_shade folder
    for img_file in shade_path.iterdir():
        if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            shade_name = img_file.stem  # Filename without extension
            print(f"Processing: {shade_name}")
            
            colors = analyze_shade_image(img_file)
            if colors:
                all_shades[shade_name] = colors
                print(f"  Extracted {len(colors)} colors")
                for c in colors:
                    print(f"    RGB{c['color']} - {c['tone']} (H:{c['hue']:.0f}, S:{c['saturation']:.2f}, B:{c['brightness']:.0f})")
            else:
                print(f"  [WARN] No colors extracted")
    
    return all_shades

def combine_colors(colors):
    """Fast color combining with tone awareness"""
    if not colors:
        return []
    
    combined = []
    for color in colors:
        rgb = color["color"]
        pct = color["percentage"]
        tone = color["tone"]
        
        merged = False
        for existing in combined:
            # Check RGB distance
            dist = np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb, existing["color"])))
            
            # Don't merge different tones
            if existing["tone"] != tone and dist > 15:
                continue
            
            if dist < 25:
                # Weighted merge
                total = existing["percentage"] + pct
                for i in range(3):
                    existing["color"][i] = int((existing["color"][i] * existing["percentage"] + rgb[i] * pct) / total)
                existing["percentage"] = total
                existing["brightness"] = (existing["brightness"] * existing["percentage"] + color["brightness"] * pct) / total
                existing["hue"] = (existing["hue"] * existing["percentage"] + color["hue"] * pct) / total
                existing["saturation"] = (existing["saturation"] * existing["percentage"] + color["saturation"] * pct) / total
                merged = True
                break
        
        if not merged:
            combined.append(color.copy())
    
    # Normalize
    total = sum(c["percentage"] for c in combined)
    if total > 0:
        for c in combined:
            c["percentage"] = round((c["percentage"] / total) * 100, 2)
            c["brightness"] = round(c["brightness"], 2)
            c["hue"] = round(c["hue"], 2)
            c["saturation"] = round(c["saturation"], 3)
    
    combined.sort(key=lambda x: x["percentage"], reverse=True)
    return combined[:3]  # Keep top 3 colors

def main():
    print("Creating perfect shade database from new_shade folder...\n")
    
    shades = process_new_shade_folder()
    
    if shades:
        output_path = Path("app/shade/perfect_shades.json")
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(shades, f, indent=2)
        
        print(f"\n[OK] Created database with {len(shades)} shades")
        print(f"[OK] Saved to: {output_path}")
    else:
        print("\n[ERROR] No shades processed!")

if __name__ == "__main__":
    main()
