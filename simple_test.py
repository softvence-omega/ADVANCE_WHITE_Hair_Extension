import cv2
import numpy as np
from sklearn.cluster import KMeans
import json

def get_color(img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (100, 100))
    img = img.reshape((-1, 3))
    
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(img)
    
    colors = kmeans.cluster_centers_
    counts = np.bincount(kmeans.labels_)
    dominant = colors[np.argmax(counts)]
    
    return dominant.astype(int).tolist()

def distance(c1, c2):
    return np.linalg.norm(np.array(c1) - np.array(c2))

# Test
target = get_color("1h.png")
print(f"Target color: {target}")

with open("app/shade/kmeans_shade_signatures.json") as f:
    shades = json.load(f)

results = {}
for name, data in shades.items():
    min_dist = min(distance(target, shade_rgb) for shade_rgb in data['dominant_colors'])
    results[name] = min_dist

sorted_results = sorted(results.items(), key=lambda x: x[1])
print("\nTop 5:")
for name, dist in sorted_results[:5]:
    print(f"{name}: {dist:.2f}")
