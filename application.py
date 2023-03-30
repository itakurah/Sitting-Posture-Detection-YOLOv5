import sys
import time

import cv2
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from worker_thread import WorkThread


class Application(QMainWindow):

    def __init__(self):
        super().__init__()
        width = 640
        height = 540
        h, w = (0,0)
        self.prev_frame_time = 0
        self.IMAGE_BOX_SIZE = 600
        cbox_camera_list_width = 150
        cbox_camera_list_x = 20
        cbox_camera_list_y = 20
        self.camera_mapping = {}
        self.camera = None
        self.workThread = None

        # window settings
        self.setWindowTitle("YOLO Sitting Posture Detector")
        self.setGeometry(100, 100, width, height)
        self.setFixedSize(width, height)
        self.center_window()

        # combobox settings
        self.cbox_camera_list = QComboBox(self)
        self.cbox_camera_list.addItems(self.get_connected_camera_alias())
        self.cbox_camera_list.move(cbox_camera_list_x, cbox_camera_list_y)
        self.cbox_camera_list.setFixedWidth(cbox_camera_list_width)
        self.cbox_camera_list.setFixedHeight(25)

        # image settings
        self.image_camera = QLabel(self)
        self.image_camera.setStyleSheet("border: 0px solid black")
        self.image_camera.setHidden(True)
        p = QPixmap('')
        self.image_camera.setPixmap(p)
        self.image_camera.move(cbox_camera_list_x, cbox_camera_list_y + 30)
        self.image_camera.adjustSize()

        # btn_start settings
        btn_start_width = 60
        btn_start_height = 27
        btn_start_x = cbox_camera_list_x + cbox_camera_list_width
        btn_start_y = 50
        self.btn_start = QPushButton('start', self)
        self.btn_start.setFixedHeight(btn_start_height)
        self.btn_start.setFixedWidth(btn_start_width)
        self.btn_start.move(btn_start_x, cbox_camera_list_y - 1)
        self.btn_start.clicked.connect(self.on_btn_start_clicked)

        # btn_stop
        btn_stop_x = btn_start_width + btn_start_x
        btn_stop_y = 50
        self.btn_stop = QPushButton('stop', self)
        self.btn_stop.setFixedHeight(27)
        self.btn_stop.setFixedWidth(60)
        self.btn_stop.move(btn_stop_x, cbox_camera_list_y - 1)
        self.btn_stop.clicked.connect(self.on_btn_stop_clicked)

        # statusbar settings
        # add class info
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.class_info = QLabel("detected class: -")
        self.status_bar.addPermanentWidget(self.class_info)
        self.camera_size = QLabel("frame size: -")
        self.status_bar.addPermanentWidget(self.camera_size)
        self.camera_fps = QLabel("fps: -")
        self.status_bar.addPermanentWidget(self.camera_fps)
        self.status_bar.showMessage('Idle')

        # define signals for updates
        self.cbox_camera_list.currentTextChanged.connect(self.on_cbox_camera_changed)
        # self.cbox_camera_list.currentTextChanged.connect(self.btn_start.setEnabled(False))

        # load cbox items
        self.update_cbox_items()
        self.btn_stop.setEnabled(False)

    # centers the main window
    def center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # on click start button
    def on_btn_start_clicked(self):
        self.status_bar.showMessage('Stream started..')
        self.cbox_camera_list.setEnabled(False)
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.image_camera.setHidden(False)
        self.image_camera.setStyleSheet("border: 1px solid black")
        #QtCore.QCoreApplication.processEvents()
        current_item = self.cbox_camera_list.currentText()
        #print(self.camera_mapping)
        #print(self.camera_mapping.get(current_item))
        self.workThread = WorkThread(self.camera_mapping.get(current_item))
        self.workThread.update_Camera.connect(self.draw_camera)
        self.workThread.start()

    # on click stop button
    def on_btn_stop_clicked(self):
        self.status_bar.showMessage('Stream stopped..',2000)
        QtCore.QCoreApplication.processEvents()
        self.cbox_camera_list.setEnabled(True)
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.image_camera.setHidden(True)
        if self.workThread is not None:
            self.workThread.stop()
            self.workThread.wait()
            self.workThread = None
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        self.status_bar.showMessage('Stream stopped..')
        QtCore.QCoreApplication.processEvents()
        self.status_bar.showMessage('Idle')
        #QtCore.QCoreApplication.processEvents()

    # update combobox items with current available cameras
    def on_cbox_camera_changed(self):
        self.cbox_camera_list.setEnabled(False)
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(False)
        # workaround to process the stack otherwise it will ignore the statements above
        QtCore.QCoreApplication.processEvents()
        if self.is_camera_connected():
            self.update_cbox_items()
        # do your code
        self.cbox_camera_list.setEnabled(True)
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(True)

    # update combobox items 
    def update_cbox_items(self):
        self.status_bar.showMessage('Updating camera list..')
        QtCore.QCoreApplication.processEvents()
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.cbox_camera_list.setEnabled(False)
        QtCore.QCoreApplication.processEvents()
        self.cbox_camera_list.currentTextChanged.disconnect(self.on_cbox_camera_changed)
        text = self.cbox_camera_list.currentText()
        self.camera_mapping = self.update_camera_mapping(self.get_connected_camera_alias(),
                                                         self.get_connected_camera_ids())
        self.cbox_camera_list.clear()
        self.cbox_camera_list.addItems(self.camera_mapping.keys())
        index = self.cbox_camera_list.findText(text, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.cbox_camera_list.setCurrentIndex(index)
        self.cbox_camera_list.currentTextChanged.connect(self.on_cbox_camera_changed)
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.cbox_camera_list.setEnabled(True)
        self.status_bar.showMessage('Idle')

    def draw_camera(self, img, fps):
        self.status_bar.showMessage('Getting camera stream..')
        QtCore.QCoreApplication.processEvents()
        rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if rgb_frame.shape[0]>rgb_frame.shape[1]:
            rgb_frame_resized = self.image_resize(rgb_frame, None, self.IMAGE_BOX_SIZE)
        else:
            rgb_frame_resized = self.image_resize(rgb_frame, self.IMAGE_BOX_SIZE)
        # get height and width
        h, w = rgb_frame_resized.shape[:2]
        # update statusbar
        self.update_statusbar(h, w, fps)

        height, width, channel = rgb_frame_resized.shape
        bytes_per_line = 3 * width
        q_image = QImage(rgb_frame_resized.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.resize(q_image.width(), q_image.height())
        self.image_camera.adjustSize()
        self.image_camera.setPixmap(pixmap)
        self.image_camera.update()

    # update the statusbar while streaming
    def update_statusbar(self, h, w, fps):
        self.camera_size.setText("image size: " + str(h) + "x" + str(w))
        self.camera_fps.setText("fps: {:.2f}".format(fps))

    # get connected camera id's from opencv
    @staticmethod
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
        #print(available_ports)
        return available_ports

    # get all connected cameras from pyqt5
    @staticmethod
    def get_connected_camera_alias():
        camera_list = [cam.description() for cam in QCameraInfo.availableCameras()]
        return camera_list

    # checks if at least one camera is connected
    @staticmethod
    def is_camera_connected():
        camera_list = [cam.description() for cam in QCameraInfo.availableCameras()]
        return False if len(camera_list) == 0 | len(Application.get_connected_camera_alias()) \
                        != len(Application.get_connected_camera_ids()) else True

    # maps the alias names from pyqt5 with the id's from opencv
    @staticmethod
    def update_camera_mapping(keys, values):
        mapping = dict(zip(keys, values))
        #print(mapping)
        return mapping

    # resize image to specific width and height
    @staticmethod
    def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
        # initialize the dimensions of the image to be resized and
        # grab the image size
        dim = None
        h, w = image.shape[:2]

        # if both the width and height are None, then return the
        # original image
        if width is None and height is None:
            return image

        # check to see if the width is None
        if width is None:
            # calculate the ratio of the height and construct the
            # dimensions
            r = height / float(h)
            dim = (int(w * r), height)

        # otherwise, the height is None
        else:
            # calculate the ratio of the width and construct the
            # dimensions
            r = width / float(w)
            dim = (width, int(h * r))

        # resize the image
        resized = cv2.resize(image, dim, interpolation=inter)

        # return the resized image
        return resized

app = QApplication([])
window = Application()
window.show()
sys.exit(app.exec())
