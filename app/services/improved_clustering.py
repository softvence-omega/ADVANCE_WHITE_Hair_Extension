import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def preprocess_hair_image(hair_img):
    """Preprocess hair image to remove noise"""
    # Gaussian Blur
    blurred = cv2.GaussianBlur(hair_img, (5, 5), 0)
    # Morphological Closing
    kernel = np.ones((5, 5), np.uint8)
    cleaned = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)
    return cleaned

def normalize_lighting(img):
    """Normalize lighting using histogram equalization in LAB space"""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.equalizeHist(l)
    lab = cv2.merge((l, a, b))
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

def find_optimal_clusters(pixels, max_clusters=5):
    """Find optimal number of clusters using silhouette score"""
    if len(pixels) < 100:
        return 2
    
    best_k = 2
    best_score = -1
    
    for k in range(2, min(max_clusters + 1, len(pixels))):
        try:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(pixels)
            score = silhouette_score(pixels, labels)
            
            if score > best_score:
                best_score = score
                best_k = k
        except:
            continue
    
    return best_k

def extract_dominant_colors_lab(hair_img, auto_clusters=True):
    """Extract dominant colors using LAB color space"""
    # Preprocess
    cleaned = preprocess_hair_image(hair_img)
    
    # Normalize lighting
    normalized = normalize_lighting(cleaned)
    
    # Convert to LAB
    lab = cv2.cvtColor(normalized, cv2.COLOR_BGR2LAB)
    
    # Get non-zero pixels
    pixels = lab.reshape(-1, 3)
    
    # Remove very dark and very bright pixels
    brightness = pixels[:, 0]
    valid_mask = (brightness > 20) & (brightness < 235)
    valid_pixels = pixels[valid_mask]
    
    if len(valid_pixels) < 100:
        valid_pixels = pixels
    
    # Find optimal clusters
    if auto_clusters:
        n_clusters = find_optimal_clusters(valid_pixels)
    else:
        n_clusters = 5
    
    # KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(valid_pixels)
    
    # Get cluster centers and counts
    centers = kmeans.cluster_centers_
    counts = np.bincount(labels)
    total = len(labels)
    
    # Convert LAB centers to RGB
    colors = []
    for i in range(n_clusters):
        percentage = (counts[i] / total) * 100
        if percentage >= 2:
            # Convert LAB to RGB
            lab_color = np.uint8([[centers[i]]])
            rgb_color = cv2.cvtColor(lab_color, cv2.COLOR_LAB2RGB)[0][0]
            
            colors.append({
                "color": [int(c) for c in rgb_color],
                "percentage": round(percentage, 2)
            })
    
    # Sort by percentage
    colors.sort(key=lambda x: x["percentage"], reverse=True)
    
    return colors if colors else [{"color": [0, 0, 0], "percentage": 100.0}]