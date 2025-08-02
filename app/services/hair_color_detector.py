
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

# def vis_parsing_maps(im, origin, parsing_anno, stride):
#     im = np.array(im)
#     vis_parsing_anno = parsing_anno.copy().astype(np.uint8)
#     vis_parsing_anno = cv2.resize(vis_parsing_anno, None, fx=stride, fy=stride, interpolation=cv2.INTER_NEAREST)

#     SB = 0
#     SR = 0
#     SG = 0
#     cnt = 0
#     FB = 0
#     FR = 0
#     FG = 0
#     FN = 0
#     for x in range(origin.shape[0]):
#         for y in range(origin.shape[1]):
#             _x = int(x * 512 / origin.shape[0])
#             _y = int(y * 512 / origin.shape[1])
#             if vis_parsing_anno[_x][_y] == 1:
#                 FB += int(origin[x][y][0])
#                 FG += int(origin[x][y][1])
#                 FR += int(origin[x][y][2])
#                 FN += 1
#     if FN > 0:
#         FB = int(FB / FN)
#         FR = int(FR / FN)
#         FG = int(FG / FN)
#     for x in range(origin.shape[0]):
#         for y in range(origin.shape[1]):
#             _x = int(x * 512 / origin.shape[0])
#             _y = int(y * 512 / origin.shape[1])
#             if vis_parsing_anno[_x][_y] == 17:
#                 OB = int(origin[x][y][0])
#                 OG = int(origin[x][y][1])
#                 OR = int(origin[x][y][2])
#                 if similar(OB, OG, OR, FB, FG, FR):
#                     continue
#                 SB += OB
#                 SG += OG
#                 SR += OR
#                 cnt += 1
#     if cnt > 0:
#         SB = int(SB / cnt)
#         SG = int(SG / cnt)
#         SR = int(SR / cnt)
#     else:
#         SB = SG = SR = 0

#     avg_hair_rgb = {"average_hair_rgb": [SR, SG, SB]}  # Convert BGR to RGB
#     with open("hair_rgb.json", "w") as f:
#         json.dump(avg_hair_rgb, f)



def get_dominant_colors_from_hair(hair_pixels, n_clusters=3, min_percentage=3):
    # print(f"Extracting dominant colors from hair pixels...{hair_pixels}")
    if len(hair_pixels) == 0:
        return [{"color": [0, 0, 0], "percentage": 100.0}]
    
    data = np.array(hair_pixels)

    # Remove duplicate rows to avoid KMeans warning
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

        # Ensure at least one color is returned
        if not dominant_colors:
            avg_color = data.mean(axis=0).astype(int).tolist()
            return [{"color": avg_color, "percentage": 100.0}]

        return dominant_colors

    except Exception as e:
        print(f"[ERROR] KMeans failed: {e}")
        avg_color = data.mean(axis=0).astype(int).tolist()
        return [{"color": avg_color, "percentage": 100.0}]

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

    dominant_colors = get_dominant_colors_from_hair(hair_pixels, n_clusters=3, min_percentage=3)

    with open("hair_rgb.json", "w") as f:
        json.dump({"dominant_hair_colors": dominant_colors}, f)




def highlight_hair_region(origin, parsing_anno, stride=1):
    # Resize parsing map to original image scale
    vis_parsing_anno = parsing_anno.copy().astype(np.uint8)
    vis_parsing_anno = cv2.resize(vis_parsing_anno, (origin.shape[1], origin.shape[0]), interpolation=cv2.INTER_NEAREST)
    
    # Create a mask where hair label == 17
    hair_mask = (vis_parsing_anno == 17).astype(np.uint8) * 255  # binary mask 0 or 255
    
    # Optional: smooth the mask a bit
    kernel = np.ones((5,5), np.uint8)
    hair_mask = cv2.morphologyEx(hair_mask, cv2.MORPH_CLOSE, kernel)
    
    # Create an overlay with hair highlighted in color (e.g., green)
    overlay = origin.copy()
    overlay[hair_mask == 255] = [0, 255, 0]  # green highlight on hair pixels (BGR)
    
    # Blend original and overlay
    highlighted = cv2.addWeighted(origin, 0.7, overlay, 0.3, 0)
    
    # Save highlighted hair image
    cv2.imwrite("highlighted_hair.png", highlighted)
    
    return highlighted

def evaluate(cp='model/model.pth', input_path=''):
    # n_classes = 19
    # net = BiSeNet(n_classes=n_classes)
    # net.cpu()
    # save_pth = osp.join('', cp)
    # net.load_state_dict(torch.load(save_pth, map_location=torch.device('cpu')))
    # net.eval()

    n_classes = 19
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')  # Check for GPU
    print(f"Using device------------: {device}")
    net = BiSeNet(n_classes=n_classes)
    net.to(device)  # Move model to GPU (if available)

    save_pth = osp.join('', cp)
    net.load_state_dict(torch.load(save_pth, map_location=device))  # Load to correct device
    net.eval()

    to_tensor = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ])
    with torch.no_grad():
        img = Image.open(input_path).convert("RGB")
        origin = cv2.imread(input_path, cv2.IMREAD_COLOR)  # BGR image
        image = img.resize((512,512))
        img = to_tensor(image)
        img = torch.unsqueeze(img, 0)
        img = img.to(device)
        out = net(img)[0]
        parsing = out.squeeze(0).cpu().numpy().argmax(0)

        # Hair region visualization
        highlight_hair_region(origin, parsing, stride=1)

        # Hair color extraction
        vis_parsing_maps(image, origin, parsing, stride=1)
        

def detect_hair_color(input_path='files/1.JPG'):
    evaluate(input_path=input_path)
    with open("hair_rgb.json", "r") as f:
        hair_rgb = json.load(f)
    os.remove("hair_rgb.json")  # Clean up temp file
    return hair_rgb["dominant_hair_colors"]


if __name__ == "__main__":
    hair_rgb = detect_hair_color(input_path='image.png')
    print(json.dumps(hair_rgb))