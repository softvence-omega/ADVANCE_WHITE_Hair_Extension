
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import Settings
from app.services.hair_color_detector import detect_hair_color
from app.services.perfect_shade_matcher import find_perfect_match
from app.services.shade_code_mapper import get_color_code, get_tone_type, get_description
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
        Settings.ensure_directories()
        upload_path = f"temp_uploadg_{file.filename}"
        with open(upload_path, "wb") as f:
            f.write(await file.read())

        # Detect hair colors
        user_rgb = detect_hair_color(input_path=upload_path, original_path=upload_path)
        print("\n=== DETECTED COLORS ===")
        for i, c in enumerate(user_rgb):
            rgb = c.get("color", [0,0,0])
            print(f"Color {i+1}: RGB{rgb} ({c['percentage']:.1f}%)")
        
        # Match to shade database
        shade_data = load_shades_rgb(Settings.FINAL_SHADE_PATH)
        best, all_scores, base_shade = find_perfect_match(user_rgb, shade_data)
        
        if not base_shade:
            base_shade = best.split("_")[0] if best and "_" in best else best
        
        print(f"\n✓ Best Match: {base_shade}")
        print(f"✓ Score: {all_scores[best]:.1f}%")
        print(f"✓ Code: {get_color_code(base_shade)}\n")
        
        os.remove(upload_path)
        
        return {
            "matched_shade": base_shade,
            "color_code": get_color_code(base_shade),
            "tone_type": get_tone_type(base_shade),
            "description": get_description(base_shade),
            "match_percentage": all_scores[best] if best else 0
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
