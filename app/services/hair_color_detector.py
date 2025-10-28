
from app.model import BiSeNet
import torch
import os.path as osp
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
import cv2
import json
import os
from sklearn.cluster import KMeans
from app.services.any_formate import load_image_any_format


def similar(G1, B1, R1, G2, B2, R2):
    ar = []
    if G2 > 30:
        ar.append(1000. * G1 / G2)
    if B2 > 30:
        ar.append(1000. * B1 / B2)
    if R2 > 30:
        ar.append(1000. * R1 / R2)
    if len(ar) < 1:
        return False
    if min(ar) == 0:
        return False
    br = max(R1, G1, B1) / max(G2, B2, R2)
    return max(ar) / min(ar) < 1.55 and br > 0.7 and br < 1.4


def rgb_to_hsv_simple(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    diff = max_c - min_c
    if diff == 0:
        h = 0
    elif max_c == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_c == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360
    s = 0 if max_c == 0 else (diff / max_c)
    v = max_c
    return h, s, v

def rgb_to_lab(rgb):
    """Convert RGB to Lab"""
    from colormath.color_objects import LabColor, sRGBColor
    from colormath.color_conversions import convert_color
    r, g, b = [x / 255.0 for x in rgb]
    rgb_color = sRGBColor(r, g, b)
    lab_color = convert_color(rgb_color, LabColor)
    return [lab_color.lab_l, lab_color.lab_a, lab_color.lab_b]

def classify_tone(rgb, h, s):
    r, g, b = rgb
    if h < 30 and s > 0.3 and r > g + 15:
        return "warm_orange"
    elif 30 <= h < 60 and s > 0.2:
        return "warm_brown"
    elif h < 40 and s < 0.2:
        return "neutral_brown"
    elif 40 <= h < 80 and s > 0.2:
        return "golden"
    elif 180 <= h < 270:
        return "cool"
    else:
        return "neutral"

def get_dominant_colors_from_hair(hair_pixels, n_clusters=6, min_percentage=5):
    if len(hair_pixels) == 0:
        return [{"color": [0, 0, 0], "percentage": 0.0, "tone": "neutral"}]
    
    data = np.array(hair_pixels)
    
    data = np.array(hair_pixels)
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
                color = [max(0, min(255, int(c))) for c in centers[i]]
                brightness_val = color[0] * 0.299 + color[1] * 0.587 + color[2] * 0.114
                h, s, v = rgb_to_hsv_simple(color)
                tone = classify_tone(color, h, s)
                lab = rgb_to_lab(color)
                
                dominant_colors.append({
                    "color": color,
                    "rgb": color,
                    "lab": [round(x, 2) for x in lab],
                    "percentage": round(percentage, 2),
                    "brightness": round(brightness_val, 2),
                    "hue": round(h, 2),
                    "saturation": round(s, 3),
                    "tone": tone
                })

        # Sort by percentage
        dominant_colors.sort(key=lambda x: x["percentage"], reverse=True)
        
        # Ensure at least one color
        if not dominant_colors:
            most_common_idx = np.argmax(counts)
            color = [max(0, min(255, int(c))) for c in centers[most_common_idx]]
            brightness_val = color[0] * 0.299 + color[1] * 0.587 + color[2] * 0.114
            h, s, v = rgb_to_hsv_simple(color)
            tone = classify_tone(color, h, s)
            dominant_colors = [{"color": color, "percentage": round((counts[most_common_idx] / total) * 100, 2), "tone": tone}]

        return dominant_colors

    except Exception as e:
        pass  # KMeans failed, use average
        avg_color = [max(0, min(255, int(c))) for c in data.mean(axis=0)]
        h, s, v = rgb_to_hsv_simple(avg_color)
        tone = classify_tone(avg_color, h, s)
        return [{"color": avg_color, "percentage": 100.0, "tone": tone}]

def vis_parsing_maps(im, origin, parsing_anno, stride):
    # Resize mask to match original image size
    vis_parsing_anno = parsing_anno.copy().astype(np.uint8)
    vis_parsing_anno = cv2.resize(vis_parsing_anno, (origin.shape[1], origin.shape[0]), interpolation=cv2.INTER_NEAREST)

    hair_pixels = []

    # Extract hair pixels directly from original image
    for x in range(origin.shape[0]):
        for y in range(origin.shape[1]):
            if vis_parsing_anno[x][y] == 17:  # 17 = hair
                b, g, r = origin[x, y]
                hair_pixels.append([r, g, b])  # RGB

    # Detected hair pixels
    # Use 6 clusters with 5% minimum to get accurate hair colors
    dominant_colors = get_dominant_colors_from_hair(hair_pixels, n_clusters=6, min_percentage=5)
    
    # Mark base color (darkest with highest percentage)
    if dominant_colors:
        darkest = min(dominant_colors, key=lambda x: x["color"][0] * 0.299 + x["color"][1] * 0.587 + x["color"][2] * 0.114)
        darkest_brightness = darkest["color"][0] * 0.299 + darkest["color"][1] * 0.587 + darkest["color"][2] * 0.114
        
        if darkest_brightness < 80 and darkest["percentage"] > 40:
            darkest["is_base_color"] = True

    with open("hair_rgb.json", "w") as f:
        json.dump({"dominant_hair_colors": dominant_colors}, f)




def highlight_hair_region(origin, parsing_anno, stride=1):
    vis_parsing_anno = parsing_anno.copy().astype(np.uint8)
    vis_parsing_anno = cv2.resize(vis_parsing_anno, (origin.shape[1], origin.shape[0]), interpolation=cv2.INTER_NEAREST)
    
    hair_mask = (vis_parsing_anno == 17).astype(np.uint8) * 255
    
    kernel = np.ones((5,5), np.uint8)
    hair_mask = cv2.morphologyEx(hair_mask, cv2.MORPH_CLOSE, kernel)
    
    # Save only hair with transparent background
    b, g, r = cv2.split(origin)
    rgba = cv2.merge([b, g, r, hair_mask])
    cv2.imwrite("highlighted_hair.png", rgba)
    
    return hair_mask

def normalize_lighting(img):
    """Gray World lighting normalization"""
    img_float = img.astype(np.float32)
    avg_b = np.mean(img_float[:, :, 0])
    avg_g = np.mean(img_float[:, :, 1])
    avg_r = np.mean(img_float[:, :, 2])
    gray = (avg_r + avg_g + avg_b) / 3
    scale_b = gray / (avg_b + 1e-6)
    scale_g = gray / (avg_g + 1e-6)
    scale_r = gray / (avg_r + 1e-6)
    img_float[:, :, 0] = np.clip(img_float[:, :, 0] * scale_b, 0, 255)
    img_float[:, :, 1] = np.clip(img_float[:, :, 1] * scale_g, 0, 255)
    img_float[:, :, 2] = np.clip(img_float[:, :, 2] * scale_r, 0, 255)
    return img_float.astype(np.uint8)

def evaluate(cp='model/model.pth', input_path='', original_path=''):
    n_classes = 19
    device = torch.device('cpu')
    net = BiSeNet(n_classes=n_classes)
    net.cpu()
    save_pth = osp.join('', cp)
    net.load_state_dict(torch.load(save_pth, map_location=torch.device('cpu')))
    net.eval()

    # Load ORIGINAL image for color extraction
    if original_path and os.path.exists(original_path):
        pil_img_original = load_image_any_format(original_path)
        origin = np.array(pil_img_original)[:, :, ::-1].copy()  # RGB → BGR
    else:
        pil_img_original = load_image_any_format(input_path)
        origin = np.array(pil_img_original)[:, :, ::-1].copy()
    
    # DON'T normalize user hair - keep original colors
    # origin = normalize_lighting(origin)
    
    # Load image for segmentation
    pil_img = load_image_any_format(input_path)  # PIL Image (RGB)

    # Preprocess for model
    to_tensor = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ])
    image_resized = pil_img.resize((512, 512))
    img_tensor = to_tensor(image_resized)
    img_tensor = torch.unsqueeze(img_tensor, 0).to(device)

    # Run inference
    with torch.no_grad():
        out = net(img_tensor)[0]
        parsing = out.squeeze(0).cpu().numpy().argmax(0)

    # Get hair mask and save image
    hair_mask = highlight_hair_region(origin, parsing, stride=1)
    
    # Load saved hair image and extract colors
    hair_img = cv2.imread("highlighted_hair.png", cv2.IMREAD_UNCHANGED)
    if hair_img.shape[2] == 4:  # RGBA
        hair_pixels = []
        for x in range(hair_img.shape[0]):
            for y in range(hair_img.shape[1]):
                if hair_img[x, y, 3] > 0:  # alpha > 0
                    b, g, r, a = hair_img[x, y]
                    hair_pixels.append([r, g, b])
        
        dominant_colors = get_dominant_colors_from_hair(hair_pixels, n_clusters=6, min_percentage=5)
        with open("hair_rgb.json", "w") as f:
            json.dump({"dominant_hair_colors": dominant_colors}, f)
    else:
        # Fallback to original method
        vis_parsing_maps(image_resized, origin, parsing, stride=1)

def detect_shade_color(input_path):
    img = Image.open(input_path).convert("RGB")
    img_rgb = np.array(img)  # shape (H, W, 3)
    pixels_array = img_rgb.reshape(-1, 3)  # shape (num_pixels, 3)

    # Convert each pixel's each channel to np.uint8 explicitly (redundant but for safety)
    pixels= [[np.uint8(ch) for ch in pixel] for pixel in pixels_array]
   
    print(len(pixels))

    dominant_colors = get_dominant_colors_from_hair(pixels, n_clusters=6, min_percentage=5)

    with open("shade_rgb.json", "w") as f:
        json.dump({"dominant_hair_colors": dominant_colors}, f)
    with open("shade_rgb.json", "r") as f:
        shade_rgb = json.load(f)
    os.remove("shade_rgb.json")  # Clean up temp file
    
    return shade_rgb["dominant_hair_colors"]

        

def detect_hair_color(input_path='files/1.JPG', original_path=''):
    evaluate(input_path=input_path, original_path=original_path)
    with open("hair_rgb.json", "r") as f:
        hair_rgb = json.load(f)
    os.remove("hair_rgb.json")  # Clean up temp file
    return hair_rgb["dominant_hair_colors"]


if __name__ == "__main__":
    hair_rgb = detect_hair_color(input_path='image.png')
    # hair_rgb = detect_shade_color(input_path='image.png')
    print(json.dumps(hair_rgb))