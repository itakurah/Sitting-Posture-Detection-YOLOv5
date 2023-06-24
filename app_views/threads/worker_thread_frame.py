import time

import cv2
from PyQt5 import QtCore

from app_controllers.utils.frame_helper import *

'''Thread class for handling the received frames
'''


class WorkerThreadFrame(QtCore.QThread):
    update_camera = QtCore.pyqtSignal(object, object, object, object, object)

    def __init__(self, model, view):
        # Use super() to call __init__() methods in the parent classes
        super(WorkerThreadFrame, self).__init__()
        self.model = model
        self.view = view
        self.inference_model = model.inference_model
        self.slider_brightness = view.slider_brightness
        self.button_rotate = view.button_rotate
        self.slider_contrast = view.slider_contrast
        # Place the camera object in the WorkThread
        self.frame = None
        # read current selected camera id
        self.id = model.camera_mapping.get(view.combobox_camera_list.currentText())
        self.camera = cv2.VideoCapture(self.id)
        # set video format to mjpg to compress the frames to increase fps
        self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        # set frame resolution
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        # The boolean variable to break the while loop in self.run() method
        self.running = True

    def run(self):
        frame_count = 0
        start_time = time.time()
        fps = 0
        while self.running:
            # read one frame
            b, self.frame = self.camera.read()
            if b:
                frame_count += 1
                elapsed_time = time.time() - start_time
                if elapsed_time >= 1:
                    fps = frame_count / elapsed_time
                    frame_count = 0
                    start_time = time.time()
            # change brightness based on slider value
            self.frame = change_brightness(self.frame, self.slider_brightness.value() / 100)
            # change contrast based on slider value
            self.frame = change_contrast(self.frame, self.slider_contrast.value() / 100)
            self.check_orientation()
            self.check_rotation()
            # predict using inference_models
            results = self.inference_model.predict(self.frame)
            self.update_camera.emit(self.model, self.view, self.frame, fps, results)

    def stop(self):
        # terminate the while loop in self.run() method
        self.running = False
        self.camera.release()
        cv2.destroyAllWindows()

    def check_rotation(self):
        if self.model.frame_rotation == 90:
            self.frame = np.rot90(self.frame, -1, (0, 1))
        elif self.model.frame_rotation == 180:
            self.frame = np.rot90(self.frame, -2, (0, 1))
        elif self.model.frame_rotation == 270:
            self.frame = np.rot90(self.frame, -3, (0, 1))

    def check_orientation(self):
        if self.model.frame_orientation_vertical == 1:
            self.frame = np.flipud(self.frame)
        if self.model.frame_orientation_horizontal == 1:
            self.frame = np.fliplr(self.frame)
