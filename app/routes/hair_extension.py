# app/routes/hair_extension.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import cv2
import json
import numpy as np
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie2000
from pathlib import Path
from app.config import settings

router = APIRouter()

TEMP_UPLOAD_DIR = settings.TEMP_DIR
SHADE_SIGNATURE_FILE = settings.SHADE_JSON

def extract_lab_signature_from_image(image_path: str) -> list:
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")
    image_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    pixels = image_lab.reshape((-1, 3))
    # Filter pixels (optional thresholding to remove noise)
    mask = (pixels[:, 0] > 20) & (pixels[:, 0] < 240)
    valid_pixels = pixels[mask]
    if valid_pixels.size == 0:
        raise ValueError(f"No valid LAB pixels in image: {image_path}")
    mean_lab = np.mean(valid_pixels, axis=0)
    return mean_lab.tolist()

def calculate_delta_e(lab1, lab2) -> float:
    color1 = LabColor(lab_l=lab1[0], lab_a=lab1[1], lab_b=lab1[2])
    color2 = LabColor(lab_l=lab2[0], lab_a=lab2[1], lab_b=lab2[2])
    return delta_e_cie2000(color1, color2)

@router.post("/hair/upload")
async def upload_image(file: UploadFile = File(...)):
    os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)
    temp_image_path = TEMP_UPLOAD_DIR / file.filename

    contents = await file.read()
    with open(temp_image_path, "wb") as f:
        f.write(contents)

    try:
        uploaded_lab = extract_lab_signature_from_image(str(temp_image_path))

        if not SHADE_SIGNATURE_FILE.exists():
            raise HTTPException(status_code=500, detail="Shade signature file missing")

        with open(SHADE_SIGNATURE_FILE, "r") as f:
            shade_signatures = json.load(f)

        shade_scores = []
        for shade_name, shade_lab in shade_signatures.items():
            delta_e = calculate_delta_e(uploaded_lab, shade_lab)
            shade_scores.append({"shade": shade_name, "delta_e": delta_e})

        shade_scores.sort(key=lambda x: x["delta_e"])
        top_matches = shade_scores[:5]  # Return top 5 matches

        return JSONResponse(content={"previews": top_matches})

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        if temp_image_path.exists():
            temp_image_path.unlink()
