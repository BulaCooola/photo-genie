# https://pyimagesearch.com/2015/09/07/blur-detection-with-opencv/

# GUI slider for threshold?
# possible issues with pictures with shallow depth of field?

import cv2
# threshold=100

image_path = 'blur 2.jpg'
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()

print(laplacian_var)