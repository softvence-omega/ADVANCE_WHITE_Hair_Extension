import cv2
import numpy as np
from sklearn.cluster import KMeans
import os
import json
from collections import defaultdict

def get_dominant_colors(img_path, k=3):
    img = cv2.imread(img_path)
    if img is None:
        return None
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (100, 100))
    img = img.reshape((-1, 3))

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(img)
    
    colors = kmeans.cluster_centers_
    return [color.astype(int).tolist() for color in colors]

def process_shade_folder(folder_path="new_shade", k=3):
    shade_data = defaultdict(list)
    
    for file in os.listdir(folder_path):
        if file.endswith(('.jpg', '.png', '.jpeg')):
            shade_name = file.rsplit('.', 1)[0]
            for suffix in ['_CloseUp', '_IndoorLight', '_light', '_NaturalLight']:
                shade_name = shade_name.replace(suffix, '')
            
            img_path = os.path.join(folder_path, file)
            colors = get_dominant_colors(img_path, k)
            
            if colors:
                shade_data[shade_name].extend(colors)
    
    final_data = {}
    for shade_name, colors in shade_data.items():
        final_data[shade_name] = {"dominant_colors": colors}
    
    return final_data

print("Processing shade images with KMeans clustering...")
shade_signatures = process_shade_folder("new_shade", k=3)

output_path = "app/shade/kmeans_shade_signatures.json"
with open(output_path, 'w') as f:
    json.dump(shade_signatures, f, indent=2)

print(f"Generated {output_path}")
print(f"Total shades: {len(shade_signatures)}")
for shade, data in list(shade_signatures.items())[:2]:
    print(f"{shade}: {len(data['dominant_colors'])} colors")
