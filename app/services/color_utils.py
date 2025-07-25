import cv2
import numpy as np

def average_lab_from_mask(image, mask):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    pixels = lab[mask > 0]
    if len(pixels) == 0:
        return [0, 0, 0]
    return np.mean(pixels, axis=0).tolist()
