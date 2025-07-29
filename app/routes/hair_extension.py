from fastapi import APIRouter, UploadFile, File,HTTPException
from PIL import Image
import numpy as np
import json
from app.utils.color_matcher import match_shade_rgb, load_shades_rgb
from app.config import Settings
from app.services.hair_color_detector import detect_hair_color
import os
import shutil
SHADE_PATH = Settings.SHADE_PATH
router = APIRouter()

@router.post("/match-hair-color")
async def match_hair_color(file: UploadFile = File(...)):
    try:
        Settings.ensure_directories()  # Ensure all directories exist
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        user_rgb = detect_hair_color(input_path=temp_path)
        print("user_rgb-------------", user_rgb)
        os.remove(temp_path)  # Clean up the temporary file

        # Step 3: Load shade data & match
        shade_data = load_shades_rgb(Settings.SHADE_PATH)
        print("shade_data-------------", shade_data)
        matched_name, matched_rgb, delta = match_shade_rgb(user_rgb, shade_data)

        return {
            "user_hair_rgb": user_rgb,
            "matched_shade": matched_name,
            "product_shade_rgb": matched_rgb,
            "delta_e": delta
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
