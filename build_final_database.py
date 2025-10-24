"""
Final Production Database Builder
- Lighting normalization
- Lab color space
- 6 tone classification
- Multi-lighting support
"""
import cv2
import numpy as np
import json
from pathlib import Path
from sklearn.cluster import KMeans
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color

def normalize_lighting(img):
    """Gray World Algorithm for lighting normalization"""
    img_float = img.astype(np.float32)
    
    # Calculate mean for each channel
    avg_b = np.mean(img_float[:, :, 0])
    avg_g = np.mean(img_float[:, :, 1])
    avg_r = np.mean(img_float[:, :, 2])
    
    # Gray world assumption: average should be gray
    gray = (avg_r + avg_g + avg_b) / 3
    
    # Scale factors
    scale_b = gray / (avg_b + 1e-6)
    scale_g = gray / (avg_g + 1e-6)
    scale_r = gray / (avg_r + 1e-6)
    
    # Apply correction
    img_float[:, :, 0] = np.clip(img_float[:, :, 0] * scale_b, 0, 255)
    img_float[:, :, 1] = np.clip(img_float[:, :, 1] * scale_g, 0, 255)
    img_float[:, :, 2] = np.clip(img_float[:, :, 2] * scale_r, 0, 255)
    
    return img_float.astype(np.uint8)

def rgb_to_lab(rgb):
    """Convert RGB to Lab color space"""
    r, g, b = [x / 255.0 for x in rgb]
    rgb_color = sRGBColor(r, g, b)
    lab_color = convert_color(rgb_color, LabColor)
    return [lab_color.lab_l, lab_color.lab_a, lab_color.lab_b]

def classify_tone(rgb, h, s):
    """Classify into 6 tones"""
    r, g, b = rgb
    
    if h < 30 and s > 0.3 and r > g + 15:
        return "warm_orange"
    elif 30 <= h < 60 and s > 0.2:
        return "warm_brown"
    elif h < 40 and s < 0.2:
        return "neutral_brown"
    elif 40 <= h < 80 and s > 0.2:
        return "golden"
    elif 180 <= h < 270:
        return "cool"
    else:
        return "neutral"

def rgb_to_hsv(rgb):
    """RGB to HSV"""
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

def extract_colors(image_path):
    """Extract colors with lighting normalization"""
    img = cv2.imread(str(image_path))
    if img is None:
        return None
    
    # Resize
    h, w = img.shape[:2]
    if max(h, w) > 600:
        scale = 600 / max(h, w)
        img = cv2.resize(img, None, fx=scale, fy=scale)
    
    # Normalize lighting
    img_normalized = normalize_lighting(img)
    
    # Convert to RGB
    img_rgb = cv2.cvtColor(img_normalized, cv2.COLOR_BGR2RGB)
    pixels = img_rgb.reshape(-1, 3).astype(np.float32)
    
    # Filter
    brightness = pixels[:, 0] * 0.299 + pixels[:, 1] * 0.587 + pixels[:, 2] * 0.114
    max_vals = np.max(pixels, axis=1)
    min_vals = np.min(pixels, axis=1)
    saturation = (max_vals - min_vals) / (max_vals + 1)
    
    valid = (brightness > 25) & (brightness < 220) & (saturation > 0.05)
    clean = pixels[valid]
    
    if len(clean) < 100:
        clean = pixels[(brightness > 30) & (brightness < 210)]
    
    # Sample
    if len(clean) > 8000:
        idx = np.random.choice(len(clean), 8000, replace=False)
        clean = clean[idx]
    
    # Cluster
    n = min(3, len(np.unique(clean.astype(int), axis=0)))
    kmeans = KMeans(n_clusters=n, random_state=42, n_init=5)
    kmeans.fit(clean)
    
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_
    counts = np.bincount(labels)
    total = len(labels)
    
    colors = []
    for i in range(n):
        pct = (counts[i] / total) * 100
        if pct >= 5:
            rgb = [max(0, min(255, int(c))) for c in centers[i]]
            
            # Calculate properties
            brightness_val = rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114
            h, s, v = rgb_to_hsv(rgb)
            lab = rgb_to_lab(rgb)
            tone = classify_tone(rgb, h, s)
            
            colors.append({
                "rgb": rgb,
                "lab": [round(x, 2) for x in lab],
                "percentage": round(pct, 2),
                "brightness": round(brightness_val, 2),
                "hue": round(h, 2),
                "saturation": round(s, 3),
                "tone": tone
            })
    
    colors.sort(key=lambda x: x["percentage"], reverse=True)
    return colors

def process_shades():
    """Process new_shade folder"""
    shade_path = Path("new_shade")
    if not shade_path.exists():
        print("❌ new_shade folder not found!")
        return {}
    
    all_shades = {}
    subdirs = [d for d in shade_path.iterdir() if d.is_dir()]
    
    if subdirs:
        print(f"📁 Found {len(subdirs)} shade folders\n")
        
        for shade_dir in subdirs:
            shade_name = shade_dir.name
            print(f"🎨 Processing: {shade_name}")
            
            all_colors = []
            for img_file in shade_dir.iterdir():
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    colors = extract_colors(img_file)
                    if colors:
                        all_colors.extend(colors)
            
            if all_colors:
                merged = merge_colors(all_colors)
                all_shades[shade_name] = merged
                print(f"   ✓ {len(merged)} colors | Tone: {merged[0]['tone']}")
    else:
        print("📄 Processing direct images\n")
        
        for img_file in shade_path.iterdir():
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                shade_name = img_file.stem
                print(f"🎨 {shade_name}")
                
                colors = extract_colors(img_file)
                if colors:
                    all_shades[shade_name] = colors
                    print(f"   ✓ {len(colors)} colors")
    
    return all_shades

def merge_colors(colors):
    """Merge similar colors"""
    merged = []
    
    for color in colors:
        rgb = color["rgb"]
        pct = color["percentage"]
        tone = color["tone"]
        
        found = False
        for existing in merged:
            dist = np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb, existing["rgb"])))
            
            if existing["tone"] != tone and dist > 20:
                continue
            
            if dist < 30:
                total = existing["percentage"] + pct
                for i in range(3):
                    existing["rgb"][i] = int((existing["rgb"][i] * existing["percentage"] + rgb[i] * pct) / total)
                    existing["lab"][i] = (existing["lab"][i] * existing["percentage"] + color["lab"][i] * pct) / total
                
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
            c["lab"] = [round(x, 2) for x in c["lab"]]
    
    merged.sort(key=lambda x: x["percentage"], reverse=True)
    return merged[:3]

def main():
    print("=" * 60)
    print("🚀 Building Final Production Database")
    print("=" * 60)
    print("✓ Lighting normalization")
    print("✓ Lab color space")
    print("✓ 6-tone classification")
    print("=" * 60)
    print()
    
    shades = process_shades()
    
    if shades:
        output = Path("app/shade/final_shades.json")
        output.parent.mkdir(exist_ok=True)
        
        with open(output, 'w') as f:
            json.dump(shades, f, indent=2)
        
        print()
        print("=" * 60)
        print(f"✅ Created {len(shades)} shades")
        print(f"💾 Saved to: {output}")
        print("=" * 60)
        
        # Summary
        tone_count = {}
        for shade_name, colors in shades.items():
            tone = colors[0]["tone"]
            tone_count[tone] = tone_count.get(tone, 0) + 1
        
        print("\n📊 Tone Distribution:")
        for tone, count in sorted(tone_count.items()):
            print(f"   {tone}: {count} shades")
    else:
        print("\n❌ No shades processed!")

if __name__ == "__main__":
    main()
