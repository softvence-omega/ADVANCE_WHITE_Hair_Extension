from fastapi import APIRouter, UploadFile, File
from app.services.hair_color_detector import evaluate
import shutil
import os
import json

router = APIRouter()

@router.post("/hair-color/")
async def detect_hair_color(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    evaluate(input_path=temp_path)
    os.remove(temp_path)
    with open("hair_rgb.json", "r") as f:
        result = json.load(f)
    return result