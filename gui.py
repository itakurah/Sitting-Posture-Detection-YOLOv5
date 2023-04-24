from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QLabel, QPushButton, QGroupBox, QRadioButton, QButtonGroup, QCheckBox, \
    QStatusBar, QDesktopWidget, QColorDialog, QSlider

from camera_helper import get_connected_camera_alias
from worker_thread_pause_screen import WorkerThreadPauseScreen
from worker_thread_system_resource import WorkerThreadSystemResource

'''Class for creating the application view
'''


def load(self):
    """
    Loads the gui components
    """
    # window settings
    self.gui_width = 870
    self.gui_height = 540
    self.setWindowTitle("YOLO Sitting Posture Detector")
    self.setGeometry(100, 100, self.gui_width, self.gui_height)
    self.setFixedSize(self.gui_width, self.gui_height)

    # centers the window
    center_window(self)

    # combobox settings
    combobox_camera_list_width = 200
    combobox_camera_list_x = 20
    combobox_camera_list_y = 20

    self.combobox_camera_list = QComboBox(self)
    self.combobox_camera_list.addItems(get_connected_camera_alias())
    self.combobox_camera_list.move(combobox_camera_list_x, combobox_camera_list_y)
    self.combobox_camera_list.setFixedWidth(combobox_camera_list_width)
    self.combobox_camera_list.setFixedHeight(25)

    # image label settings
    self.label_stream = QLabel(self)
    self.label_stream.setStyleSheet("border: 2px solid black")
    self.label_stream_width = 600
    self.label_stream_height = 450
    self.label_stream.setFixedWidth(self.label_stream_width)
    self.label_stream.setFixedHeight(self.label_stream_height)
    self.label_stream.move(combobox_camera_list_x, combobox_camera_list_y + 30)
    self.label_stream.setHidden(True)

    # image label settings
    self.label_no_camera = QLabel(self)
    self.label_no_camera.setStyleSheet("border: 0px solid black")
    self.label_no_camera.setFixedWidth(self.label_stream_width)
    self.label_no_camera.setFixedHeight(self.label_stream_height)
    self.label_no_camera.move(combobox_camera_list_x, combobox_camera_list_y + 30)

    # start button settings
    button_start_width = 80
    button_start_height = 27
    button_start_x = combobox_camera_list_x + combobox_camera_list_width + 5
    button_start_y = 50
    self.button_start = QPushButton('Start', self)
    self.button_start.setFixedHeight(button_start_height)
    self.button_start.setFixedWidth(button_start_width)
    self.button_start.move(button_start_x, combobox_camera_list_y - 1)

    # btn_stop
    button_stop_x = button_start_width + button_start_x + 5
    button_stop_y = 50
    self.button_stop = QPushButton('Stop', self)
    self.button_stop.setFixedHeight(27)
    self.button_stop.setFixedWidth(80)
    self.button_stop.move(button_stop_x, combobox_camera_list_y - 1)

    # groupbox settings
    self.groupbox_frame_options = QGroupBox(self)
    self.groupbox_frame_options.setTitle('Frame Options')
    self.groupbox_frame_options.setFixedHeight(340)
    self.groupbox_frame_options.setFixedWidth(230)
    self.groupbox_frame_options.setStyleSheet("QGroupBox::title {"
                                              "padding-top:  8px;"
                                              "padding-left: 8px;} ")
    self.groupbox_frame_options.move(630, 50)

    # radio buttons settings
    self.current_rb_selected = None
    self.button_group = QButtonGroup(self)
    self.rb_1 = QRadioButton('Bottom-left', self.groupbox_frame_options)
    self.rb_1.move(10, 60)
    self.rb_2 = QRadioButton('Bottom-right', self.groupbox_frame_options)
    self.rb_2.move(110, 60)
    self.rb_3 = QRadioButton('Top-left', self.groupbox_frame_options)
    self.rb_3.move(10, 30)
    self.rb_4 = QRadioButton('Top-right', self.groupbox_frame_options)
    self.rb_4.move(110, 30)
    self.rb_1.setChecked(True)
    self.button_group.addButton(self.rb_1, 1)
    self.button_group.addButton(self.rb_2, 2)
    self.button_group.addButton(self.rb_3, 3)
    self.button_group.addButton(self.rb_4, 4)

    # checkbox settings
    self.cbox_enable_bbox = QCheckBox('Bounding Box', self.groupbox_frame_options)
    self.cbox_enable_bbox.move(10, 110)
    self.cbox_enable_class = QCheckBox('Class', self.groupbox_frame_options)
    self.cbox_enable_class.move(10, 170)
    self.cbox_enable_conf = QCheckBox('Confidence', self.groupbox_frame_options)
    self.cbox_enable_conf.move(10, 140)
    self.cbox_enable_info_background = QCheckBox('Background', self.groupbox_frame_options)
    self.cbox_enable_info_background.move(10, 200)
    self.cbox_enable_bbox.setChecked(True)
    self.cbox_enable_class.setChecked(True)
    self.cbox_enable_conf.setChecked(True)
    self.cbox_enable_info_background.setChecked(True)

    # statusbar settings
    self.status_bar = QStatusBar()
    self.setStatusBar(self.status_bar)
    self.label_class_info = QLabel("Class: -")
    self.status_bar.addPermanentWidget(self.label_class_info)
    self.label_conf = QLabel("Confidence: -")
    self.status_bar.addPermanentWidget(self.label_conf)
    self.label_dim = QLabel("Image size: -")
    self.status_bar.addPermanentWidget(self.label_dim)
    self.label_fps = QLabel("FPS: -")
    self.status_bar.addPermanentWidget(self.label_fps)
    self.label_memory_usage = QLabel('Memory: -')
    self.status_bar.addPermanentWidget(self.label_memory_usage)
    self.label_cpu_usage = QLabel('CPU: -')
    self.status_bar.addPermanentWidget(self.label_cpu_usage)
    self.status_bar.showMessage('Idle')

    # create timer for buttons
    self.timer_start = QTimer()
    self.timer_stop = QTimer()

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

    self.groupbox_general_options = QGroupBox(self)
    self.groupbox_general_options.setTitle('General Options')
    self.groupbox_general_options.setFixedHeight(100)
    self.groupbox_general_options.setFixedWidth(230)
    self.groupbox_general_options.setStyleSheet("QGroupBox::title {"
                                                "padding-top:  8px;"
                                                "padding-left: 8px;} ")
    self.groupbox_general_options.move(630, 390)
    self.cbox_enable_debug = QCheckBox('Debug Info', self.groupbox_general_options)
    self.cbox_enable_debug.move(10, 30)
    self.cbox_enable_debug.setChecked(True)
    self.cbox_enable_debug.stateChanged.connect(self.set_debug_mode)

    # slider settings - brightness
    self.label_brightness_control = QLabel('Brightness:', self.groupbox_frame_options)
    self.label_brightness_control.move(10, 245)
    self.slider_brightness = QSlider(Qt.Horizontal, self.groupbox_frame_options)
    self.slider_brightness.move(10, 265)
    self.slider_brightness.setFixedWidth(100)
    self.slider_brightness.setMinimum(0)
    self.slider_brightness.setMaximum(300)
    self.slider_brightness.setValue(100)
    self.slider_brightness.setSingleStep(1)
    self.slider_brightness.setTickInterval(10)
    self.slider_brightness.setStyleSheet("QSlider::add-page:horizontal {"
                                         "background: gray;"
                                         "}"
                                         "QSlider::sub-page:horizontal {"
                                         " background: gray;"
                                         "}")
    self.label_brightness_control = QLabel(str(self.slider_brightness.value()) + '%', self.groupbox_frame_options)
    self.label_brightness_control.move(115, 270)
    self.slider_brightness.valueChanged.connect(
        lambda: update_slider_text(self.slider_brightness, self.label_brightness_control))

    # slider settings - contrast
    self.label_contrast_control = QLabel('Contrast:', self.groupbox_frame_options)
    self.label_contrast_control.move(10, 290)
    self.slider_contrast = QSlider(Qt.Horizontal, self.groupbox_frame_options)
    self.slider_contrast.move(10, 310)
    self.slider_contrast.setFixedWidth(100)
    self.slider_contrast.setMinimum(0)
    self.slider_contrast.setMaximum(300)
    self.slider_contrast.setValue(100)
    self.slider_contrast.setSingleStep(1)
    self.slider_contrast.setTickInterval(10)
    self.slider_contrast.setStyleSheet("QSlider::add-page:horizontal {"
                                       "background: gray;"
                                       "}"
                                       "QSlider::sub-page:horizontal {"
                                       " background: gray;"
                                       "}")
    self.label_contrast_control = QLabel(str(self.slider_contrast.value()) + '%', self.groupbox_frame_options)
    self.label_contrast_control.move(115, 315)
    self.slider_contrast.valueChanged.connect(
        lambda: update_slider_text(self.slider_contrast, self.label_contrast_control))

    # start memory thread
    self.worker_thread_memory = WorkerThreadSystemResource()
    self.worker_thread_memory.update_memory.connect(self.update_system_resource)
    self.worker_thread_memory.start()

    # start pause screen thread
    self.worker_thread_pause_screen = WorkerThreadPauseScreen(self.label_stream_width, self.label_stream_height)
    self.worker_thread_pause_screen.update_pause_screen.connect(self.update_pause_frame)
    self.worker_thread_pause_screen.start()

    # register signals
    self.combobox_camera_list.currentTextChanged.connect(self.on_combobox_camera_list_changed)
    self.button_start.clicked.connect(self.on_button_start_clicked)
    self.button_stop.clicked.connect(self.on_button_stop_clicked)
    self.timer_start.timeout.connect(lambda: timer_timeout_start(self))
    self.timer_stop.timeout.connect(lambda: timer_timeout_stop(self))
    self.btn_color_box.clicked.connect(lambda: show_color_picker(self, self.btn_color_box))
    self.btn_color_class.clicked.connect(lambda: show_color_picker(self, self.btn_color_class))
    self.btn_color_conf.clicked.connect(lambda: show_color_picker(self, self.btn_color_conf))
    self.btn_color_bg.clicked.connect(lambda: show_color_picker(self, self.btn_color_bg))
    # load cbox items
    self.update_combobox_camera_list_items()

    # disable stop button on start
    self.button_stop.setEnabled(False)


# on timeout stop button
def timer_timeout_stop(self):
    """
    Stops the timeout timer
    """
    # stop timer and toggle button state
    self.timer_stop.stop()
    if not self.button_stop.isEnabled():
        self.button_start.setEnabled(True)
        self.combobox_camera_list.setEnabled(True)


# on timeout start button
def timer_timeout_start(self):
    """
    Starts the timeout timer

    """
    # stop timer and toggle button state
    self.timer_start.stop()
    if not self.button_start.isEnabled():
        self.button_stop.setEnabled(True)


# centers the main window
def center_window(self):
    """
    Centers the main window

    """
    qr = self.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())


# update color for frame and buttons
def show_color_picker(self, button):
    """
    Shows the color picker menu

    Args:
        button: The button which the color is applied.
    """
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


def update_slider_text(control, label):
    """
    Updates the text of the QLabel besides the slider

    Args:
        control: the control object to read from.
        label: the label to be updated.
    """
    label.setText(str(control.value()) + '%')
