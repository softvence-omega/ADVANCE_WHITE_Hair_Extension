import cv2
import mediapipe as mp
import numpy as np

def get_hair_mask(image):
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as segment:
        results = segment.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        condition = results.segmentation_mask > 0.6
        mask = np.where(condition, 255, 0).astype(np.uint8)
        return mask
