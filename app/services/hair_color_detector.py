from app.model import BiSeNet
import torch
import os.path as osp
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
import cv2
import json

def similar(G1,B1,R1,G2,B2,R2):
    ar=[]
    if G2 > 30:
        ar.append(1000.*G1/G2)
    if B2 > 30:
        ar.append(1000.*B1/B2)
    if R2 > 30:
        ar.append(1000.*R1/R2)
    if len(ar) < 1:
        return False
    if min(ar) == 0:
        return False
    br = max(R1,G1,B1) / max(G2,B2,R2)
    return max(ar) / min(ar) < 1.55 and br > 0.7 and br < 1.4

def vis_parsing_maps(im, origin, parsing_anno, stride):
    im = np.array(im)
    vis_parsing_anno = parsing_anno.copy().astype(np.uint8)
    vis_parsing_anno = cv2.resize(vis_parsing_anno, None, fx=stride, fy=stride, interpolation=cv2.INTER_NEAREST)

    SB = 0
    SR = 0
    SG = 0
    cnt = 0
    FB = 0
    FR = 0
    FG = 0
    FN = 0
    for x in range(origin.shape[0]):
        for y in range(origin.shape[1]):
            _x = int(x * 512 / origin.shape[0])
            _y = int(y * 512 / origin.shape[1])
            if vis_parsing_anno[_x][_y] == 1:
                FB += int(origin[x][y][0])
                FG += int(origin[x][y][1])
                FR += int(origin[x][y][2])
                FN += 1
    if FN > 0:
        FB = int(FB / FN)
        FR = int(FR / FN)
        FG = int(FG / FN)
    for x in range(origin.shape[0]):
        for y in range(origin.shape[1]):
            _x = int(x * 512 / origin.shape[0])
            _y = int(y * 512 / origin.shape[1])
            if vis_parsing_anno[_x][_y] == 17:
                OB = int(origin[x][y][0])
                OG = int(origin[x][y][1])
                OR = int(origin[x][y][2])
                if similar(OB,OG,OR,FB,FG,FR):
                    continue
                SB += OB
                SG += OG
                SR += OR
                cnt += 1
    if cnt > 0:
        SB = int(SB / cnt)
        SG = int(SG / cnt)
        SR = int(SR / cnt)
    else:
        SB = SG = SR = 0

    avg_hair_rgb = {"average_hair_rgb": [SR, SG, SB]}  # Convert BGR to RGB
    with open("hair_rgb.json", "w") as f:
        json.dump(avg_hair_rgb, f)

def evaluate(cp='model/model.pth', input_path=''):
    n_classes = 19
    net = BiSeNet(n_classes=n_classes)
    net.cpu()
    save_pth = osp.join('', cp)
    net.load_state_dict(torch.load(save_pth, map_location=torch.device('cpu')))
    net.eval()

    to_tensor = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ])
    with torch.no_grad():
        img = Image.open(input_path).convert("RGB")
        origin = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        image = img.resize((512,512))
        img = to_tensor(image)
        img = torch.unsqueeze(img, 0)
        img = img.cpu()
        out = net(img)[0]
        parsing = out.squeeze(0).cpu().numpy().argmax(0)
        vis_parsing_maps(image, origin, parsing, stride=1)

import os
def detect_hair_color(input_path='files/1.JPG'):
    evaluate(input_path=input_path)
    with open("hair_rgb.json", "r") as f:
        hair_rgb = json.load(f)
    os.remove("hair_rgb.json")  # Clean up the temporary file
    return hair_rgb["average_hair_rgb"]


if __name__ == "__main__":
    hair_rgb = detect_hair_color(input_path='files/1.JPG')
    print(json.dumps(hair_rgb))