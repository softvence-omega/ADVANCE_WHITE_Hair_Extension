import numpy as np
from sklearn.cluster import KMeans
import cv2

def filter_hair_pixels(hair_pixels, remove_highlights=True, remove_shadows=True):
    """Filter out highlights and shadows from hair pixels for better color detection"""
    if len(hair_pixels) == 0:
        return hair_pixels
    
    pixels = np.array(hair_pixels)
    filtered_pixels = []
    
    for pixel in pixels:
        r, g, b = pixel
        
        # Calculate brightness and saturation
        brightness = (r * 0.299 + g * 0.587 + b * 0.114)
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        
        # Skip very bright pixels (highlights)
        if remove_highlights and brightness > 200:
            continue
            
        # Skip very dark pixels (deep shadows) unless it's genuinely black hair
        if remove_shadows and brightness < 15:
            continue
            
        # Skip pixels with extreme saturation (likely noise)
        if max_val > 0 and (max_val - min_val) / max_val > 0.8 and brightness > 100:
            continue
            
        filtered_pixels.append(pixel)
    
    return filtered_pixels if filtered_pixels else hair_pixels

def get_improved_dominant_colors(hair_pixels, n_clusters=5, min_percentage=5):
    """Improved dominant color extraction with better filtering"""
    if len(hair_pixels) == 0:
        return [{"color": [0, 0, 0], "percentage": 0.0}]
    
    # Filter pixels to remove highlights and shadows
    filtered_pixels = filter_hair_pixels(hair_pixels)
    
    if len(filtered_pixels) < 10:  # Not enough pixels after filtering
        filtered_pixels = hair_pixels  # Use original pixels
    
    data = np.array(filtered_pixels)
    
    # Remove duplicate rows
    unique_colors = np.unique(data, axis=0)
    actual_clusters = min(len(unique_colors), n_clusters)
    
    if actual_clusters == 0:
        return [{"color": [0, 0, 0], "percentage": 0.0}]
    
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
                color = centers[i].tolist()
                
                # Ensure RGB values are in valid range
                color = [max(0, min(255, c)) for c in color]
                
                dominant_colors.append({
                    "color": color,
                    "percentage": round(percentage, 2)
                })
        
        # Sort by percentage (highest first)
        dominant_colors.sort(key=lambda x: x["percentage"], reverse=True)
        
        # If no colors meet the minimum percentage, return the most dominant one
        if not dominant_colors and actual_clusters > 0:
            most_dominant_idx = np.argmax(counts)
            color = centers[most_dominant_idx].tolist()
            color = [max(0, min(255, c)) for c in color]
            dominant_colors = [{
                "color": color,
                "percentage": round((counts[most_dominant_idx] / total) * 100, 2)
            }]
        
        return dominant_colors if dominant_colors else [{"color": [0, 0, 0], "percentage": 0.0}]
        
    except Exception as e:
        print(f"[ERROR] Improved KMeans failed: {e}")
        # Fallback to average color
        avg_color = data.mean(axis=0).astype(int).tolist()
        avg_color = [max(0, min(255, c)) for c in avg_color]
        return [{"color": avg_color, "percentage": 100.0}]

def analyze_hair_color_distribution(hair_pixels):
    """Analyze the distribution of hair colors to detect black hair better"""
    if len(hair_pixels) == 0:
        return {"is_black": False, "confidence": 0.0}
    
    pixels = np.array(hair_pixels)
    
    # Calculate brightness for all pixels
    brightness_values = []
    for pixel in pixels:
        r, g, b = pixel
        brightness = (r * 0.299 + g * 0.587 + b * 0.114)
        brightness_values.append(brightness)
    
    brightness_array = np.array(brightness_values)
    
    # Statistics
    mean_brightness = np.mean(brightness_array)
    median_brightness = np.median(brightness_array)
    std_brightness = np.std(brightness_array)
    
    # Count very dark pixels
    very_dark_count = np.sum(brightness_array < 50)
    dark_count = np.sum(brightness_array < 80)
    total_pixels = len(brightness_array)
    
    very_dark_ratio = very_dark_count / total_pixels
    dark_ratio = dark_count / total_pixels
    
    # Black hair indicators
    is_black_hair = (
        mean_brightness < 60 and
        median_brightness < 55 and
        very_dark_ratio > 0.6 and
        dark_ratio > 0.8
    )
    
    confidence = min(1.0, (very_dark_ratio + dark_ratio) / 2)
    
    return {
        "is_black": is_black_hair,
        "confidence": confidence,
        "mean_brightness": mean_brightness,
        "dark_pixel_ratio": dark_ratio
    }