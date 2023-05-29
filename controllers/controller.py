import os

import cv2
import psutil
from IPython.external.qt_for_kernel import QtCore
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap, QColor, QPainter
from PyQt5.QtWidgets import QColorDialog, QDesktopWidget

from util.helper import camera_helper, frame_helper
from util.helper.load_model import InferenceModel
from util.threads.worker_thread_frame import WorkerThreadFrame
from util.threads.worker_thread_pause_screen import WorkerThreadPauseScreen
from views.fullscreen_view import FullscreenView


class Controller():
    def __init__(self, model, view):
        super().__init__()
        self.worker_thread_pause_screen = None
        self.work_thread_camera = None
        self.model = model
        self.is_fullscreen = True

    @staticmethod
    def show_fullscreen(view):
        view.fullscreen_window.showFullScreen()

    def on_fullscreen_closed(self):
        self.is_fullscreen = False

    @staticmethod
    def on_button_pressed(button, path):
        button.setIcon(QIcon(path))

    @staticmethod
    def on_button_released(button, path):
        button.setIcon(QIcon(path))

    @staticmethod
    def update_last_update_time(view):
        view.last_update_time = QDateTime.currentDateTime()

    @staticmethod
    def check_idle_time(view):
        if view.status_bar.currentMessage() == "Idle":
            return
        current_time = QDateTime.currentDateTime()
        if view.last_update_time.msecsTo(current_time) >= 1000:
            view.status_bar.showMessage('Idle')

    # update color for frame and buttons
    @staticmethod
    def show_color_picker(view, button):
        """
        Shows the color picker menu

        Args:
            button: The button which the color is applied.
            view:
        """
        color = QColorDialog.getColor()
        if color.isValid():
            # update the color tuple with the new RGB values
            color_tuple = (color.red(), color.green(), color.blue())
            # set the background color of the button using stylesheet
            button.setStyleSheet(f'background-color: rgb({color.red()}, {color.green()}, {color.blue()});border: none')
            # update the original color tuple with the new RGB values
            if button == view.button_color_box:
                view.box_color = color_tuple
            elif button == view.button_color_class:
                view.text_color_class = color_tuple
            elif button == view.button_color_confidence:
                view.text_color_conf = color_tuple
            elif button == view.button_color_bg:
                view.text_color_bg = color_tuple

    # on timeout stop button
    @staticmethod
    def timer_timeout_stop(view):
        """
        Stops the timeout timer
        """
        # stop timer and toggle button state
        view.timer_stop.stop()
        if not view.button_stop.isEnabled():
            view.button_start.setEnabled(True)
            view.combobox_camera_list.setEnabled(True)

    # on timeout start button
    @staticmethod
    def timer_timeout_start(view):
        """
        Starts the timeout timer

        """
        # stop timer and toggle button state
        view.timer_start.stop()
        if not view.button_start.isEnabled():
            view.button_stop.setEnabled(True)

    # update combobox items with current available cameras
    def on_combobox_camera_list_changed(self, view):
        QtCore.QCoreApplication.processEvents()
        view.combobox_camera_list.setEnabled(False)
        view.button_start.setEnabled(False)
        view.button_stop.setEnabled(False)
        # workaround to process the stack otherwise it will ignore the statements above
        QtCore.QCoreApplication.processEvents()
        if camera_helper.is_camera_connected():
            self.update_combobox_camera_list_items(view)
            view.button_start.setEnabled(True)
        else:
            view.button_start.setEnabled(False)
        view.combobox_camera_list.setEnabled(True)
        view.button_stop.setEnabled(False)
        QtCore.QCoreApplication.processEvents()

    # update combobox items
    @staticmethod
    def update_combobox_camera_list_items(view):
        view.status_bar.showMessage('Updating camera list..')
        QtCore.QCoreApplication.processEvents()
        view.combobox_camera_list.currentTextChanged.disconnect(Controller.on_combobox_camera_list_changed)
        text = view.combobox_camera_list.currentText()
        view.camera_mapping = camera_helper.get_camera_mapping(camera_helper.get_connected_camera_alias(),
                                                               camera_helper.get_connected_camera_ids())
        view.combobox_camera_list.clear()
        view.combobox_camera_list.addItems(view.camera_mapping.keys())
        index = view.combobox_camera_list.findText(text, QtCore.Qt.MatchFixedString)
        if index >= 0:
            view.combobox_camera_list.setCurrentIndex(index)
        view.combobox_camera_list.currentTextChanged.connect(Controller.on_combobox_camera_list_changed)

    # update memory and cpu usage in statusbar
    @staticmethod
    def update_system_resource(model, view):
        model.memory_usage = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
        view.label_memory_usage.setText('Memory: {:.0f} MB'.format(model.memory_usage))
        model.cpu_usage = psutil.cpu_percent(interval=None, percpu=False)
        view.label_cpu_usage.setText('CPU: {:.0f} %'.format(model.cpu_usage))

    @staticmethod
    def update_slider_text(control, label):
        """
        Updates the text of the QLabel besides the slider

        Args:
            control: the control object to read from.
            label: the label to be updated.
        """
        label.setText(str(control.value()) + '%')

    @staticmethod
    def center_window(view):
        """
        Centers the main window

        """
        qr = view.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        view.move(qr.topLeft())

    @staticmethod
    def set_border_color(label, color):
        label.setStyleSheet('border: 4px solid {}'.format(color))

    # show or hide debug features
    @staticmethod
    def set_debug_mode(view):
        if view.cbox_enable_debug.isChecked():
            view.label_fps.setHidden(False)
            view.label_class_info.setHidden(False)
            view.label_conf.setHidden(False)
            view.label_dim.setHidden(False)
            view.label_memory_usage.setHidden(False)
            view.label_cpu_usage.setHidden(False)
        else:
            view.label_fps.setHidden(True)
            view.label_class_info.setHidden(True)
            view.label_conf.setHidden(True)
            view.label_dim.setHidden(True)
            view.label_memory_usage.setHidden(True)
            view.label_cpu_usage.setHidden(True)

    @staticmethod
    def start_worker_thread_camera(view, model):
        current_item = view.combobox_camera_list.currentText()
        Controller.work_thread_camera = WorkerThreadFrame(model.inference_model, model.camera_mapping.get(current_item),
                                                          view.slider_brightness,
                                                          view.slider_contrast)
        Controller.work_thread_camera.update_camera.connect(Controller.draw_frame)
        Controller.work_thread_camera.start()

    @staticmethod
    def stop_worker_thread_pause_screen(view):
        view.worker_thread_pause_screen.stop()

    # stop camera worker thread
    def stop_worker_thread_camera(self):
        if self.work_thread_camera is not None:
            self.work_thread_camera.stop()
            self.work_thread_camera.wait()
            self.work_thread_camera = None
        if self.model.camera is not None:
            self.model.camera.release()
            self.model.camera = None
        cv2.destroyAllWindows()
        self.model.flag_is_camera_thread_running = False

    @staticmethod
    def on_button_start_clicked(view, model):
        model.flag_is_camera_thread_running = True
        # disable gui elements
        view.label_stream.setHidden(False)
        view.button_start.setEnabled(False)
        view.combobox_camera_list.setEnabled(False)
        # start timer
        view.timer_start.start(2000)
        # set current text from cbox

        # start worker thread
        Controller.start_worker_thread_camera(view, model)
        # stop worker thread
        Controller.stop_worker_thread_pause_screen(view)
        view.label_no_camera.setHidden(True)

    @staticmethod
    def on_button_stop_clicked(view):
        view.status_bar.showMessage('Stream stopped..')
        # enable gui elements
        view.label_no_camera.setHidden(False)
        view.label_stream.setHidden(True)
        view.button_stop.setEnabled(False)
        QtCore.QCoreApplication.processEvents()
        view.timer_stop.start(2000)
        # stop camera thread
        view.stop_worker_thread_camera()
        view.start_worker_thread_pause_screen()

    # display frame to label_stream
    def draw_frame(self, img, fps, results):
        if self.model.flag_is_camera_thread_running:
            self.model.status_bar.showMessage('Getting camera stream..')
        QtCore.QCoreApplication.processEvents()
        class_name, confidence = None, None
        # convert to rgb format
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # resize to fit into QImage element
        if frame.shape[0] > frame.shape[1]:
            frame = frame_helper.resize_frame(frame, None, self.model.IMAGE_BOX_SIZE)
        else:
            frame = frame_helper.resize_frame(frame, self.model.IMAGE_BOX_SIZE)
        # get height and width of frame
        height, width = frame.shape[:2]
        # format results as pandas table
        # results = results.pandas().xyxy[0].to_dict(orient="records")
        if len(results.pandas().xyxy[0].value_counts('name')) > 0:
            # get single results from prediction
            (bbox_x1, bbox_y1, bbox_x2, bbox_y2, class_name, confidence) = InferenceModel.get_results(results)
            self.draw_items(frame, bbox_x1, bbox_y1, bbox_x2, bbox_y2, class_name, confidence)
        else:
            self.set_border_color(self.model.label_stream, 'black')
            (bbox_x1, bbox_y1, bbox_x2, bbox_y2, class_name, confidence) = InferenceModel.get_results(results)
        # convert frame to QPixmap format
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.model.pixmap = QPixmap.fromImage(q_image)
        # add border to frame
        self.model.pixmap = self.draw_black_border(self.model.pixmap)
        if self.model.flag_is_camera_thread_running:
            self.update_statusbar(height, width, fps, class_name, confidence)
        else:
            self.update_statusbar()
        if self.is_fullscreen:
            self.fullscreen_window.set_central_widget_content(self.model.pixmap)
        else:
            self.model.label_stream.setPixmap(QPixmap.fromImage(self.model.pixmap))
        self.model.label_stream.adjustSize()
        self.model.label_stream.update()

    # draw items on frame
    def draw_items(self, frame, bbox_x1, bbox_y1, bbox_x2, bbox_y2, class_name, confidence):
        self.draw_bounding_box(frame, bbox_x1, bbox_y1, bbox_x2, bbox_y2)
        self.draw_information(frame, class_name, confidence)

    # draw black border around frame
    def draw_black_border(self, pixmap):
        border_width = self.model.label_stream.width()
        border_height = self.model.label_stream.height()
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

    # draw bounding box on frame
    def draw_bounding_box(self, frame, bbox_x1, bbox_y1, bbox_x2, bbox_y2):
        if self.model.cbox_enable_bbox.isChecked():
            cv2.rectangle(frame, (bbox_x1, bbox_y1), (bbox_x2, bbox_y2), self.box_color, self.model.box_thickness)

    # draw class name on frame
    def draw_information(self, frame, class_name, confidence):
        # example text to get dimensions of actual text
        text_size, _ = cv2.getTextSize('confidence: 100.00%', self.model.text_font,
                                       self.model.text_font_scale, self.model.text_thickness)
        # extract width and height from text size
        width = text_size[0]
        height = text_size[1]
        # get frame dimensions
        (frame_height, frame_width) = frame.shape[:2]
        # initialize coordinates for rectangle (x1,y1) bottom left, (x2,y2) top right
        x1, x2, y1, y2 = None, None, None, None

        # check which radio button is selected
        # bottom left corner
        if self.model.button_group.checkedId() == 1:
            # set text to bottom left
            x_bottom_left = 10
            y_bottom_left = frame_height - 10
            x1, y1, x2, y2 = x_bottom_left, y_bottom_left, x_bottom_left + width, y_bottom_left - height
        # bottom right corner
        elif self.model.button_group.checkedId() == 2:
            # set text to bottom right
            x_bottom_right = frame_width - width - 10
            y_bottom_right = frame_height - 10
            x1, y1, x2, y2 = x_bottom_right, y_bottom_right, x_bottom_right + width, y_bottom_right - height
        # top left corner
        elif self.model.button_group.checkedId() == 3:
            # set text to top left
            x_top_left = 10
            y_top_left = height + 25
            x1, y1, x2, y2 = x_top_left, y_top_left, x_top_left + width, y_top_left - height
        # yop right corner
        elif self.model.button_group.checkedId() == 4:
            # set text to top right
            x_top_right = frame_width - width - 10
            y_top_right = height + 25
            x1, y1, x2, y2 = x_top_right, y_top_right, x_top_right + width, y_top_right - height
        # space between text and border of rectangle
        border_space = 10
        if self.model.cbox_enable_info_background.isChecked():
            # class is checked
            if self.model.cbox_enable_class.isChecked() & (not self.model.cbox_enable_conf.isChecked()):
                # draw black box background
                cv2.rectangle(frame, (x1, y1 + (int((self.model.text_font_scale * 100) / 10))),
                              (x2, y2),
                              self.text_color_bg, -1)
            # conf is checked
            elif self.model.cbox_enable_conf.isChecked() & (not self.model.cbox_enable_class.isChecked()):
                # draw black box background
                cv2.rectangle(frame, (x1, y2 + (int((self.model.text_font_scale * 100) / 10)) - border_space),
                              (x2, y2 - (y1 - y2) - border_space),
                              self.text_color_bg, -1)
            # class and conf is checked
            elif self.model.cbox_enable_class.isChecked() & self.model.cbox_enable_conf.isChecked():
                # draw black box background
                cv2.rectangle(frame, (x1, y1 + (int((self.model.text_font_scale * 100) / 10))),
                              (x2, y2 - (y1 - y2) - border_space),
                              self.text_color_bg, -1)
        if self.model.cbox_enable_conf.isChecked():
            # draw confidence score
            cv2.putText(frame, 'confidence: ' + '{:.2f}'.format(confidence * 100) + '%',
                        (x1, y1 + (y2 - y1) - border_space),
                        self.model.text_font,
                        self.model.text_font_scale, self.text_color_conf, self.model.text_thickness, cv2.LINE_AA)
        if self.model.cbox_enable_class.isChecked():
            # draw class name
            cv2.putText(frame, 'sitting: good' if class_name == 0 else 'sitting: bad', (x1, y1),
                        self.model.text_font,
                        self.model.text_font_scale, self.text_color_class, self.model.text_thickness, cv2.LINE_AA)
        if class_name == 0:
            self.set_border_color(self.model.label_stream, 'green')
        else:
            self.set_border_color(self.model.label_stream, 'red')

    # update the statusbar while streaming
    def update_statusbar(self, height=None, width=None, fps=None, class_name=None, confidence=None):
        # update image size label
        if (height is None) & (width is None):
            self.model.label_dim.setText("Image size: -")
        else:
            self.model.label_dim.setText("Image size: " + str(width) + "x" + str(height))
        # update fps label
        if fps is None:
            self.model.label_fps.setText("FPS: 0.00")
        else:
            self.model.label_fps.setText("FPS: {:.2f}".format(fps))
        # update detected class
        if class_name is None:
            self.model.label_class_info.setText("Class: -")
        elif class_name == 0:
            self.model.label_class_info.setText("Class: 0")
        else:
            self.model.label_class_info.setText("Class: 1")
        # update confidence
        if confidence is None:
            self.model.label_conf.setText('Confidence: 0.00')
        else:
            self.model.label_conf.setText('Confidence: {:.2f}'.format(confidence))

    # start camera worker thread
    def start_worker_thread_pause_screen(self):
        self.worker_thread_pause_screen = WorkerThreadPauseScreen(self.model.label_stream_width,
                                                                  self.model.label_stream_height)
        self.worker_thread_pause_screen.update_pause_screen.connect(self.update_pause_frame)
        self.worker_thread_pause_screen.start()
