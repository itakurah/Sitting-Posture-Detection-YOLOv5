import os
import random
import sys
import tempfile

import cv2
import psutil
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage, QColor, QPainter
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from qt_material import apply_stylesheet

from worker_thread_camera import WorkerThreadCamera
from worker_thread_memory import WorkerThreadMemory
from worker_thread_pause_screen import WorkerThreadPauseScreen


class Application(QMainWindow):

    def __init__(self):
        super().__init__()
        self.memory_usage = None
        self.confidence = None
        self.class_name = None
        self.width = None
        self.height = None
        self.fps = None
        self.gui_width = 870
        self.gui_height = 540
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
        self.setGeometry(100, 100, self.gui_width, self.gui_height)
        self.setFixedSize(self.gui_width, self.gui_height)
        self.center_window()

        # combobox settings
        self.cbox_camera_list = QComboBox(self)
        self.cbox_camera_list.addItems(self.get_connected_camera_alias())
        self.cbox_camera_list.move(cbox_camera_list_x, cbox_camera_list_y)
        self.cbox_camera_list.setFixedWidth(cbox_camera_list_width)
        self.cbox_camera_list.setFixedHeight(25)
        self.cbox_camera_list.currentTextChanged.connect(self.on_cbox_camera_list_changed)

        # image label settings
        self.label_stream = QLabel(self)
        self.label_stream.setStyleSheet("border: 2px solid black")
        self.qlabel_stream_width = 600
        self.qlabel_stream_height = 450
        self.label_stream.setFixedWidth(self.qlabel_stream_width)
        self.label_stream.setFixedHeight(self.qlabel_stream_height)
        self.label_stream.move(cbox_camera_list_x, cbox_camera_list_y + 30)
        self.label_stream.setHidden(True)

        # image label settings
        self.qlabel_no_camera = QLabel(self)
        self.qlabel_no_camera.setStyleSheet("border: 0px solid black")
        self.qlabel_no_camera.setFixedWidth(self.qlabel_stream_width)
        self.qlabel_no_camera.setFixedHeight(self.qlabel_stream_height)
        self.qlabel_no_camera.move(cbox_camera_list_x, cbox_camera_list_y + 30)

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
        self.groupbox_frame_options = QGroupBox(self)
        self.groupbox_frame_options.setTitle('frame options')
        self.groupbox_frame_options.setFixedHeight(240)
        self.groupbox_frame_options.setFixedWidth(230)
        self.groupbox_frame_options.setStyleSheet("QGroupBox::title {"
                                                  "padding-top:  8px;"
                                                  "padding-left: 8px;} ")
        self.groupbox_frame_options.move(630, 50)

        # radio buttons settings
        self.current_rb_selected = None
        self.button_group = QButtonGroup(self)
        self.rb_1 = QRadioButton('bottom left', self.groupbox_frame_options)
        self.rb_1.move(10, 60)
        self.rb_2 = QRadioButton('bottom right', self.groupbox_frame_options)
        self.rb_2.move(110, 60)
        self.rb_3 = QRadioButton('top left', self.groupbox_frame_options)
        self.rb_3.move(10, 30)
        self.rb_4 = QRadioButton('top right', self.groupbox_frame_options)
        self.rb_4.move(110, 30)
        self.rb_1.setChecked(True)
        self.button_group.addButton(self.rb_1, 1)
        self.button_group.addButton(self.rb_2, 2)
        self.button_group.addButton(self.rb_3, 3)
        self.button_group.addButton(self.rb_4, 4)

        # checkbox settings
        self.cbox_enable_bbox = QCheckBox('bounding box', self.groupbox_frame_options)
        self.cbox_enable_bbox.move(10, 110)
        self.cbox_enable_class = QCheckBox('class', self.groupbox_frame_options)
        self.cbox_enable_class.move(10, 170)
        self.cbox_enable_conf = QCheckBox('confidence', self.groupbox_frame_options)
        self.cbox_enable_conf.move(10, 140)
        self.cbox_enable_info_background = QCheckBox('background', self.groupbox_frame_options)
        self.cbox_enable_info_background.move(10, 200)
        self.cbox_enable_bbox.setChecked(True)
        self.cbox_enable_class.setChecked(True)
        self.cbox_enable_conf.setChecked(True)
        self.cbox_enable_info_background.setChecked(True)

        # statusbar settings
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.label_class_info = QLabel("detected class: -")
        self.status_bar.addPermanentWidget(self.label_class_info)
        self.label_conf = QLabel("conf: -")
        self.status_bar.addPermanentWidget(self.label_conf)
        self.label_dim = QLabel("frame size: -")
        self.status_bar.addPermanentWidget(self.label_dim)
        self.label_fps = QLabel("fps: -")
        self.status_bar.addPermanentWidget(self.label_fps)
        self.label_memory_usage = QLabel('memory: -')
        self.status_bar.addPermanentWidget(self.label_memory_usage)

        # show message
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
        self.box_color = (251, 255, 12)
        self.box_thickness = 2

        # settings text drawing
        self.text_color_conf = (251, 255, 12)
        self.text_color_class = (251, 255, 12)
        self.text_color_bg = (0, 0, 0)
        self.text_thickness = 1
        self.text_font = cv2.FONT_HERSHEY_SIMPLEX
        self.text_font_scale = 0.5
        self.pos_x = 0
        self.pos_y = 0

        self.btn_color_box = QPushButton('', self.groupbox_frame_options)
        self.btn_color_box.move(140, 118)
        self.btn_color_box.setFixedHeight(20)
        self.btn_color_box.setFixedWidth(20)
        self.btn_color_class = QPushButton('', self.groupbox_frame_options)
        self.btn_color_class.move(140, 178)
        self.btn_color_class.setFixedHeight(20)
        self.btn_color_class.setFixedWidth(20)
        self.btn_color_conf = QPushButton('', self.groupbox_frame_options)
        self.btn_color_conf.move(140, 148)
        self.btn_color_conf.setFixedHeight(20)
        self.btn_color_conf.setFixedWidth(20)
        self.btn_color_bg = QPushButton('', self.groupbox_frame_options)
        self.btn_color_bg.move(140, 208)
        self.btn_color_bg.setFixedHeight(20)
        self.btn_color_bg.setFixedWidth(20)
        self.btn_color_box.setStyleSheet(
            f"background-color: rgb({self.box_color[0]}, {self.box_color[1]}, {self.box_color[2]})")
        self.btn_color_class.setStyleSheet(
            f"background-color: rgb({self.text_color_class[0]}, {self.text_color_class[1]}, {self.text_color_class[2]})")
        self.btn_color_conf.setStyleSheet(
            f"background-color: rgb({self.text_color_conf[0]}, {self.text_color_conf[1]}, {self.text_color_conf[2]})")
        self.btn_color_bg.setStyleSheet(
            f"background-color: rgb({self.text_color_bg[0]}, {self.text_color_bg[1]}, {self.text_color_bg[2]})")
        self.btn_color_box.clicked.connect(lambda: self.show_color_picker(self.btn_color_box))
        self.btn_color_class.clicked.connect(lambda: self.show_color_picker(self.btn_color_class))
        self.btn_color_conf.clicked.connect(lambda: self.show_color_picker(self.btn_color_conf))
        self.btn_color_bg.clicked.connect(lambda: self.show_color_picker(self.btn_color_bg))

        self.groupbox_general_options = QGroupBox(self)
        self.groupbox_general_options.setTitle('general options')
        self.groupbox_general_options.setFixedHeight(100)
        self.groupbox_general_options.setFixedWidth(230)
        self.groupbox_general_options.setStyleSheet("QGroupBox::title {"
                                                    "padding-top:  8px;"
                                                    "padding-left: 8px;} ")
        self.groupbox_general_options.move(630, 300)
        self.cbox_enable_debug = QCheckBox('developer mode', self.groupbox_general_options)
        self.cbox_enable_debug.move(10, 30)
        self.cbox_enable_debug.setChecked(True)
        self.cbox_enable_debug.stateChanged.connect(self.set_debug_mode)

        # start memory thread
        self.worker_thread_memory = WorkerThreadMemory()
        self.worker_thread_memory.update_memory.connect(self.update_memory_usage)
        self.worker_thread_memory.start()

        # start pause screen thread
        self.worker_thread_pause_screen = WorkerThreadPauseScreen(self.qlabel_stream_width, self.qlabel_stream_height)
        self.worker_thread_pause_screen.update_pause_screen.connect(self.update_pause_frame)
        self.worker_thread_pause_screen.start()

    # update memory usage in statusbar
    def update_memory_usage(self):
        self.memory_usage = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
        self.label_memory_usage.setText('mem: {:.0f} MB'.format(self.memory_usage))

    # show or hide debug features
    def set_debug_mode(self):
        if self.cbox_enable_debug.isChecked():
            self.label_fps.setHidden(False)
            self.label_class_info.setHidden(False)
            self.label_conf.setHidden(False)
            self.label_dim.setHidden(False)
            self.label_memory_usage.setHidden(False)
        else:
            self.label_fps.setHidden(True)
            self.label_class_info.setHidden(True)
            self.label_conf.setHidden(True)
            self.label_dim.setHidden(True)
            self.label_memory_usage.setHidden(True)

    # update color for frame and buttons
    def show_color_picker(self, button):
        color = QColorDialog.getColor()
        if color.isValid():
            # update the color tuple with the new RGB values
            color_tuple = (color.red(), color.green(), color.blue())
            # set the background color of the button using stylesheet
            button.setStyleSheet(f"background-color: rgb({color.red()}, {color.green()}, {color.blue()})")
            # update the original color tuple with the new RGB values
            if button == self.btn_color_box:
                self.box_color = color_tuple
            elif button == self.btn_color_class:
                self.text_color_class = color_tuple
            elif button == self.btn_color_conf:
                self.text_color_conf = color_tuple
            elif button == self.btn_color_bg:
                self.text_color_bg = color_tuple

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
        self.label_stream.setHidden(False)
        self.btn_start.setEnabled(False)
        self.cbox_camera_list.setEnabled(False)
        # start timer
        self.timer_start.start(2000)
        # set current text from cbox
        current_item = self.cbox_camera_list.currentText()

        # start worker thread
        self.start_worker_thread_camera(current_item)
        # stop worker thread
        self.stop_wroker_thread_pause_screen()
        self.qlabel_no_camera.setHidden(True)
        # set frame for Pixmap
        # self.label_stream.setStyleSheet("border: 2px solid black")

    # on click stop button
    def on_btn_stop_clicked(self):
        self.status_bar.showMessage('stream stopped..')
        # enable gui elements
        self.qlabel_no_camera.setHidden(False)
        self.label_stream.setHidden(True)
        self.btn_stop.setEnabled(False)
        QtCore.QCoreApplication.processEvents()
        self.timer_stop.start(2000)
        # stop camera thread
        self.stop_worker_thread_camera()
        self.start_wroker_thread_pause_screen()
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

    # random color
    @staticmethod
    def generate_random_tuple():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    # draw bounding box on frame
    def draw_bounding_box(self, frame, bbox_x1, bbox_y1, bbox_x2, bbox_y2):
        if self.cbox_enable_bbox.isChecked():
            cv2.rectangle(frame, (bbox_x1, bbox_y1), (bbox_x2, bbox_y2), self.box_color, self.box_thickness)

    # draw class name on frame
    def draw_information(self, frame, class_name, confidence):
        # example text to get dimensions of actual text
        text_size, _ = cv2.getTextSize('confidence: 100.00%', self.text_font,
                                       self.text_font_scale, self.text_thickness)
        # extract width and height from text size
        width = text_size[0]
        height = text_size[1]
        # get frame dimensions
        (frame_height, frame_width) = frame.shape[:2]
        # initialize coordinates for rectangle (x1,y1) bottom left, (x2,y2) top right
        x1, x2, y1, y2 = None, None, None, None
        # check which radio button is selected
        # bottom left corner
        if self.button_group.checkedId() == 1:
            # set text to bottom left
            x_bottom_left = 10
            y_bottom_left = frame_height - 10
            x1, y1, x2, y2 = x_bottom_left, y_bottom_left, x_bottom_left + width, y_bottom_left - height
        # bottom right corner
        elif self.button_group.checkedId() == 2:
            # set text to bottom right
            x_bottom_right = frame_width - width - 10
            y_bottom_right = frame_height - 10
            x1, y1, x2, y2 = x_bottom_right, y_bottom_right, x_bottom_right + width, y_bottom_right - height
        # top left corner
        elif self.button_group.checkedId() == 3:
            # set text to top left
            x_top_left = 10
            y_top_left = height + 25
            x1, y1, x2, y2 = x_top_left, y_top_left, x_top_left + width, y_top_left - height
        # yop right corner
        elif self.button_group.checkedId() == 4:
            # set text to top right
            x_top_right = frame_width - width - 10
            y_top_right = height + 25
            x1, y1, x2, y2 = x_top_right, y_top_right, x_top_right + width, y_top_right - height
        # space between text and border of rectangle
        border_space = 10
        if self.cbox_enable_info_background.isChecked():
            # class is checked
            if self.cbox_enable_class.isChecked() & (not self.cbox_enable_conf.isChecked()):
                # draw black box background
                cv2.rectangle(frame, (x1, y1 + (int((self.text_font_scale * 100) / 10))),
                              (x2, y2),
                              self.text_color_bg, -1)
            # conf is checked
            elif self.cbox_enable_conf.isChecked() & (not self.cbox_enable_class.isChecked()):
                # draw black box background
                cv2.rectangle(frame, (x1, y2 + (int((self.text_font_scale * 100) / 10)) - border_space),
                              (x2, y2 - (y1 - y2) - border_space),
                              self.text_color_bg, -1)
            # class and conf is checked
            elif self.cbox_enable_class.isChecked() & self.cbox_enable_conf.isChecked():
                # draw black box background
                cv2.rectangle(frame, (x1, y1 + (int((self.text_font_scale * 100) / 10))),
                              (x2, y2 - (y1 - y2) - border_space),
                              self.text_color_bg, -1)
        if self.cbox_enable_conf.isChecked():
            # draw confidence score
            cv2.putText(frame, 'confidence: ' + '{:.2f}'.format(confidence * 100) + '%',
                        (x1, y1 + (y2 - y1) - border_space),
                        self.text_font,
                        self.text_font_scale, self.text_color_conf, self.text_thickness, cv2.LINE_AA)
        if self.cbox_enable_class.isChecked():
            # draw class name
            cv2.putText(frame, 'sitting: good' if class_name == 0 else 'sitting: bad', (x1, y1),
                        self.text_font,
                        self.text_font_scale, self.text_color_class, self.text_thickness, cv2.LINE_AA)
        if class_name == 0:
            self.label_stream.setStyleSheet("border: 2px solid {}".format('green'))
        else:
            self.label_stream.setStyleSheet("border: 2px solid {}".format('red'))

    # draw items on frame
    def draw_items(self, frame, bbox_x1, bbox_y1, bbox_x2, bbox_y2, class_name, confidence):
        self.draw_bounding_box(frame, bbox_x1, bbox_y1, bbox_x2, bbox_y2)
        self.draw_information(frame, class_name, confidence)

    # display frame to qlabel_stream
    def draw_frame(self, img, fps, results):
        if self.flag_is_camera_thread_running:
            self.status_bar.showMessage('getting camera stream..')
        QtCore.QCoreApplication.processEvents()
        class_name, confidence = None, None
        # convert to rgb format
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # resize to fit into QImage element
        if frame.shape[0] > frame.shape[1]:
            frame = self.image_resize(frame, None, self.IMAGE_BOX_SIZE)
        else:
            frame = self.image_resize(frame, self.IMAGE_BOX_SIZE)
        # get height and width of frame
        height, width = frame.shape[:2]
        # format results as pandas table
        results = results.pandas().xyxy[0].to_dict(orient="records")
        if results:
            # get single results from prediction
            (bbox_x1, bbox_y1, bbox_x2, bbox_y2, class_name, confidence) = self.get_results(results)
            self.draw_items(frame, bbox_x1, bbox_y1, bbox_x2, bbox_y2, class_name, confidence)
        else:
            self.label_stream.setStyleSheet("border: 2px solid black")
        # convert frame to QPixmap format
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        # add border to frame
        pixmap = self.draw_black_border(pixmap)
        if self.flag_is_camera_thread_running:
            self.update_statusbar(height, width, fps, class_name, confidence)
        else:
            self.update_statusbar()
        self.label_stream.setPixmap(QPixmap.fromImage(pixmap))
        self.label_stream.adjustSize()
        self.label_stream.update()

    # extract items from results
    def get_results(self, results):
        (bbox_x1, bbox_y1, bbox_x2, bbox_y2, class_name, confidence) = None, None, None, None, None, None
        for result in results:
            confidence = result['confidence']
            class_name = result['class']
            bbox_x1 = int(result['xmin'])
            bbox_y1 = int(result['ymin'])
            bbox_x2 = int(result['xmax'])
            bbox_y2 = int(result['ymax'])
        return bbox_x1, bbox_y1, bbox_x2, bbox_y2, class_name, confidence

    # draw black border around frame
    def draw_black_border(self, pixmap):
        border_width = self.label_stream.width()
        border_height = self.label_stream.height()
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
    def update_statusbar(self, height=None, width=None, fps=None, class_name=None, confidence=None):
        # update image size label
        if (height is None) & (width is None):
            self.label_dim.setText("image size: -")
        else:
            self.label_dim.setText("image size: " + str(width) + "x" + str(height))
        # update fps label
        if fps is None:
            self.label_fps.setText("fps: -")
        else:
            self.label_fps.setText("fps: {:.2f}".format(fps))
        # update detected class
        if class_name is None:
            self.label_class_info.setText("detected class: no class")
        elif class_name == 0:
            self.label_class_info.setText("detected class: sitting_good")
        else:
            self.label_class_info.setText("detected class: sitting_bad")
        # update confidence
        if confidence is None:
            self.label_conf.setText('conf: -')
        else:
            self.label_conf.setText('conf: {:.2f}'.format(confidence))

    # update pixmap with when no camera is available
    def update_pause_frame(self, pixmap):
        print(pixmap)
        self.qlabel_no_camera.adjustSize()
        self.qlabel_no_camera.setPixmap(pixmap)
        # self.qlabel_no_camera.repaint()
        self.qlabel_no_camera.update()

    # start camera worker thread
    def start_wroker_thread_pause_screen(self):
        self.worker_thread_pause_screen = WorkerThreadPauseScreen(self.qlabel_stream_width, self.qlabel_stream_height)
        self.worker_thread_pause_screen.update_pause_screen.connect(self.update_pause_frame)
        self.worker_thread_pause_screen.start()

    # stop pause screen worker thread
    def stop_wroker_thread_pause_screen(self):
        self.worker_thread_pause_screen.stop()

    # initialize worker thread for camera capture
    def start_worker_thread_camera(self, current_item):
        self.work_thread_camera = WorkerThreadCamera(self.camera_mapping.get(current_item))
        self.work_thread_camera.update_camera.connect(self.draw_frame)
        self.work_thread_camera.start()

    # stop camera worker thread
    def stop_worker_thread_camera(self):
        if self.work_thread_camera is not None:
            self.work_thread_camera.stop()
            self.work_thread_camera.wait()
            self.work_thread_camera = None
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        cv2.destroyAllWindows()
        self.flag_is_camera_thread_running = False

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
        self.worker_thread_memory.stop()


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
