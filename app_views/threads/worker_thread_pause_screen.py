import cv2
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QImage

'''Thread class for displaying the pause screen
'''


class WorkerThreadPauseScreen(QtCore.QThread):
    update_pause_screen = QtCore.pyqtSignal(object, QPixmap)

    def __init__(self, view, width, height):
        # Use super() to call __init__() methods in the parent classes
        super(WorkerThreadPauseScreen, self).__init__()
        self.view = view
        self.pixmap = QPixmap(width, height)
        self.width = int(width)
        self.height = int(height)

        # The boolean variable to break the while loop in self.run() method
        self.running = True

    def run(self):
        while self.running:
            # generate random RGB colors for all pixels in one step
            colors = np.random.rand(self.height, self.width, 3) * 255
            colors = colors.astype(np.uint8)

            # group neighboring pixels to create larger pixels
            scale_factor = 2  # Adjust the scale factor to control the size of the grouped pixels
            resized_colors = cv2.resize(colors, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_NEAREST)

            # create a QImage from the NumPy array
            image = QImage(resized_colors.data, resized_colors.shape[1], resized_colors.shape[0], QImage.Format_RGB888)

            self.pixmap = QPixmap.fromImage(image)
            self.update_pause_screen.emit(self.view, self.pixmap)
            self.msleep(90)

    def stop(self):
        # terminate the while loop in self.run() method
        self.running = False
