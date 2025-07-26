import cv2
import numpy as np
from pathlib import Path
import json
from app.config import Settings

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

def main():
    shade_signatures = {}
    for shade_folder in DATA_DIR.iterdir():
        if shade_folder.is_dir():
            signature = process_shade_folder(shade_folder)
            if signature is not None:
                shade_signatures[shade_folder.name] = signature.tolist()
                print(f"Processed shade: {shade_folder.name} -> {signature}")
    
    with open("shade_rgb_signatures.json", "w") as f:
        json.dump(shade_signatures, f, indent=2)

if __name__ == "__main__":
    main()
