import cv2
from PyQt5.QtMultimedia import QCameraInfo

'''Helper class for retrieving information of camera status
'''


def get_connected_camera_ids():
    """
    Retrieves the ports of connected cameras

    Returns:
        available_ports: Available ports.
    """
    available_ports = []
    for x in range(5):
        camera = cv2.VideoCapture(x)
        if camera.isOpened():
            available_ports.append(x)
            ret, frame = camera.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
    return available_ports


def get_connected_camera_alias():
    """
    Retrieves all names of connected cameras

    Returns:
        camera_list: Available camera names.
    """
    camera_list = [cam.description() for cam in QCameraInfo.availableCameras()]
    return camera_list


def is_camera_connected():
    """
    Checks if no cameras are connected

    Returns:
        bool: False if no camera is connected.
    """
    camera_list = [cam.description() for cam in QCameraInfo.availableCameras()]
    return False if len(camera_list) == 0 | len(get_connected_camera_alias()) \
                    != len(get_connected_camera_ids()) else True


def get_camera_mapping(keys, values):
    """
    Maps the current available camera ports with it corresponding names

    Args:
        keys: The names of the cameras.
        values: The port id's of the cameras.

    Returns:
        dict: The mapped cameras key/value pairs.
    """
    return dict(zip(keys, values))
