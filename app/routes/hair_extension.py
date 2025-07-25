from fastapi import APIRouter, UploadFile, File
from PIL import Image
import numpy as np
import json
from app.utils.color_matcher import match_shade_rgb, load_shades_rgb
from app.config import SHADE_PATH

router = APIRouter()

@router.post("/match-hair-color/")
async def match_hair_color(file: UploadFile = File(...)):
    # Step 1: Load the image
    image = Image.open(file.file).convert("RGB")
    image_np = np.array(image)

    # Step 2: Compute average hair color (simplified version)
    avg_rgb = image_np.reshape(-1, 3).mean(axis=0).tolist()

    # Step 3: Load shade data & match
    shade_data = load_shades_rgb(SHADE_PATH)
    matched_name, matched_rgb, delta = match_shade_rgb(avg_rgb, shade_data)

    return {
        "user_rgb": avg_rgb,
        "matched_shade": matched_name,
        "shade_rgb": matched_rgb,
        "delta_e": delta
    }
