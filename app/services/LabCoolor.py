import cv2
import numpy as np
from pathlib import Path
import json
from app.config import Settings


DATA_DIR = Settings.DATA_DIR

def rgb_to_lab(image_path):
    img = cv2.imread(str(image_path))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
    return img_lab

def average_lab(image_lab):
    # Flatten and average across pixels
    h, w, c = image_lab.shape
    lab_pixels = image_lab.reshape(h * w, c)
    avg = np.mean(lab_pixels, axis=0)
    return avg

def process_shade_folder(shade_path):
    labs = []
    for img_file in shade_path.glob("*.jpg"):
        lab_img = rgb_to_lab(img_file)
        avg_lab = average_lab(lab_img)
        labs.append(avg_lab)
    if labs:
        return np.mean(labs, axis=0)
    return None

def main():
    shade_signatures = {}
    for shade_folder in DATA_DIR.iterdir():
        if shade_folder.is_dir():
            signature = process_shade_folder(shade_folder)
            if signature is not None:
                shade_signatures[shade_folder.name] = signature.tolist()
                print(f"Processed shade: {shade_folder.name} -> {signature}")
    
    # Save to JSON
    with open("shade_lab_signatures.json", "w") as f:
        json.dump(shade_signatures, f, indent=2)

if __name__ == "__main__":
    main()