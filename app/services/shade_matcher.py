import json
import numpy as np
from app.config import Settings

SHADE_PATH = Settings.SHADE_PATH

def load_shades(SHADE_PATH):
    with open(SHADE_PATH) as f:
        return json.load(f)

def delta_e(lab1, lab2):
    return np.linalg.norm(np.array(lab1) - np.array(lab2))

def match_shade(lab_input, shade_data):
    closest = None
    min_distance = float("inf")
    for name, lab_val in shade_data.items():
        dist = delta_e(lab_input, lab_val)
        if dist < min_distance:
            min_distance = dist
            closest = name
    return closest, min_distance
