import cv2
import numpy as np

'''Class for handling frame manipulation 
'''


def change_contrast(image, contrast_factor):
    """
    Changes the contrast of an image.

    Args:
        image (numpy array): The input image as a NumPy ndarray.
        contrast_factor (float): The contrast factor. A value of 1.0 means no change,
            <1.0 will decrease the contrast, and >1.0 will increase the contrast.

    Returns:
        numpy array: The image with adjusted contrast.
    """
    # Convert the image to float32 for arithmetic operations
    image = image.astype('float32')

    # Apply the contrast formula
    output = (image - 128) * contrast_factor + 128

    # Clip the values to the range [0, 255]
    output = np.clip(output, 0, 255)

    # Convert the image back to uint8 data type
    output = output.astype('uint8')

    return output


def change_brightness(image, brightness_factor):
    """
    Changes the brightness of an image using NumPy element-wise array operations.

    Args:
        image (numpy array): The input image as a NumPy ndarray.
        brightness_factor (float): The brightness factor. A value of 1.0 means no change,
            <1.0 will make the image darker, and >1.0 will make the image brighter.

    Returns:
        numpy array: The image with adjusted brightness.
    """
    # Scale the image by the brightness factor
    output = image * brightness_factor

    # Clip the values to the range [0, 255]
    output = np.clip(output, 0, 255)

    # Convert the image back to uint8 data type
    output = output.astype('uint8')

    return output


# resize image to specific width and height
def resize_frame(image, width=None, height=None, inter=cv2.INTER_AREA):
    """
    Resizes an image to specific size

    Args:
        image (numpy array): The input image as a NumPy ndarray.
        width: The width to resize the image to.
        height: The height to resize the image to.
        inter: The interpolation method to be applied, INTER_AREA (default).

    Returns:
        numpy array: The resized image.
    """

    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    h, w = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized
