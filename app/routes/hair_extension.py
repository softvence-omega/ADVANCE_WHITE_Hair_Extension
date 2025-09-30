
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import Settings
from app.services.hair_color_detector import detect_hair_color
from app.services.best_shade_matcher import find_best_shade,find_best_shade_single,find_best_shade4
from app.services.background_remove import remove_background
from pathlib import Path
import json
import os
import time

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
        start_time = time.time()
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
        
        shade_data = load_shades_rgb(Settings.N_SHADE_PATH)
        print("shade_data-------------")
        best, all_scores = find_best_shade_single(user_rgb, shade_data)
        
        # shade_data = load_shades_rgb(Settings.SHADE_PATH)
        # best, all_scores = find_best_shade(user_rgb, shade_data)

        # shade_data = load_shades_rgb(Settings.N4_SHADE_PATH)
        # best, all_scores = find_best_shade4(user_rgb, shade_data)
        
        print("best-------------", best)
        print("all_scores-------------", all_scores)
        end_time = time.time()
        execution_time = end_time - start_time
        print("execute--------------------",execution_time)
        import psutil
        process = psutil.Process(os.getpid())
        ram_usage = process.memory_info().rss / 1024 ** 2  # MB
        total_ram = psutil.virtual_memory().total / (1024 ** 3)
        print(f"Total system RAM: {total_ram:.2f} GB")
        print("Uses--ram",round(ram_usage, 2))


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
