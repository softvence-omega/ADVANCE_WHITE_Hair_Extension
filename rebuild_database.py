import cv2
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
import json

# -----------------------------
# Color & Analysis Utilities
# -----------------------------
def rgb_to_lab(rgb):
    """Convert RGB to LAB color space."""
    r, g, b = [x / 255.0 for x in rgb]
    r = ((r + 0.055)/1.055)**2.4 if r > 0.04045 else r/12.92
    g = ((g + 0.055)/1.055)**2.4 if g > 0.04045 else g/12.92
    b = ((b + 0.055)/1.055)**2.4 if b > 0.04045 else b/12.92
    x = r*0.4124 + g*0.3576 + b*0.1805
    y = r*0.2126 + g*0.7152 + b*0.0722
    z = r*0.0193 + g*0.1192 + b*0.9505
    x, y, z = x/0.95047, y/1.0, z/1.08883
    x = x**(1/3) if x>0.008856 else 7.787*x + 16/116
    y = y**(1/3) if y>0.008856 else 7.787*y + 16/116
    z = z**(1/3) if z>0.008856 else 7.787*z + 16/116
    L = 116*y - 16
    a = 500*(x-y)
    b_val = 200*(y-z)
    return [round(L,2), round(a,2), round(b_val,2)]

def get_color_properties(rgb):
    """Extract brightness, hue, saturation, tone, undertone, lab."""
    r, g, b = rgb
    brightness = r*0.299 + g*0.587 + b*0.114

    # HSV Calculation
    r_n, g_n, b_n = r/255.0, g/255.0, b/255.0
    mx, mn = max(r_n, g_n, b_n), min(r_n, g_n, b_n)
    diff = mx - mn
    if diff == 0:
        hue = 0
    elif mx == r_n:
        hue = (60 * ((g_n - b_n)/diff) + 360) % 360
    elif mx == g_n:
        hue = (60 * ((b_n - r_n)/diff) + 120) % 360
    else:
        hue = (60 * ((r_n - g_n)/diff) + 240) % 360
    saturation = 0 if mx==0 else diff/mx

    # Tone classification
    if hue<30 and saturation>0.3 and r>g+15:
        tone, undertone = "warm_orange","orange"
    elif 30<=hue<60 and saturation>0.2:
        tone, undertone = "warm_brown","golden"
    elif hue<40 and saturation<0.2:
        tone, undertone = "neutral_brown","neutral"
    elif 40<=hue<80 and saturation>0.2:
        tone, undertone = "golden","yellow"
    elif 180<=hue<270:
        tone, undertone = "cool","ash"
    else:
        tone, undertone = "neutral","neutral"

    lab = rgb_to_lab(rgb)
    return {
        "brightness": round(brightness,2),
        "hue": round(hue,2),
        "saturation": round(saturation,3),
        "tone": tone,
        "undertone": undertone,
        "lab": lab
    }

def calculate_color_score(color_data):
    """Weighted matching score for a color."""
    brightness = color_data.get('brightness', 100)
    saturation = color_data.get('saturation', 0.5)
    percentage = color_data.get('percentage', 25)
    tone = color_data.get('tone','neutral')

    # Base score from dominance
    base_score = percentage

    # Brightness factor
    if brightness<40: factor=1.2
    elif brightness<80: factor=1.1
    elif brightness<120: factor=1.0
    elif brightness<160: factor=0.95
    else: factor=0.9

    # Saturation factor
    if saturation>0.3: sat_factor=1.15
    elif saturation>0.15: sat_factor=1.05
    else: sat_factor=1.0

    # Tone factor
    tone_factors = {'warm_brown':1.1,'warm_orange':1.15,'neutral_brown':1.0,
                    'neutral':1.0,'cool':0.95,'golden':1.1}
    tone_factor = tone_factors.get(tone,1.0)

    return round(base_score*factor*sat_factor*tone_factor,2)

# -----------------------------
# Image Analysis
# -----------------------------
def analyze_image(image_path, n_clusters=3):
    """Analyze dominant colors from image."""
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pixels = img_rgb.reshape(-1,3)
    mask = (pixels.sum(axis=1)>30) & (pixels.sum(axis=1)<720)
    filtered = pixels[mask]
    if len(filtered)<100:
        filtered = pixels
    n_clusters = min(n_clusters, len(np.unique(filtered, axis=0)))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(filtered)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_.astype(int)
    counts = np.bincount(labels)
    colors=[]
    total=len(labels)
    for i in range(n_clusters):
        rgb=[int(c) for c in centers[i]]
        perc=(counts[i]/total)*100
        if perc>=5:
            props=get_color_properties(rgb)
            colors.append({"rgb":rgb,"percentage":round(perc,1),**props})
    colors.sort(key=lambda x:x["percentage"],reverse=True)
    return colors

def merge_colors(all_colors, dist_threshold=20, top_n=3):
    """Merge similar colors and normalize percentages."""
    merged=[]
    for color in all_colors:
        found=False
        for m in merged:
            dist=sum((a-b)**2 for a,b in zip(color["rgb"],m["rgb"]))**0.5
            if dist<dist_threshold:
                for k in ["rgb","brightness","hue","saturation"]:
                    if k=="rgb":
                        m[k]=[int((a+b)/2) for a,b in zip(m[k],color[k])]
                    else:
                        m[k]=(m[k]+color[k])/2
                m["percentage"]+=color["percentage"]
                found=True
                break
        if not found:
            merged.append(color.copy())
    total=sum(c["percentage"] for c in merged)
    for c in merged:
        c["percentage"]=round((c["percentage"]/total)*100,1)
    merged.sort(key=lambda x:x["percentage"],reverse=True)
    final_colors=merged[:top_n]
    # Recalculate properties
    for c in final_colors:
        props=get_color_properties(c["rgb"])
        c.update(props)
        c["score"]=calculate_color_score(c)
    return final_colors

# -----------------------------
# Shade Classification
# -----------------------------
def classify_shade(shade_name, colors):
    """Classify shade category and undertone."""
    avg_brightness=sum(c["brightness"]*c["percentage"]/100 for c in colors)
    dominant_tone=colors[0]["tone"] if colors else "neutral"
    dominant_undertone=colors[0]["undertone"] if colors else "neutral"
    if avg_brightness<40:
        category="Black"
        expected=["Natural Black","Jet Black"]
    elif avg_brightness<80:
        category="Dark Brown"
        expected=["Dark Brown","Cool Brown","Coffee","Sunkissed Brown"]
    elif avg_brightness<120:
        category="Medium Brown"
        expected=["Medium Brown","Autumn","Caramel","Toffee","Sandy","Soft Blended"]
    elif avg_brightness<150:
        category="Light Brown / Dark Blonde"
        expected=["Rooted","Teddy Bear","Old Money","Scandinavian"]
    elif avg_brightness<180:
        category="Blonde"
        expected=["Honey","Summer","Mixed","Luscious"]
    else:
        category="Light Blonde / Platinum"
        expected=["Champagne","Platinum","Silver","Ivory"]
    name_match=any(exp.lower() in shade_name.lower() for exp in expected)
    explanation=f"{category} shade"
    if "Balayage" in shade_name or "Rooted" in shade_name:
        explanation+=" with dimension (roots to ends)"
    if dominant_tone in ["warm_orange","warm_brown","golden"]:
        explanation+=", warm "+dominant_undertone+" undertone"
    elif dominant_tone=="cool":
        explanation+=", cool "+dominant_undertone+" undertone"
    else:
        explanation+=", neutral undertone"
    return {
        "category": category,
        "name_accurate": name_match,
        "explanation": explanation,
        "avg_brightness": round(avg_brightness,1),
        "dominant_tone": dominant_tone,
        "dominant_undertone": dominant_undertone
    }

# -----------------------------
# Pipeline Execution
# -----------------------------
def build_shade_database(shade_folder_path="new_shade"):
    shade_folder = Path(shade_folder_path)
    database={}
    analysis_report={}

    # Collect unique shade names
    shade_names=set()
    for img_file in shade_folder.glob("*.*"):
        if img_file.suffix.lower() in ['.jpg','.png','.jpeg']:
            name=img_file.stem
            for variant in ["_CloseUp","_IndoorLight","_NaturalLight","_light"]:
                name=name.replace(variant,"")
            shade_names.add(name)

    # Process each shade
    for shade_name in sorted(shade_names):
        all_colors=[]
        for img_file in shade_folder.glob(f"{shade_name}*.*"):
            if img_file.suffix.lower() in ['.jpg','.png','.jpeg']:
                try:
                    colors=analyze_image(img_file)
                    all_colors.extend(colors)
                except Exception as e:
                    print(f"Error with {img_file.name}: {e}")
        if not all_colors:
            continue
        final_colors=merge_colors(all_colors)
        database[shade_name]=final_colors
        analysis_report[shade_name]=classify_shade(shade_name, final_colors)
        print(f"{shade_name}: {len(final_colors)} colors, Category: {analysis_report[shade_name]['category']}")

    # Save JSON
    output_db = Path("app/shade/final_shades.json")
    output_report = Path("shade_analysis_report.json")
    output_db.parent.mkdir(parents=True, exist_ok=True)
    with open(output_db,"w") as f: json.dump(database,f,indent=2)
    with open(output_report,"w") as f: json.dump(analysis_report,f,indent=2)
    print(f"\n✓ Database saved: {output_db}")
    print(f"✓ Analysis report saved: {output_report}")
    return database, analysis_report

# -----------------------------
# Run Pipeline
# -----------------------------
if __name__=="__main__":
    build_shade_database("new_shade")
