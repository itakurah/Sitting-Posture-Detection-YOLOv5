import os
import random
import sys
import tempfile

import cv2
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage, QColor, QPainter
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from qt_material import apply_stylesheet

from worker_thread_camera import WorkerThreadCamera


class Application(QMainWindow):

    def __init__(self):
        super().__init__()
        width = 870
        height = 540
        self.prev_frame_time = 0
        self.IMAGE_BOX_SIZE = 600
        cbox_camera_list_width = 200
        cbox_camera_list_x = 20
        cbox_camera_list_y = 20
        self.flag_is_camera_thread_running = True
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
        self.cbox_camera_list.currentTextChanged.connect(self.on_cbox_camera_list_changed)

        # image label settings
        self.qlabel_stream = QLabel(self)
        self.qlabel_stream.setStyleSheet("border: 0px solid black")
        self.qlabel_stream_width = 600
        self.qlabel_stream_height = 450
        self.qlabel_stream.setFixedWidth(self.qlabel_stream_width)
        self.qlabel_stream.setFixedHeight(self.qlabel_stream_height)
        self.qlabel_stream.move(cbox_camera_list_x, cbox_camera_list_y + 30)
        self.qlabel_stream.setHidden(True)

        # image label settings
        self.qlabel_no_camera = QLabel(self)
        self.qlabel_no_camera.setStyleSheet("border: 0px solid black")
        self.qlabel_no_camera.setFixedWidth(600)
        self.qlabel_no_camera.setFixedHeight(450)
        self.qlabel_no_camera.move(cbox_camera_list_x, cbox_camera_list_y + 30)
        self.update_pixmap_no_camera()

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

        # groupbox settings
        self.groupbox_text_position = QGroupBox(self)
        self.groupbox_text_position.setTitle('class position')
        self.groupbox_text_position.setFixedHeight(100)
        self.groupbox_text_position.setFixedWidth(220)
        self.groupbox_text_position.setStyleSheet("QGroupBox::title {"
                                                  "padding-top:  8px;"
                                                  "padding-left: 8px;} ")
        self.groupbox_text_position.move(630, 50)

        # radio buttons
        self.button_group = QButtonGroup(self)
        self.rb_1 = QRadioButton('bottom left', self.groupbox_text_position)
        self.rb_1.move(10, 60)
        self.rb_2 = QRadioButton('bottom right', self.groupbox_text_position)
        self.rb_2.move(110, 60)
        self.rb_3 = QRadioButton('top left', self.groupbox_text_position)
        self.rb_3.move(10, 30)
        self.rb_4 = QRadioButton('top right', self.groupbox_text_position)
        self.rb_4.move(110, 30)
        self.rb_1.setChecked(True)
        self.button_group.addButton(self.rb_1, 1)
        self.button_group.addButton(self.rb_2, 2)
        self.button_group.addButton(self.rb_3, 3)
        self.button_group.addButton(self.rb_4, 4)

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
        self.status_bar.showMessage('idle')

        # load cbox items
        self.update_cbox_items()

        # disable stop button on start
        self.btn_stop.setEnabled(False)

        # create timer for buttons
        self.timer_start = QTimer()
        self.timer_start.timeout.connect(self.timer_timeout_start)
        self.timer_stop = QTimer()
        self.timer_stop.timeout.connect(self.timer_timeout_stop)

        # settings bounding box drawing
        self.box_color = (0, 255, 0)
        self.box_thickness = 2

        # settings text drawing
        self.text_color = (0, 255, 0)
        self.text_thickness = 2
        self.pos_x = 0
        self.pos_y = 0

    # centers the main window
    def center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # on click start button
    def on_btn_start_clicked(self):
        self.flag_is_camera_thread_running = True
        # disable gui elements
        self.qlabel_no_camera.setHidden(True)
        self.qlabel_stream.setHidden(False)
        self.btn_start.setEnabled(False)
        self.cbox_camera_list.setEnabled(False)

        # start timer
        self.timer_start.start(2000)

        # set current text from cbox
        current_item = self.cbox_camera_list.currentText()

        # start worker thread
        self.start_worker_thread_camera(current_item)

        # set frame for Pixmap
        self.qlabel_stream.setStyleSheet("border: 1px solid black")

    # on click stop button
    def on_btn_stop_clicked(self):
        self.status_bar.showMessage('stream stopped..')
        # enable gui elements
        self.qlabel_no_camera.setHidden(False)
        self.qlabel_stream.setHidden(True)
        self.btn_stop.setEnabled(False)
        QtCore.QCoreApplication.processEvents()
        self.timer_stop.start(2000)

        # stop camera thread
        self.stop_worker_thread_camera()
        self.status_bar.showMessage('idle')

    # on timeout stop button
    def timer_timeout_stop(self):
        # stop timer and toggle button state
        self.timer_stop.stop()
        if not self.btn_stop.isEnabled():
            self.btn_start.setEnabled(True)
            self.cbox_camera_list.setEnabled(True)

    # on timeout start button
    def timer_timeout_start(self):
        # stop timer and toggle button state
        self.timer_start.stop()
        if not self.btn_start.isEnabled():
            self.btn_stop.setEnabled(True)

    # update combobox items with current available cameras
    def on_cbox_camera_list_changed(self):
        QtCore.QCoreApplication.processEvents()
        self.cbox_camera_list.setEnabled(False)
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(False)
        # workaround to process the stack otherwise it will ignore the statements above
        QtCore.QCoreApplication.processEvents()
        if self.is_camera_connected():
            self.update_cbox_items()
            self.btn_start.setEnabled(True)
        else:
            self.btn_start.setEnabled(False)
        # do your code
        self.cbox_camera_list.setEnabled(True)
        self.btn_stop.setEnabled(False)
        QtCore.QCoreApplication.processEvents()

    # update combobox items 
    def update_cbox_items(self):
        self.status_bar.showMessage('updating camera list..')
        QtCore.QCoreApplication.processEvents()
        self.cbox_camera_list.currentTextChanged.disconnect(self.on_cbox_camera_list_changed)
        text = self.cbox_camera_list.currentText()
        self.camera_mapping = self.update_camera_mapping(self.get_connected_camera_alias(),
                                                         self.get_connected_camera_ids())
        self.cbox_camera_list.clear()
        self.cbox_camera_list.addItems(self.camera_mapping.keys())
        index = self.cbox_camera_list.findText(text, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.cbox_camera_list.setCurrentIndex(index)
        self.cbox_camera_list.currentTextChanged.connect(self.on_cbox_camera_list_changed)
        self.status_bar.showMessage('idle')

    @staticmethod
    def generate_random_tuple():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    # draw bounding box around class
    def draw_bounding_box(self, frame, x1, y1, x2, y2):
        cv2.rectangle(frame, (x1, y1), (x2, y2), self.box_color, self.box_thickness)

    def draw_class(self, frame, x1, y1, x2, y2, class_name):
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        color = (255, 0, 0)
        thickness = 1
        text_size, _ = cv2.getTextSize("sitting_good", font, font_scale, thickness)
        (x, y) = frame.shape[:2]
        if self.button_group.checkedId() == 1:
            # set text to bottom left
            org = (10, x - 10)
        elif self.button_group.checkedId() == 2:
            # set text to bottom right
            org = y - text_size[0] - 10, x - 10
        elif self.button_group.checkedId() == 3:
            # set text to top left
            org = 10, text_size[1] + 10
        elif self.button_group.checkedId() == 4:
            # set text to top right
            org = (y - text_size[0] - 10, text_size[1] + 10)
        # draw text to frame
        cv2.putText(frame, 'sitting_good' if class_name == 0 else 'sitting_bad', org, font, font_scale,
                    color, thickness, cv2.LINE_AA)

    def draw_frame(self, img, fps, results):
        if self.flag_is_camera_thread_running:
            self.status_bar.showMessage('getting camera stream..')
        QtCore.QCoreApplication.processEvents()
        # convert to rgb format
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # resize to fit into QImage element
        if frame.shape[0] > frame.shape[1]:
            frame = self.image_resize(frame, None, self.IMAGE_BOX_SIZE)
        else:
            frame = self.image_resize(frame, self.IMAGE_BOX_SIZE)
        # get height and width of frame
        h, w = frame.shape[:2]

        # labels, cord_thres = results.xyxyn[0][:, -1].cpu().numpy(), results.xyxyn[0][:,
        #:-1].cpu().numpy()  # *************************
        results = results.pandas().xyxy[0].to_dict(orient="records")
        # print(results)
        if results:
            for result in results:
                confidence = result['confidence']
                class_name = result['class']
                x1 = int(result['xmin'])
                y1 = int(result['ymin'])
                x2 = int(result['xmax'])
                y2 = int(result['ymax'])
                self.draw_bounding_box(frame, x1, y1, x2, y2)
                self.draw_class(frame, x1, y1, x2, y2, class_name)
        if self.flag_is_camera_thread_running:
            # update statusbar
            if not results:
                self.update_statusbar(h, w, fps)
            else:
                self.update_statusbar(h, w, fps, class_name)

        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        # add border
        pixmap = self.draw_black_border(pixmap)

        self.qlabel_stream.setPixmap(QPixmap.fromImage(pixmap))
        self.qlabel_stream.adjustSize()
        self.qlabel_stream.update()

    # draw black border around frame
    def draw_black_border(self, pixmap):
        border_width = self.qlabel_stream.width()
        border_height = self.qlabel_stream.height()
        pixmap_scaled = pixmap.scaled(border_width, border_height, aspectRatioMode=Qt.KeepAspectRatio)
        # create a black QImage with the same size as the label
        border_pixmap = QImage(border_width, border_height, QImage.Format_RGB888)
        border_pixmap.fill(QColor(0, 0, 0))
        # calculate the position to place the pixmap
        x = (border_width - pixmap.width()) // 2
        y = (border_height - pixmap.height()) // 2
        # paint the pixmap onto the image with black borders
        painter = QPainter(border_pixmap)
        painter.drawPixmap(x, y, pixmap_scaled)
        painter.end()
        return border_pixmap

    # update the statusbar while streaming
    def update_statusbar(self, h=None, w=None, fps=None, class_frame=None):
        # update image size label
        if (h is None) & (w is None):
            self.camera_size.setText("image size: -")
        else:
            self.camera_size.setText("image size: " + str(w) + "x" + str(h))
        # update fps label
        if fps is None:
            self.camera_fps.setText("fps: -")
        else:
            self.camera_fps.setText("fps: {:.2f}".format(fps))
        # update detected class
        if class_frame is None:
            self.class_info.setText("detected class: no class")
        elif class_frame == 0:
            self.class_info.setText("detected class: sitting_good")
        else:
            self.class_info.setText("detected class: sitting_bad")

    # update pixmap with when no camera is available
    def update_pixmap_no_camera(self):
        # draw camera not available info frame
        pixmap = QPixmap(600, 450)
        pixmap.fill(QtGui.QColor("black"))
        painter = QtGui.QPainter(pixmap)
        font = QtGui.QFont('Arial', 20)
        painter.setFont(font)
        painter.setPen(QtGui.QColor(255, 255, 255))
        painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, "Camera not available")
        painter.end()
        self.qlabel_no_camera.adjustSize()
        self.qlabel_no_camera.setPixmap(pixmap)
        self.qlabel_no_camera.update()

    # initialize worker thread for camera capture
    def start_worker_thread_camera(self, current_item):
        self.work_thread_camera = WorkerThreadCamera(self.camera_mapping.get(current_item))
        self.work_thread_camera.finished.connect(lambda: self.update_statusbar())
        self.work_thread_camera.update_camera.connect(self.draw_frame)
        self.work_thread_camera.start()

    # stop camera worker thread
    def stop_worker_thread_camera(self):
        self.flag_is_camera_thread_running
        if self.work_thread_camera is not None:
            self.work_thread_camera.stop()
            self.work_thread_camera.wait()
            self.update_pixmap_no_camera()
            self.work_thread_camera = None
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        cv2.destroyAllWindows()
        self.flag_is_camera_thread_running = False
        self.update_statusbar()

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

    # get connected cameras aliases from pyqt5
    @staticmethod
    def get_connected_camera_alias():
        camera_list = [cam.description() for cam in QCameraInfo.availableCameras()]
        return camera_list

    # check if at least one camera is connected
    @staticmethod
    def is_camera_connected():
        camera_list = [cam.description() for cam in QCameraInfo.availableCameras()]
        return False if len(camera_list) == 0 | len(Application.get_connected_camera_alias()) \
                        != len(Application.get_connected_camera_ids()) else True

    # map the aliases from pyqt5 with the id's from opencv
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
