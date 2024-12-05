# https://pyimagesearch.com/2015/09/07/blur-detection-with-opencv/

# GUI slider for threshold?
# possible issues with pictures with shallow depth of field?

import cv2
import numpy as np
import matplotlib.pyplot as plt

# threshold=100


def imshow(image, *args, **kwargs):
    if len(image.shape) == 3:
        # Height, width, channels
        # Assume BGR, do a conversion since
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        # Height, width - must be grayscale
        # convert to RGB, since matplotlib will plot in a weird colormap (instead of black = 0, white = 1)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    # Draw the image
    plt.imshow(image, *args, **kwargs)
    # We'll also disable drawing the axes and tick marks in the plot, since it's actually an image
    plt.axis("off")
    # Make sure it outputs
    plt.show()


#####
# Using Sobel Gradients to determine the gradient magnitude for edge detection
def sharpness_test_gradient(image_path):
    # Load the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Image could not be loaded. Check the file path.")

    # Compute gradients in x and y directions
    sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)

    # Compute gradient magnitude
    gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)

    # Calculate mean gradient magnitude
    mean_gradient = np.mean(gradient_magnitude)
    return mean_gradient


# image_path = "blur 2.jpg"
image_path = "_DSC3940.JPG"
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()

print(laplacian_var)

imshow(image)

######
# Test the function
sharpness_score_gradient = sharpness_test_gradient(image_path)
print(f"Sharpness score (Gradient Magnitude): {sharpness_score_gradient}")
