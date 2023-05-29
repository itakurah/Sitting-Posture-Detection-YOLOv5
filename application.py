import os
import sys
import tempfile

import cv2
import psutil
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QColor, QPainter
from PyQt5.QtWidgets import *


from util.gui import gui, frame_properties

from util.threads.worker_thread_pause_screen import WorkerThreadPauseScreen
from views.view import View


class Application(QMainWindow):
    os.environ['CURL_CA_BUNDLE'] = ''

    def __init__(self):
        super().__init__()
        #self.view = View()
        # annotate class variables


        # load frame properties
        #frame_properties.load(self)
        # load gui
        #gui.load(self)






    # on click start button


    # on click stop button











    # update pixmap with when no camera is available




    # stop pause screen worker thread


    # initialize worker thread for camera capture


    def closeEvent(self, event):
        cv2.destroyAllWindows()
        self.stop_worker_thread_camera()
        self.worker_thread_memory.stop()


def get_model_name():
    return model_name







