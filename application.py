import os
import sys
import tempfile

import cv2
import psutil
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QColor, QPainter
from PyQt5.QtWidgets import *
from qt_material import apply_stylesheet

import camera_helper
import frame_helper
import frame_properties
import gui
from load_model import Model
from worker_thread_frame import WorkerThreadFrame
from worker_thread_pause_screen import WorkerThreadPauseScreen


class Application(QMainWindow):

    def __init__(self):
        super().__init__()
        # annotate class variables
        self.worker_thread_pause_screen = None
        self.worker_thread_memory = None
        self.label_stream_height = None
        self.label_stream_width = None
        self.slider_brightness = None
        self.text_color_class = None
        self.text_color_conf = None
        self.text_color_bg = None
        self.cbox_enable_conf = None
        self.cbox_enable_class = None
        self.cbox_enable_info_background = None
        self.button_group = None
        self.button_group = None
        self.text_thickness = None
        self.text_thickness = None
        self.text_font = None
        self.text_font = None
        self.box_color = None
        self.slider_contrast = None
        self.text_font_scale = None
        self.timer_stop = None
        self.button_stop = None
        self.label_no_camera = None
        self.box_color: None
        self.box_thickness = None
        self.status_bar = None
        self.status_bar = None
        self.cbox_enable_bbox = None
        self.timer_start = None
        self.combobox_camera_list = None
        self.button_start = None
        self.label_stream = None
        self.label_cpu_usage = None
        self.label_dim = None
        self.label_conf = None
        self.label_class_info = None
        self.cbox_enable_debug = None
        self.label_fps = None
        self.label_memory_usage = None
        self.memory_usage = None
        self.cpu_usage = None
        self.confidence = None
        self.class_name = None
        self.width = None
        self.height = None
        self.fps = None

        self.prev_frame_time = 0
        self.IMAGE_BOX_SIZE = 600
        self.flag_is_camera_thread_running = True
        self.camera_mapping = {}
        self.camera = None
        self.work_thread_camera = None

        # load frame properties
        frame_properties.load(self)
        # load gui
        gui.load(self)

    # update memory and cpu usage in statusbar
    def update_system_resource(self):
        self.memory_usage = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
        self.label_memory_usage.setText('Memory: {:.0f} MB'.format(self.memory_usage))
        self.cpu_usage = psutil.cpu_percent(interval=None, percpu=False)
        self.label_cpu_usage.setText('CPU: {:.0f} %'.format(self.cpu_usage))

    # show or hide debug features
    def set_debug_mode(self):
        if self.cbox_enable_debug.isChecked():
            self.label_fps.setHidden(False)
            self.label_class_info.setHidden(False)
            self.label_conf.setHidden(False)
            self.label_dim.setHidden(False)
            self.label_memory_usage.setHidden(False)
            self.label_cpu_usage.setHidden(False)
        else:
            self.label_fps.setHidden(True)
            self.label_class_info.setHidden(True)
            self.label_conf.setHidden(True)
            self.label_dim.setHidden(True)
            self.label_memory_usage.setHidden(True)
            self.label_cpu_usage.setHidden(True)

    # on click start button
    def on_button_start_clicked(self):
        self.flag_is_camera_thread_running = True
        # disable gui elements
        self.label_stream.setHidden(False)
        self.button_start.setEnabled(False)
        self.combobox_camera_list.setEnabled(False)
        # start timer
        self.timer_start.start(2000)
        # set current text from cbox
        current_item = self.combobox_camera_list.currentText()
        # start worker thread
        self.start_worker_thread_camera(current_item)
        # stop worker thread
        self.stop_worker_thread_pause_screen()
        self.label_no_camera.setHidden(True)

    # on click stop button
    def on_button_stop_clicked(self):
        self.status_bar.showMessage('Stream stopped..')
        # enable gui elements
        self.label_no_camera.setHidden(False)
        self.label_stream.setHidden(True)
        self.button_stop.setEnabled(False)
        QtCore.QCoreApplication.processEvents()
        self.timer_stop.start(2000)
        # stop camera thread
        self.stop_worker_thread_camera()
        self.start_worker_thread_pause_screen()
        self.status_bar.showMessage('Idle')

    # update combobox items with current available cameras
    def on_combobox_camera_list_changed(self):
        QtCore.QCoreApplication.processEvents()
        self.combobox_camera_list.setEnabled(False)
        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(False)
        # workaround to process the stack otherwise it will ignore the statements above
        QtCore.QCoreApplication.processEvents()
        if camera_helper.is_camera_connected():
            self.update_combobox_camera_list_items()
            self.button_start.setEnabled(True)
        else:
            self.button_start.setEnabled(False)
        self.combobox_camera_list.setEnabled(True)
        self.button_stop.setEnabled(False)
        QtCore.QCoreApplication.processEvents()

    # update combobox items 
    def update_combobox_camera_list_items(self):
        self.status_bar.showMessage('Updating camera list..')
        QtCore.QCoreApplication.processEvents()
        self.combobox_camera_list.currentTextChanged.disconnect(self.on_combobox_camera_list_changed)
        text = self.combobox_camera_list.currentText()
        self.camera_mapping = camera_helper.get_camera_mapping(camera_helper.get_connected_camera_alias(),
                                                               camera_helper.get_connected_camera_ids())
        self.combobox_camera_list.clear()
        self.combobox_camera_list.addItems(self.camera_mapping.keys())
        index = self.combobox_camera_list.findText(text, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.combobox_camera_list.setCurrentIndex(index)
        self.combobox_camera_list.currentTextChanged.connect(self.on_combobox_camera_list_changed)

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

    # display frame to label_stream
    def draw_frame(self, img, fps, results):
        if self.flag_is_camera_thread_running:
            self.status_bar.showMessage('Getting camera stream..')
        QtCore.QCoreApplication.processEvents()
        class_name, confidence = None, None
        # convert to rgb format
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # resize to fit into QImage element
        if frame.shape[0] > frame.shape[1]:
            frame = frame_helper.resize_frame(frame, None, self.IMAGE_BOX_SIZE)
        else:
            frame = frame_helper.resize_frame(frame, self.IMAGE_BOX_SIZE)
        # get height and width of frame
        height, width = frame.shape[:2]
        # format results as pandas table
        results = results.pandas().xyxy[0].to_dict(orient="records")
        if results:
            # get single results from prediction
            (bbox_x1, bbox_y1, bbox_x2, bbox_y2, class_name, confidence) = Model.get_results(results)
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
            self.label_dim.setText("Image size: -")
        else:
            self.label_dim.setText("Image size: " + str(width) + "x" + str(height))
        # update fps label
        if fps is None:
            self.label_fps.setText("FPS: 0.00")
        else:
            self.label_fps.setText("FPS: {:.2f}".format(fps))
        # update detected class
        if class_name is None:
            self.label_class_info.setText("Class: -")
        elif class_name == 0:
            self.label_class_info.setText("Class: 0")
        else:
            self.label_class_info.setText("Class: 1")
        # update confidence
        if confidence is None:
            self.label_conf.setText('Confidence: 0.00')
        else:
            self.label_conf.setText('Confidence: {:.2f}'.format(confidence))

    # update pixmap with when no camera is available
    def update_pause_frame(self, pixmap):
        self.label_no_camera.adjustSize()
        self.label_no_camera.setPixmap(pixmap)
        self.label_no_camera.update()

    # start camera worker thread
    def start_worker_thread_pause_screen(self):
        self.worker_thread_pause_screen = WorkerThreadPauseScreen(self.label_stream_width, self.label_stream_height)
        self.worker_thread_pause_screen.update_pause_screen.connect(self.update_pause_frame)
        self.worker_thread_pause_screen.start()

    # stop pause screen worker thread
    def stop_worker_thread_pause_screen(self):
        self.worker_thread_pause_screen.stop()

    # initialize worker thread for camera capture
    def start_worker_thread_camera(self, current_item):
        self.work_thread_camera = WorkerThreadFrame(self.camera_mapping.get(current_item), self.slider_brightness,
                                                    self.slider_contrast)
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

    def closeEvent(self, event):
        cv2.destroyAllWindows()
        self.stop_worker_thread_camera()
        self.worker_thread_memory.stop()


style = '''<!--?xml version="1.0" encoding="UTF-8"?-->
<resources>
  <color name="primaryColor">#ffffff</color>
  <color name="primaryLightColor">#6e6d6d</color>
  <color name="secondaryColor">#323844</color>
  <color name="secondaryLightColor">#4f5b62</color>
  <color name="secondaryDarkColor">#31363b</color>
  <color name="primaryTextColor">#ffffff</color>
  <color name="secondaryTextColor">#ffffff</color>
</resources>'''

app = QApplication([])
window = Application()
with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
    # Write the XML string to the temporary file
    tmp.write(style.encode('utf-8'))
    # Close the temporary file
    tmp.close()
    apply_stylesheet(app, theme=tmp.name, css_file='custom.css')
os.unlink(tmp.name)
window.show()
sys.exit(app.exec())
