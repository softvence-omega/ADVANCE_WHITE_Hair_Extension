
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


def get_dominant_colors_from_hair(hair_pixels, n_clusters=3, min_percentage=3):
    # print(f"Extracting dominant colors from hair pixels...{hair_pixels}")
    # if len(hair_pixels) == 0:
    #     return [{"color": [0, 0, 0], "percentage": 100.0}]
    
    data = np.array(hair_pixels)

    # Remove duplicate rows to avoid KMeans warning
    unique_colors = np.unique(data, axis=0)
    actual_clusters = min(len(unique_colors), n_clusters)

    if actual_clusters == 0:
        print("there is no cluster [{color: [0, 0, 0], percentage: 100.0}]")
        # return [{"color": [0, 0, 0], "percentage": 100.0}]
        return {"status_code": 400, "error": "No valid clusters could be formed from hair pixels."}

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

        # Ensure at least one color is returned
        if not dominant_colors:
            avg_color = data.mean(axis=0).astype(int).tolist()
            print("there is no dominant color: [{color: [0, 0, 0], percentage: 100.0}]" )
            return {"status_code": 400, "error": "No dominant color met the minimum percentage threshold."}

        # return dominant_colors
        return {
            "status_code": 200,                 # 200 = success, 400/500 = error
            "dominant_hair_colors": dominant_colors,      # list of dicts, empty or filled
            "message": "Hair color matched successfully."  # error/success message
        }

    # except Exception as e:
    #     print(f"[ERROR] KMeans failed: {e}")
    #     avg_color = data.mean(axis=0).astype(int).tolist()
    #     return [{"color": avg_color, "percentage": 100.0}]
    except Exception as e:
        print(f"[ERROR] KMeans failed: {e}")
        return {
            "status_code": 500,
            "dominant_hair_colors": [],
            "message": f"Failed to extract dominant hair colors: {str(e)}"
        }

def vis_parsing_maps(im, origin, parsing_anno, stride):

    im = np.array(im)
    vis_parsing_anno = parsing_anno.copy().astype(np.uint8)
    vis_parsing_anno = cv2.resize(vis_parsing_anno, None, fx=stride, fy=stride, interpolation=cv2.INTER_NEAREST)

    hair_pixels = []

    for x in range(origin.shape[0]):
        for y in range(origin.shape[1]):
            _x = int(x * 512 / origin.shape[0])
            _y = int(y * 512 / origin.shape[1])
            if vis_parsing_anno[_x][_y] == 17:  # 17 = hair
                b, g, r = origin[x, y]
                hair_pixels.append([r, g, b])  # RGB

    print("hair pixel--------------", len(hair_pixels))
    if len(hair_pixels) == 0 :
        return {
            "status_code": 400,
            "error": "No hair pixels detected. Please upload a clear image with visible hair for processing."
        }

    response = get_dominant_colors_from_hair(hair_pixels, n_clusters=3, min_percentage=3)
    print("get dominant color--------------", response['dominant_hair_colors'])
    if response['status_code'] == 400:
        return response

    with open("hair_rgb.json", "w") as f:
        json.dump({"dominant_hair_colors": response['dominant_hair_colors']}, f)
        return {"status_code": 200}




# def highlight_hair_region(origin, parsing_anno, stride=1):
#     # Resize parsing map to original image scale
#     vis_parsing_anno = parsing_anno.copy().astype(np.uint8)
#     vis_parsing_anno = cv2.resize(vis_parsing_anno, (origin.shape[1], origin.shape[0]), interpolation=cv2.INTER_NEAREST)
    
#     # Create a mask where hair label == 17
#     hair_mask = (vis_parsing_anno == 17).astype(np.uint8) * 255  # binary mask 0 or 255
    
#     # Optional: smooth the mask a bit
#     kernel = np.ones((5,5), np.uint8)
#     hair_mask = cv2.morphologyEx(hair_mask, cv2.MORPH_CLOSE, kernel)
    
#     # Create an overlay with hair highlighted in color (e.g., green)
#     overlay = origin.copy()
#     overlay[hair_mask == 255] = [0, 255, 0]  # green highlight on hair pixels (BGR)
    
#     # Blend original and overlay
#     highlighted = cv2.addWeighted(origin, 0.7, overlay, 0.3, 0)
    
#     # Save highlighted hair image
#     cv2.imwrite("highlighted_hair.png", highlighted)
    
#     return highlighted
import cv2
import numpy as np

def highlight_hair_region(origin, parsing_anno, stride=1, bottom_fraction=0.5):
    # Resize parsing map to original image scale
    vis_parsing_anno = parsing_anno.copy().astype(np.uint8)
    vis_parsing_anno = cv2.resize(vis_parsing_anno, (origin.shape[1], origin.shape[0]), interpolation=cv2.INTER_NEAREST)
    
    # Create a mask where hair label == 17
    hair_mask = (vis_parsing_anno == 17).astype(np.uint8) * 255  # binary mask 0 or 255
    
    # Optional: smooth the mask
    kernel = np.ones((5,5), np.uint8)
    hair_mask = cv2.morphologyEx(hair_mask, cv2.MORPH_CLOSE, kernel)
    
    # Find hair bounding box
    ys, xs = np.where(hair_mask == 255)
    if len(ys) == 0:  # no hair detected
        return origin
    y_min, y_max = ys.min(), ys.max()
    
    # Only keep bottom part
    y_cut = int(y_min + (y_max - y_min) * (1 - bottom_fraction))
    bottom_mask = np.zeros_like(hair_mask)
    bottom_mask[y_cut:y_max, :] = hair_mask[y_cut:y_max, :]
    
    # Create overlay with bottom hair highlighted in green
    overlay = origin.copy()
    overlay[bottom_mask == 255] = [0, 255, 0]  # BGR
    
    # Blend original and overlay
    highlighted = cv2.addWeighted(origin, 0.7, overlay, 0.3, 0)
    
    # Save highlighted image
    cv2.imwrite("highlighted_hair_bottom.png", highlighted)
    
    return highlighted


def evaluate(cp='model/model.pth', input_path=''):
    n_classes = 19
    # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    device = torch.device('cpu')
    print(f"Using device: {device}")
    n_classes = 19
    net = BiSeNet(n_classes=n_classes)
    net.cpu()
    save_pth = osp.join('', cp)
    net.load_state_dict(torch.load(save_pth, map_location=torch.device('cpu')))
    net.eval()

    # Load image universally
    pil_img = load_image_any_format(input_path)  # PIL Image (RGB)
    origin = np.array(pil_img)[:, :, ::-1].copy()  # Convert RGB → BGR for OpenCV

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

    # Hair region + color
    highlight_hair_region(origin, parsing, stride=1)
    
    response = vis_parsing_maps(image_resized, origin, parsing, stride=1)
    return response

def detect_shade_color(input_path):
    img = Image.open(input_path).convert("RGB")
    img_rgb = np.array(img)  # shape (H, W, 3)
    pixels_array = img_rgb.reshape(-1, 3)  # shape (num_pixels, 3)

    # Convert each pixel's each channel to np.uint8 explicitly (redundant but for safety)
    pixels= [[np.uint8(ch) for ch in pixel] for pixel in pixels_array]
   
    print(len(pixels))

    dominant_colors = get_dominant_colors_from_hair(pixels, n_clusters=3, min_percentage=3)

    with open("shade_rgb.json", "w") as f:
        json.dump({"dominant_hair_colors": dominant_colors}, f)
    with open("shade_rgb.json", "r") as f:
        shade_rgb = json.load(f)
    os.remove("shade_rgb.json")  # Clean up temp file
    
    return shade_rgb["dominant_hair_colors"]

        

def detect_hair_color(input_path='files/1.JPG'):
    response = evaluate(input_path=input_path)
    print("response----------------", response)
    return response


if __name__ == "__main__":
    # hair_rgb = detect_hair_color(input_path='image.png')
    # # hair_rgb = detect_shade_color(input_path='image.png')
    # print(json.dumps(hair_rgb))
    pass