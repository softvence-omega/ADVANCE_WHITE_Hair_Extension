import os
import json
import numpy as np
import cv2
from PIL import Image
from pathlib import Path
from sklearn.cluster import KMeans
from app.config import Settings

DATA_DIR = Settings.NEW_DATA_DIR


def get_dominant_colors_from_hair(hair_pixels, n_clusters=3, min_percentage=3):
    """Cluster hair pixels and extract dominant colors with percentages."""
    if len(hair_pixels) == 0:
        return [{"color": [0, 0, 0], "percentage": 100.0}]
    
    data = np.array(hair_pixels)

    # Remove duplicate rows
    unique_colors = np.unique(data, axis=0)
    actual_clusters = min(len(unique_colors), n_clusters)

    if actual_clusters == 0:
        return [{"color": [0, 0, 0], "percentage": 100.0}]

    try:
        kmeans = KMeans(n_clusters=actual_clusters, random_state=42, n_init="auto")
        labels = kmeans.fit_predict(data)
        centers = kmeans.cluster_centers_.astype(int)

        counts = np.bincount(labels)
        total = len(labels)

        dominant_colors = []
        for i in range(actual_clusters):
            percentage = (counts[i] / total) * 100
            if percentage >= min_percentage:
                dominant_colors.append({
                    "color": centers[i].tolist(),
                    "percentage": round(percentage, 2)
                })

        if not dominant_colors:
            avg_color = data.mean(axis=0).astype(int).tolist()
            return [{"color": avg_color, "percentage": 100.0}]

        return dominant_colors

    except Exception as e:
        print(f"[ERROR] KMeans failed: {e}")
        avg_color = data.mean(axis=0).astype(int).tolist()
        return [{"color": avg_color, "percentage": 100.0}]


def detect_shade_color(input_path):
    """Extract dominant hair colors from an image."""
    img = Image.open(input_path).convert("RGB")
    img_rgb = np.array(img)  # (H, W, 3)

    pixels_array = img_rgb.reshape(-1, 3)
    pixels = np.array(pixels_array, dtype=np.uint8)

    print(f"[INFO] Extracted {len(pixels)} pixels from {input_path}")

    dominant_colors = get_dominant_colors_from_hair(
        pixels, n_clusters=3, min_percentage=3
    )

    return dominant_colors


def build_reference_shade(image_path: Path):
    """Process one file → dominant shade colors."""
    key = image_path.stem
    print(f"Processing image: {image_path}")

    dominant_colors = detect_shade_color(image_path)
    return {key: dominant_colors}


def main():
    shade_signatures = {}

    for image_file in DATA_DIR.iterdir():
        if image_file.is_file() and image_file.suffix.lower() in [".jpg", ".png", ".jpeg"]:
            shades_data = build_reference_shade(image_file)
            shade_signatures.update(shades_data)

    # ✅ Save output
    out_dir = Path("app/shade")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "reference_shades_new.json", "w") as f:
        json.dump(shade_signatures, f, indent=2)

    print(f"[DONE] Saved {len(shade_signatures)} shades → app/shade/reference_shades_new.json")


if __name__ == "__main__":
    main()
