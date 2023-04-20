import time

import cv2
from PyQt5 import QtCore

from load_model import Model
from frame_helper import *


class WorkerThreadCamera(QtCore.QThread):
    update_camera = QtCore.pyqtSignal(object, object, object)
    model = Model()

    def __init__(self, id, slider_brightness, slider_contrast):
        # Use super() to call __init__() methods in the parent classes
        super(WorkerThreadCamera, self).__init__()
        self.slider_brightness = slider_brightness
        self.slider_contrast = slider_contrast
        # Place the camera object in the WorkThread
        self.frame = None
        self.camera = cv2.VideoCapture(id)
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
            # predict using model
            results = self.model.predict(self.frame)
            self.update_camera.emit(self.frame, fps, results)

    def stop(self):
        # terminate the while loop in self.run() method
        self.running = False
        self.camera.release()
        cv2.destroyAllWindows()
