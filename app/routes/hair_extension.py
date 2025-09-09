# from fastapi import APIRouter, UploadFile, File,HTTPException
# from PIL import Image
# import numpy as np
# import json
# from app.config import Settings
# from app.services.hair_color_detector import detect_hair_color
# from app.services.best_shade_matcher import find_best_shade
# from app.services.background_remove import remove_background
# import os
# import shutil
# SHADE_PATH = Settings.SHADE_PATH
# router = APIRouter()

# from pathlib import Path
# def load_shades_rgb(path):
#     path = Path(path)
#     if not path.exists():
#         raise FileNotFoundError(f"Shade data file not found at: {path}")
        
#     with path.open("r") as f:
#         return json.load(f)

# @router.post("/match-hair-color")
# async def match_hair_color(file: UploadFile = File(...)):
#     try:
#         Settings.ensure_directories()  # Ensure all directories exist
#         temp_path = f"temp_{file.filename}"
#         #step1: first remove background
#         remove_background(file.file, temp_path)
#         with open(temp_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
#         user_rgb = detect_hair_color(input_path=temp_path)
#         print("user_rgb-------------", user_rgb)
#         os.remove(temp_path)  # Clean up the temporary file

#         # Step 3: Load shade data & match
#         shade_data = load_shades_rgb(Settings.SHADE_PATH)
#         print("shade_data-------------", shade_data)
#         # matched_name, matched_rgb, delta = match_shade_rgb(user_rgb, shade_data)

#         best, all_scores = find_best_shade(user_rgb, shade_data)

#         print("best-------------", best)
#         print("all_scores-------------", all_scores)

#         return {
#             # "user_hair_rgb": user_rgb,
#             "matched_shade": best,
#             # "product_shade_rgb": matched_rgb,
#             "match_percentage": all_scores[best],
#             "all_scores": all_scores
#         }
#     except FileNotFoundError as e:
#         raise HTTPException(status_code=500, detail=str(e))
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import Settings
from app.services.hair_color_detector import detect_hair_color
from app.services.best_shade_matcher import find_best_shade
from app.services.background_remove import remove_background
from pathlib import Path
import json
import os

router = APIRouter()

def load_shades_rgb(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Shade data file not found at: {path}")
    with path.open("r") as f:
        return json.load(f)

@router.post("/match-hair-color")
async def match_hair_color(file: UploadFile = File(...)):
    try:
        Settings.ensure_directories()  # Ensure all necessary directories exist

        # Step 0: create temp paths
        upload_path = f"temp_uploadg_{file.filename}"
        bg_removed_path = "remove_bg.png"
        # Step 1: save uploaded file temporarily
        with open(upload_path, "wb") as f:
            f.write(await file.read())

        # Step 2: remove background
        
        remove_bg_path=remove_background(upload_path, bg_removed_path)

        # Step 3: detect hair color from background-removed image
        user_rgb = detect_hair_color(input_path=remove_bg_path)
        print("user_rgb-------------", user_rgb)

        # Step 4: load shades & find best match
        shade_data = load_shades_rgb(Settings.SHADE_PATH)
        best, all_scores = find_best_shade(user_rgb, shade_data)
        print("best-------------", best)
        print("all_scores-------------", all_scores)

        # Step 5: cleanup temp files
        os.remove(upload_path)
        # os.remove(bg_removed_path)

        return {
            "matched_shade": best,
            "match_percentage": all_scores[best],
            "all_scores": all_scores
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
