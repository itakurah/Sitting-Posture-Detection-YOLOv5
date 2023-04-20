import cv2
from PyQt5.QtMultimedia import QCameraInfo


# get connected camera id's from opencv
def get_connected_camera_ids():
    available_ports = []
    for x in range(5):
        camera = cv2.VideoCapture(x)
        if camera.isOpened():
            available_ports.append(x)
            ret, frame = camera.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
    # print(available_ports)
    return available_ports


# get connected cameras aliases from pyqt5
def get_connected_camera_alias():
    camera_list = [cam.description() for cam in QCameraInfo.availableCameras()]
    return camera_list


# check if at least one camera is connected
def is_camera_connected():
    camera_list = [cam.description() for cam in QCameraInfo.availableCameras()]
    return False if len(camera_list) == 0 | len(get_connected_camera_alias()) \
                    != len(get_connected_camera_ids()) else True


# map the aliases from pyqt5 with the id's from opencv
def get_camera_mapping(keys, values):
    return dict(zip(keys, values))
