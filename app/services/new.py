import cv2
import numpy as np

# Load the mask (assuming 255=hair, 0=background)
mask = cv2.imread("highlighted_hair.png", 0)

# Expand the mask using dilation to include bottom hair
kernel = np.ones((10,10), np.uint8)  # tweak kernel size for more/less expansion
expanded_mask = cv2.dilate(mask, kernel, iterations=1)

# Save refined mask
cv2.imwrite("highlighted_hair.png", expanded_mask)
