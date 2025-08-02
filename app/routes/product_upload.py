from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.LabCoolor import build_reference_shades
from fastapi.responses import JSONResponse
from app.config import Settings
import shutil
import uuid
from pathlib import Path
import json
import os

router = APIRouter()
@router.post("/upload-product")
async def upload_product(
    closeup: UploadFile = File(...),
    indoor_light: UploadFile = File(...),
    natural_light: UploadFile = File(...),
    shade_name: str = "UnknownShade"  # You can pass this via query/body
):
   # Load existing reference data before any processing
    ref_path = Path("reference_shades.json")
    if ref_path.exists():
        with open(ref_path, "r") as f:
            reference_data = json.load(f)
    else:
        reference_data = {}

    # Early check for existing shade name
    if shade_name in reference_data:
        raise HTTPException(
            status_code=400,
            detail=f"Shade '{shade_name}' already exists. Please use a different name."
        )

    # Only proceed if shade_name is new
    # temp_dir = Path(f"temp_{uuid.uuid4().hex}")
    temp_dir = Path(shade_name)
    os.makedirs(temp_dir, exist_ok=True)

    files = {
        "CloseUp": closeup,
        "IndoorLight": indoor_light,
        "NaturalLight": natural_light
    }

    try:
        # Save uploaded files
        for tag, file in files.items():
            file_path = temp_dir / f"{shade_name}_{tag}.png"
            with open(file_path, "wb") as f:
                f.write(await file.read())

        # Generate new shade from image files
        new_shade = build_reference_shades(temp_dir)
        print("new_shade-------------:", new_shade)
        # Add new shade and save updated reference file
        reference_data[shade_name] = new_shade[shade_name]
        with open(ref_path, "w") as f:
            json.dump(reference_data, f, indent=2)

        return JSONResponse(content={"message": "Shade uploaded successfully.", "data": new_shade})

    finally:
        shutil.rmtree(temp_dir)