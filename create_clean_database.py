import cv2
import numpy as np
import json
from pathlib import Path
from sklearn.cluster import KMeans

def rgb_to_hsv(rgb):
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

def extract_clean_colors(image_path):
    """Extract accurate colors from shade image"""
    img = cv2.imread(str(image_path))
    if img is None:
        return None
    
    # Resize for speed
    h, w = img.shape[:2]
    if max(h, w) > 600:
        scale = 600 / max(h, w)
        img = cv2.resize(img, None, fx=scale, fy=scale)
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pixels = img_rgb.reshape(-1, 3).astype(np.float32)
    
    # Clean filtering
    brightness = pixels[:, 0] * 0.299 + pixels[:, 1] * 0.587 + pixels[:, 2] * 0.114
    max_vals = np.max(pixels, axis=1)
    min_vals = np.min(pixels, axis=1)
    saturation = (max_vals - min_vals) / (max_vals + 1)
    
    # Remove shadows, highlights, grey
    valid = (brightness > 25) & (brightness < 220) & (saturation > 0.05)
    clean_pixels = pixels[valid]
    
    if len(clean_pixels) < 100:
        clean_pixels = pixels[(brightness > 30) & (brightness < 210)]
    
    # Sample if too many
    if len(clean_pixels) > 8000:
        idx = np.random.choice(len(clean_pixels), 8000, replace=False)
        clean_pixels = clean_pixels[idx]
    
    # Cluster into 3 colors
    n = min(3, len(np.unique(clean_pixels.astype(int), axis=0)))
    kmeans = KMeans(n_clusters=n, random_state=42, n_init=5)
    kmeans.fit(clean_pixels)
    
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_
    counts = np.bincount(labels)
    total = len(labels)
    
    colors = []
    for i in range(n):
        pct = (counts[i] / total) * 100
        if pct >= 5:
            rgb = [max(0, min(255, int(c))) for c in centers[i]]
            r, g, b = rgb
            
            brightness_val = r * 0.299 + g * 0.587 + b * 0.114
            h, s, v = rgb_to_hsv(rgb)
            
            # Accurate tone
            if h < 30 and s > 0.3 and r > g + 15:
                tone = "warm_orange"
            elif 30 <= h < 60 and s > 0.2:
                tone = "warm_brown"
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
                "percentage": round(pct, 2),
                "brightness": round(brightness_val, 2),
                "hue": round(h, 2),
                "saturation": round(s, 3),
                "tone": tone
            })
    
    colors.sort(key=lambda x: x["percentage"], reverse=True)
    return colors

def process_new_shade():
    """Process new_shade folder"""
    shade_path = Path("new_shade")
    if not shade_path.exists():
        print("new_shade folder not found!")
        return {}
    
    all_shades = {}
    
    # Check for subdirectories
    subdirs = [d for d in shade_path.iterdir() if d.is_dir()]
    
    if subdirs:
        print(f"Processing {len(subdirs)} shade folders...\n")
        
        for shade_dir in subdirs:
            shade_name = shade_dir.name
            print(f"Processing: {shade_name}")
            
            all_colors = []
            for img_file in shade_dir.iterdir():
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    colors = extract_clean_colors(img_file)
                    if colors:
                        all_colors.extend(colors)
            
            if all_colors:
                # Merge similar colors
                merged = merge_colors(all_colors)
                all_shades[shade_name] = merged
                print(f"  → {len(merged)} colors")
                for c in merged:
                    print(f"     RGB{c['color']} {c['tone']} ({c['percentage']}%)")
    else:
        print("Processing direct images...\n")
        
        for img_file in shade_path.iterdir():
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                shade_name = img_file.stem
                print(f"Processing: {shade_name}")
                
                colors = extract_clean_colors(img_file)
                if colors:
                    all_shades[shade_name] = colors
                    print(f"  → {len(colors)} colors")
    
    return all_shades

def merge_colors(colors):
    """Merge similar colors"""
    merged = []
    
    for color in colors:
        rgb = color["color"]
        pct = color["percentage"]
        tone = color["tone"]
        
        found = False
        for existing in merged:
            dist = np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb, existing["color"])))
            
            # Don't merge different tones
            if existing["tone"] != tone and dist > 20:
                continue
            
            if dist < 30:
                total = existing["percentage"] + pct
                for i in range(3):
                    existing["color"][i] = int((existing["color"][i] * existing["percentage"] + rgb[i] * pct) / total)
                existing["percentage"] = total
                existing["brightness"] = (existing["brightness"] * existing["percentage"] + color["brightness"] * pct) / total
                existing["hue"] = (existing["hue"] * existing["percentage"] + color["hue"] * pct) / total
                existing["saturation"] = (existing["saturation"] * existing["percentage"] + color["saturation"] * pct) / total
                found = True
                break
        
        if not found:
            merged.append(color.copy())
    
    # Normalize
    total = sum(c["percentage"] for c in merged)
    if total > 0:
        for c in merged:
            c["percentage"] = round((c["percentage"] / total) * 100, 2)
            c["brightness"] = round(c["brightness"], 2)
            c["hue"] = round(c["hue"], 2)
            c["saturation"] = round(c["saturation"], 3)
    
    merged.sort(key=lambda x: x["percentage"], reverse=True)
    return merged[:3]

def main():
    print("Creating CLEAN shade database...\n")
    
    shades = process_new_shade()
    
    if shades:
        output = Path("app/shade/clean_shades.json")
        output.parent.mkdir(exist_ok=True)
        
        with open(output, 'w') as f:
            json.dump(shades, f, indent=2)
        
        print(f"\n[OK] Created {len(shades)} shades")
        print(f"[OK] Saved to: {output}")
    else:
        print("\n[ERROR] No shades!")

if __name__ == "__main__":
    main()
