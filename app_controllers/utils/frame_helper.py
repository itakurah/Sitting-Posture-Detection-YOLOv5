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
    try:
        # Convert the image to float32 for arithmetic operations
        image = image.astype('float32')
        # Apply the contrast formula
        output = (image - 128) * contrast_factor + 128

        # Clip the values to the range [0, 255]
        output = np.clip(output, 0, 255)

        # Convert the image back to uint8 data type
        output = output.astype('uint8')
    except Exception as err:
        print(f'Unexpected {err=}, {type(err)=}')
        raise
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
    try:
        # Scale the image by the brightness factor
        output = image * brightness_factor

        # Clip the values to the range [0, 255]
        output = np.clip(output, 0, 255)

        # Convert the image back to uint8 data type
        output = output.astype('uint8')
    except Exception as err:
        print(f'Unexpected {err=}, {type(err)=}')
        raise
    return output
