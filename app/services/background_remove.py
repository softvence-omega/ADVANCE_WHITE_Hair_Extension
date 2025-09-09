from rembg import remove
from PIL import Image

def remove_background(input_path: str, output_path: str):
    """
    Remove background from an image and save as PNG with transparent background.

    Args:
        input_path (str): Input image file path.
        output_path (str): Output image file path (PNG recommended).
    """
    try:
        # ইমেজ ওপেন
        input_image = Image.open(input_path)

        # ব্যাকগ্রাউন্ড রিমুভ
        output_image = remove(input_image)

        # আউটপুট PNG সেভ
        output_image.save(output_path)

        print(f"Background removed successfully! Saved at: {output_path}")

    except Exception as e:
        print("Error:", e)


# Example usage
remove_background("1i.jpg", "output_image.png")
