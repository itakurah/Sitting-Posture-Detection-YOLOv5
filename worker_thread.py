from PyQt5 import QtCore
import cv2
import time

class WorkThread(QtCore.QThread):
    update_Camera = QtCore.pyqtSignal(object, object)

    def __init__(self, id):
        # Use super() to call __init__() methods in the parent classes
        super(WorkThread, self).__init__()

        # Place the camera object in the WorkThread
        self.frame = None
        self.camera = cv2.VideoCapture(id)

        # The boolean variable to break the while loop in self.run() method
        self.running = True

    def run(self):
        frame_count = 0
        start_time = time.time()
        fps = 0
        while self.running:
            # Read one frame
            b, self.frame = self.camera.read()
            # fps = 0
            if b:
                frame_count += 1
                elapsed_time = time.time() - start_time
                if elapsed_time >= 1:
                    fps = frame_count / elapsed_time
                    frame_count = 0
                    start_time = time.time()
            self.update_Camera.emit(self.frame, fps)

    def stop(self):
        # Terminate the while loop in self.run() method
        self.running = False
