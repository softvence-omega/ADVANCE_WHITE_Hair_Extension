from rembg import remove
from PIL import Image

def remove_background(input_source, output_path: str):
    """Remove background from an image and save the result to output_path."""
    input_image = Image.open(input_source).convert("RGBA")
    output_image = remove(input_image)
    output_path="remove_bg.png"
    output_image.save(output_path)
    return output_path