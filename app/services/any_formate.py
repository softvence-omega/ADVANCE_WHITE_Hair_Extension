from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener

# Enable HEIC/HEIF support for Pillow
register_heif_opener()

def load_image_any_format(input_path: str) -> Image.Image:
    """
    Open an image file safely, regardless of format (JPG, PNG, HEIC, etc.)
    Always returns an RGB Pillow Image.
    """
    try:
        img = Image.open(input_path).convert("RGB")
        return img
    except UnidentifiedImageError as e:
        raise ValueError(f"Unsupported or corrupted image format: {input_path}") from e
