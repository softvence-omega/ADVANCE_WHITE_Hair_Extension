import cv2
import numpy as np
from pathlib import Path
import json
from app.config import Settings
from app.services.hair_color_detector import detect_hair_color, detect_shade_color

DATA_DIR = Settings.NEW4_DATA_DIR

def average_rgb(image_path):
    img = cv2.imread(str(image_path))  # BGR format
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB
    h, w, c = img_rgb.shape
    rgb_pixels = img_rgb.reshape(h * w, c)
    avg_rgb = np.mean(rgb_pixels, axis=0)
    return np.round(avg_rgb).astype(int)  # Convert to integers

def process_shade_folder(shade_path):
    rgbs = []
    for img_file in shade_path.glob("*.jpg"):
        avg_rgb = average_rgb(img_file)
        rgbs.append(avg_rgb)
    if rgbs:
        return np.mean(rgbs, axis=0).round().astype(int)
    return None

import os
import os
from pathlib import Path
from app.services.hair_color_detector import detect_shade_color

def build_reference_shades(shade_folder: Path):
    """
    Process all images in a shade folder.
    Assign keys based on filename:
    - 'default' → if no suffix matches
    - 'closeup' → if 'CloseUp' in filename
    - 'indoor_light' → if 'IndoorLight' in filename
    - 'natural_light' → if 'NaturalLight' in filename
    """
    shade_info = {shade_folder.name: {}}

    for image_file in os.listdir(shade_folder):
        img_path = shade_folder / image_file
        if not img_path.is_file():
            continue

        filename_lower = image_file.lower()

        if "closeup" in filename_lower:
            key = "closeup"
        elif "indoor" in filename_lower:
            key = "indoor_light"
        elif "natural" in filename_lower:
            key = "natural_light"
        else:
            key = "default"

        # Run shade detection
        shade_info[shade_folder.name][key] = detect_shade_color(img_path)
        print(f"[INFO] Processed {key} → {img_path}")

    print(f"[DONE] Shade folder processed: {shade_folder.name}")
    return shade_info


def main():
    shade_signatures = {} 
    for shade_folder in DATA_DIR.iterdir():
        print(f"Processing shade folder: {shade_folder.name}")
        if shade_folder.is_dir():
            shades_data = build_reference_shades(shade_folder)
            shade_signatures.update(shades_data)  # dict merge
           
    # ✅ Save output
    os.makedirs("app/shade", exist_ok=True)
    with open("app/shade/reference_shades_new4.json", "w") as f:
        json.dump(shade_signatures, f, indent=2)
    


if __name__ == "__main__":
    main()
    
