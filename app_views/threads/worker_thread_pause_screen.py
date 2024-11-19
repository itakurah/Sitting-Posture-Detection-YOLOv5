import cv2
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QImage

'''Thread class for displaying the pause screen
'''


class WorkerThreadPauseScreen(QtCore.QThread):
    update_pause_screen = QtCore.pyqtSignal(object, QPixmap)

    def __init__(self, view, width, height):
        super(WorkerThreadPauseScreen, self).__init__()
        self.view = view
        self.pixmap = QPixmap(width, height)
        self.width = int(width)
        self.height = int(height)

        # The boolean variable to break the while loop in self.run() method
        self.running = True

    def run(self):
        scale_factor = 2
        small_width = self.width // scale_factor
        small_height = self.height // scale_factor

        while self.running:
            # Generate random RGB colors for scaled-down dimensions
            colors = np.random.randint(0, 256, (small_height, small_width, 3), dtype=np.uint8)

            # Upscale by repeating the values
            scaled_colors = np.repeat(np.repeat(colors, scale_factor, axis=0), scale_factor, axis=1)

            # Ensure dimensions match exactly
            scaled_colors = scaled_colors[:self.height, :self.width]

            # Create a QImage directly from the scaled NumPy array
            image = QImage(scaled_colors.data, scaled_colors.shape[1], scaled_colors.shape[0], QImage.Format_RGB888)

            self.pixmap = QPixmap.fromImage(image)
            self.update_pause_screen.emit(self.view, self.pixmap)
            self.msleep(100)

    def stop(self):
        self.running = False
