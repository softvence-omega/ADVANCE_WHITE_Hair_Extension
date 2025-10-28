from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import Settings
from app.services.hair_color_detector import detect_shade_color
from app.services.exact_shade_matcher import ExactShadeMatcher
import os

router = APIRouter()

@router.post("/match-kmeans")
async def match_hair_color_kmeans(file: UploadFile = File(...)):
    try:
        Settings.ensure_directories()
        upload_path = f"temp_upload_{file.filename}"
        with open(upload_path, "wb") as f:
            f.write(await file.read())

        user_colors = detect_shade_color(upload_path)
        
        matcher = ExactShadeMatcher()
        result = matcher.match_shade(user_colors)
        
        os.remove(upload_path)
        
        return {
            "user_colors": user_colors[:3],
            "matched_file": result['matched_file'],
            "matched_shade": result['matched_shade'],
            "distance": result['distance'],
            "top_5_matches": result['top_5']
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
