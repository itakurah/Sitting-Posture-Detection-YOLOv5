import os
import sys
import tempfile

import cv2
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from qt_material import apply_stylesheet

from worker_thread_camera import WorkerThreadCamera


class Application(QMainWindow):

    def __init__(self):
        super().__init__()
        width = 640
        height = 540
        self.prev_frame_time = 0
        self.IMAGE_BOX_SIZE = 600
        cbox_camera_list_width = 200
        cbox_camera_list_x = 20
        cbox_camera_list_y = 20
        self.camera_mapping = {}
        self.camera = None
        self.work_thread_camera = None

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
        self.cbox_camera_list.currentTextChanged.connect(self.on_cbox_camera_changed)

        # image settings
        self.image_camera = QLabel(self)
        self.image_camera.setStyleSheet("border: 0px solid black")
        self.image_camera.setFixedWidth(600)
        self.image_camera.setFixedHeight(450)
        self.image_camera.move(cbox_camera_list_x, cbox_camera_list_y + 30)
        # self.image_camera.adjustSize()
        self.update_pixmap()

        # btn_start settings
        btn_start_width = 80
        btn_start_height = 27
        btn_start_x = cbox_camera_list_x + cbox_camera_list_width + 5
        btn_start_y = 50
        self.btn_start = QPushButton('start', self)
        self.btn_start.setFixedHeight(btn_start_height)
        self.btn_start.setFixedWidth(btn_start_width)
        self.btn_start.move(btn_start_x, cbox_camera_list_y - 1)
        self.btn_start.clicked.connect(self.on_btn_start_clicked)

        # btn_stop
        btn_stop_x = btn_start_width + btn_start_x + 5
        btn_stop_y = 50
        self.btn_stop = QPushButton('stop', self)
        self.btn_stop.setFixedHeight(27)
        self.btn_stop.setFixedWidth(80)
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

        # load cbox items
        self.update_cbox_items()

        # disable stop button on start
        self.btn_stop.setEnabled(False)

        # load model
        # self.model = Model()
        # self.res = self.model.predict('test.jpg')
        # print(self.res)
        # print(self.res.pandas().xyxy[0])
        # print("f")
        # print(self.model.predict('1.jpg'))

        # create timer
        self.timer_start = QTimer()
        self.timer_start.timeout.connect(self.timer_timeout_start)
        self.timer_stop = QTimer()
        self.timer_stop.timeout.connect(self.timer_timeout_stop)

    # centers the main window
    def center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # on click start button
    def on_btn_start_clicked(self):
        # disable elements
        self.btn_start.setEnabled(False)
        self.cbox_camera_list.setEnabled(False)

        # start timer
        self.timer_start.start(2000)

        # set current text from cbox
        current_item = self.cbox_camera_list.currentText()

        # start worker thread
        self.start_worker_thread_camera(current_item)

        self.status_bar.showMessage('Stream started..')

        # set frame for Pixmap
        self.image_camera.setStyleSheet("border: 1px solid black")

    # on click stop button
    def on_btn_stop_clicked(self):
        self.btn_stop.setEnabled(False)
        QtCore.QCoreApplication.processEvents()
        self.timer_stop.start(2000)

        # stop camera thread
        self.stop_worker_thread_camera()

        self.status_bar.showMessage('Stream stopped..')
        QtCore.QCoreApplication.processEvents()
        self.status_bar.showMessage('Idle')

    def timer_timeout_stop(self):
        # stop timer and toggle button state
        self.timer_stop.stop()
        if not self.btn_stop.isEnabled():
            self.btn_start.setEnabled(True)
            self.cbox_camera_list.setEnabled(True)

    def timer_timeout_start(self):
        # stop timer and toggle button state
        self.timer_start.stop()
        if not self.btn_start.isEnabled():
            self.btn_stop.setEnabled(True)

    # update combobox items with current available cameras
    def on_cbox_camera_changed(self):
        QtCore.QCoreApplication.processEvents()
        self.cbox_camera_list.setEnabled(False)
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(False)
        # workaround to process the stack otherwise it will ignore the statements above
        QtCore.QCoreApplication.processEvents()
        if self.is_camera_connected():
            self.update_cbox_items()
        # do your code
        QtCore.QCoreApplication.processEvents()
        self.cbox_camera_list.setEnabled(True)
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        QtCore.QCoreApplication.processEvents()

    # update combobox items 
    def update_cbox_items(self):
        self.status_bar.showMessage('Updating camera list..')
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
        self.status_bar.showMessage('Idle')

    def draw_camera(self, img, fps, results):
        self.status_bar.showMessage('Getting camera stream..')
        QtCore.QCoreApplication.processEvents()
        rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if rgb_frame.shape[0] > rgb_frame.shape[1]:
            self.rgb_frame_resized = self.image_resize(rgb_frame, None, self.IMAGE_BOX_SIZE)
        else:
            self.rgb_frame_resized = self.image_resize(rgb_frame, self.IMAGE_BOX_SIZE)
        # get height and width
        self.h, self.w = self.rgb_frame_resized.shape[:2]
        # self.work_thread_prediction = WorkerThreadPrediction(self.model,self.rgb_frame_resized)
        # self.work_thread_prediction.prediction_done.connect(self.handle_prediction_results)
        # self.work_thread_prediction.start()
        # predict frame
        # results = self.model.predict(self.rgb_frame_resized)
        # print(results)
        labels, cord_thres = results.xyxyn[0][:, -1].cpu().numpy(), results.xyxyn[0][:,
                                                                    :-1].cpu().numpy()  # *************************
        # update statusbar
        self.update_statusbar(self.h, self.w, fps, labels)

        height, width, channel = self.rgb_frame_resized.shape
        bytes_per_line = 3 * width
        # print(type(self.rgb_frame_resized))
        q_image = QImage(self.rgb_frame_resized.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.resize(q_image.width(), q_image.height())
        self.image_camera.adjustSize()
        self.image_camera.setPixmap(pixmap)
        self.image_camera.update()

    def handle_prediction_results(self, results):
        # handle the prediction results here
        labels, cord_thres = results.xyxyn[0][:, -1].numpy(), results.xyxyn[0][:, :-1].numpy()
        # update statusbar and display the image
        self.update_statusbar(self.h, self.w, self.fps, labels)

        height, width, channel = self.rgb_frame_resized.shape
        bytes_per_line = 3 * width
        q_image = QImage(self.rgb_frame_resized.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.image_camera.adjustSize()
        self.image_camera.setPixmap(pixmap)
        self.image_camera.update()

    # update the statusbar while streaming
    def update_statusbar(self, h, w, fps, labels):
        self.camera_size.setText("image size: " + str(w) + "x" + str(h))
        self.camera_fps.setText("fps: {:.2f}".format(fps))
        # print(labels)
        if labels.size > 0:
            if int(labels[0]) == 0:
                self.class_info.setText("detected class: sitting_good")
            else:
                self.class_info.setText("detected class: sitting_bad")
        else:
            self.class_info.setText("detected class: no class")

    def update_pixmap(self):
        pixmap = QtGui.QPixmap(600, 450)
        pixmap.fill(QtGui.QColor("black"))
        painter = QtGui.QPainter(pixmap)
        font = QtGui.QFont('Arial', 20)
        painter.setFont(font)
        painter.setPen(QtGui.QColor(255, 255, 255))
        painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, "Camera not available")
        painter.end()
        self.image_camera.adjustSize()
        self.image_camera.setPixmap(pixmap)
        self.image_camera.update()

    def start_worker_thread_camera(self, current_item):
        self.work_thread_camera = WorkerThreadCamera(self.camera_mapping.get(current_item))
        self.work_thread_camera.update_camera.connect(self.draw_camera)
        self.work_thread_camera.start()

    def stop_worker_thread_camera(self):
        if self.work_thread_camera is not None:
            self.work_thread_camera.stop()
            self.work_thread_camera.wait()
            self.work_thread_camera = None
        if self.camera is not None:
            self.camera.release()
            self.camera = None

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
        # print(available_ports)
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
        # print(mapping)
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

    def closeEvent(self, event):
        cv2.destroyAllWindows()
        self.stop_worker_thread_camera()


style = '''<!--?xml version="1.0" encoding="UTF-8"?-->
<resources>
  <color name="primaryColor">#ffffff</color>
  <color name="primaryLightColor">#6e6d6d</color>
  <color name="secondaryColor">#8f8f8f</color>
  <color name="secondaryLightColor">#4f5b62</color>
  <color name="secondaryDarkColor">#31363b</color>
  <color name="primaryTextColor">#000000</color>
  <color name="secondaryTextColor">#ffffff</color>
</resources>'''

app = QApplication([])
window = Application()
with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
    # Write the XML string to the temporary file
    tmp.write(style.encode('utf-8'))
    # Close the temporary file
    tmp.close()
    apply_stylesheet(app, theme=tmp.name)
os.unlink(tmp.name)
window.show()
sys.exit(app.exec())
