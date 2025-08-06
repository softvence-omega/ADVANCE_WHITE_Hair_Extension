import cv2
import numpy as np
from pathlib import Path
import json
from app.config import Settings
from app.services.hair_color_detector import detect_hair_color, detect_shade_color

DATA_DIR = Settings.DATA_DIR

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
def build_reference_shades(data_dir):
    
    shade_info = {data_dir.name: {}}
    for image_file in os.listdir(data_dir):
        img_path = os.path.join(data_dir, image_file)
        print(f"Processing image: {img_path}")
        if not os.path.isfile(img_path):
            continue

        if "CloseUp" in image_file:
            key = "closeup"
        elif "IndoorLight" in image_file:
            key = "indoor_light"
        elif "NaturalLight" in image_file:
            key = "natural_light"
        else:
            print("filename not found")
            continue

        # shade_info[data_dir.name][key] = detect_hair_color(img_path)
        shade_info[data_dir.name][key] = detect_shade_color(img_path)
        print("shade_info:", shade_info)

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
    with open("app/shade/reference_shades.json", "w") as f:
        json.dump(shade_signatures, f, indent=2)
    


if __name__ == "__main__":
    main()
    
