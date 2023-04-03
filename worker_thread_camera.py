import time

import cv2
from PyQt5 import QtCore

from load_model import Model


class WorkerThreadCamera(QtCore.QThread):
    update_camera = QtCore.pyqtSignal(object, object, object)
    model = Model()

    def __init__(self, id):
        # Use super() to call __init__() methods in the parent classes
        super(WorkerThreadCamera, self).__init__()

        # Place the camera object in the WorkThread
        self.frame = None
        self.camera = cv2.VideoCapture(id)
        self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

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
            results = self.model.predict(self.frame)

            xB, xA, yB, yA = 0, 0, 0, 0
            for box in results.xyxy[0]:
                xB = int(box[2])
                xA = int(box[0])
                yB = int(box[3])
                yA = int(box[1])
            # labels, cord_thres = results.xyxyn[0][:, -1].numpy(), results.xyxyn[0][:, :-1].numpy()
            # print(labels)
            # print(cord_thres)
            cv2.rectangle(self.frame, (xA, yA), (xB, yB), (0, 255, 0), 2)

            # results = self.model.predict(self.rgb_frame_resized)
            self.update_camera.emit(self.frame, fps, results)

    def stop(self):
        # Terminate the while loop in self.run() method
        self.running = False
        self.camera.release()
        cv2.destroyAllWindows()
