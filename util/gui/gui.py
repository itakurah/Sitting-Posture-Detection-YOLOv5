import sys

from PyQt5 import QtGui
from PyQt5.QtCore import QTimer, QSize
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QComboBox, QLabel, QPushButton, QGroupBox, QRadioButton, QButtonGroup, QCheckBox, \
    QStatusBar, QDesktopWidget, QColorDialog, QSlider, QWidget

from util.helper.camera_helper import get_connected_camera_alias
from util.threads.worker_thread_pause_screen import WorkerThreadPauseScreen
from util.threads.worker_thread_system_resource import WorkerThreadSystemResource

'''Class for creating the application view
'''

COMMIT = ''
# read current commit hash
with open('./commit_hash.txt', 'r') as file:
    COMMIT = file.read()


def load(self):
    """
    Loads the gui components
    """
    # window properties
    self.gui_width = 870
    self.gui_height = 540
    self.setWindowTitle('Sitting Posture Detector (commit {})'.format(COMMIT))
    self.setGeometry(100, 100, self.gui_width, self.gui_height)
    self.setFixedSize(self.gui_width, self.gui_height)

    # Set icon
    self.setWindowIcon(QtGui.QIcon('images/logo.png'))
    # Set taskbar icon in Windows
    if sys.platform.startswith('win'):
        import ctypes
        # Specify app name
        id = '{}'.format(COMMIT)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(id)

    # centers the window
    center_window(self)

    # combobox properties
    combobox_camera_list_width = 200
    combobox_camera_list_x = 20
    combobox_camera_list_y = 20

    self.combobox_camera_list = QComboBox(self)
    self.combobox_camera_list.addItems(get_connected_camera_alias())
    self.combobox_camera_list.move(combobox_camera_list_x, combobox_camera_list_y)
    self.combobox_camera_list.setFixedWidth(combobox_camera_list_width)
    self.combobox_camera_list.setFixedHeight(25)

    # image label properties
    self.label_stream = QLabel(self)
    self.label_stream.setStyleSheet('border: 2px solid black; background-color: black;')
    self.label_stream_width = 600
    self.label_stream_height = 450
    self.label_stream.setFixedWidth(self.label_stream_width)
    self.label_stream.setFixedHeight(self.label_stream_height)
    self.label_stream.move(combobox_camera_list_x, combobox_camera_list_y + 30)
    self.label_stream.setHidden(True)

    # fullscreen button
    self.button_fullscreen = QPushButton('', self.label_stream)
    self.button_fullscreen.move(self.label_stream.width() - 45, self.label_stream.height() - 45)
    self.button_fullscreen.setFixedWidth(45)
    self.button_fullscreen.setFixedHeight(45)
    self.button_fullscreen.setToolTip('Enable/Disable fullscreen')
    self.button_fullscreen.setIcon(QIcon('images/fullscreen_icon.png'))
    self.button_fullscreen.setIconSize(QSize(25, 25))
    self.button_fullscreen.clicked.connect(self.enable_fullscreen)

    # image label properties
    self.label_no_camera = QLabel(self)
    self.label_no_camera.setStyleSheet('border: 0px solid black')
    self.label_no_camera.setFixedWidth(self.label_stream_width)
    self.label_no_camera.setFixedHeight(self.label_stream_height)
    self.label_no_camera.move(combobox_camera_list_x, combobox_camera_list_y + 30)

    # start button properties
    button_start_width = 80
    button_start_height = 27
    button_start_x = combobox_camera_list_x + combobox_camera_list_width + 5
    button_start_y = 50
    self.button_start = QPushButton('Start', self)
    self.button_start.setToolTip('Start camera stream')
    self.button_start.setFixedHeight(button_start_height)
    self.button_start.setFixedWidth(button_start_width)
    self.button_start.move(button_start_x, combobox_camera_list_y - 1)

    # btn_stop
    button_stop_x = button_start_width + button_start_x + 5
    button_stop_y = 50
    self.button_stop = QPushButton('Stop', self)
    self.button_stop.setToolTip('Stop camera stream')
    self.button_stop.setFixedHeight(27)
    self.button_stop.setFixedWidth(80)
    self.button_stop.move(button_stop_x, combobox_camera_list_y - 1)

    # groupbox properties
    self.groupbox_frame_options = QGroupBox(self)
    self.groupbox_frame_options.setTitle('General Options')
    self.groupbox_frame_options.setFixedHeight(self.label_stream_height)
    self.groupbox_frame_options.setFixedWidth(230)
    self.groupbox_frame_options.move(630, 50)

    # flip horizontal button
    self.button_flip_horizontal = QPushButton('', self.groupbox_frame_options)
    self.button_flip_horizontal.move(10, 355)
    self.button_flip_horizontal.setToolTip('Flip image horizontal')
    self.button_flip_horizontal.setFixedWidth(28)
    self.button_flip_horizontal.setFixedHeight(28)
    self.button_flip_horizontal.setIcon(QIcon('images/flip_horizontal.png'))
    self.button_flip_horizontal.setIconSize(QSize(25, 25))
    self.button_flip_horizontal.pressed.connect(lambda: on_button_pressed(self.button_flip_horizontal, 'images'
                                                                                                       '/flip_horizontal_pressed'
                                                                                                       '.png'))
    self.button_flip_horizontal.released.connect(lambda: on_button_released(self.button_flip_horizontal, 'images'
                                                                                                         '/flip_horizontal'
                                                                                                         '.png'))

    # flip vertical button
    self.button_flip_vertical = QPushButton('', self.groupbox_frame_options)
    self.button_flip_vertical.move(45, 355)
    self.button_flip_vertical.setToolTip('Flip image vertical')
    self.button_flip_vertical.setFixedWidth(28)
    self.button_flip_vertical.setFixedHeight(28)
    self.button_flip_vertical.setIcon(QIcon('images/flip_vertical.png'))
    self.button_flip_vertical.setIconSize(QSize(25, 25))
    self.button_flip_vertical.pressed.connect(lambda: on_button_pressed(self.button_flip_vertical, 'images'
                                                                                                   '/flip_vertical_pressed'
                                                                                                   '.png'))
    self.button_flip_vertical.released.connect(lambda: on_button_released(self.button_flip_vertical, 'images'
                                                                                                     '/flip_vertical'
                                                                                                     '.png'))

    # rotate button
    self.button_rotate = QPushButton('', self.groupbox_frame_options)
    self.button_rotate.move(80, 355)
    self.button_rotate.setToolTip('Rotate image by 90 degrees')
    self.button_rotate.setFixedWidth(28)
    self.button_rotate.setFixedHeight(28)
    self.button_rotate.setIcon(QIcon('images/rotate.png'))
    self.button_rotate.setIconSize(QSize(25, 25))
    self.button_rotate.pressed.connect(lambda: on_button_pressed(self.button_rotate, 'images'
                                                                                     '/rotate_pressed'
                                                                                     '.png'))
    self.button_rotate.released.connect(lambda: on_button_released(self.button_rotate, 'images'
                                                                                       '/rotate'
                                                                                       '.png'))

    # radio buttons properties
    self.current_rb_selected = None
    self.button_group = QButtonGroup(self)
    self.radiobutton_bl = QRadioButton('Bottom-left', self.groupbox_frame_options)
    self.radiobutton_bl.move(10, 65)
    self.radiobutton_bl.setToolTip('Displays information in the bottom-left corner')
    self.radiobutton_br = QRadioButton('Bottom-right', self.groupbox_frame_options)
    self.radiobutton_br.move(110, 65)
    self.radiobutton_br.setToolTip('Displays information in the bottom-right corner')
    self.radiobutton_tl = QRadioButton('Top-left', self.groupbox_frame_options)
    self.radiobutton_tl.move(10, 30)
    self.radiobutton_tl.setToolTip('Displays information in the top-left corner')
    self.radiobutton_tr = QRadioButton('Top-right', self.groupbox_frame_options)
    self.radiobutton_tr.move(110, 30)
    self.radiobutton_tr.setToolTip('Displays information in the top-right corner')
    self.radiobutton_bl.setChecked(True)
    self.button_group.addButton(self.radiobutton_bl, 1)
    self.button_group.addButton(self.radiobutton_br, 2)
    self.button_group.addButton(self.radiobutton_tl, 3)
    self.button_group.addButton(self.radiobutton_tr, 4)

    # checkbox properties
    self.cbox_enable_bbox = QCheckBox('Bounding Box', self.groupbox_frame_options)
    self.cbox_enable_bbox.move(10, 110)
    self.cbox_enable_bbox.setToolTip('Enable/Disable bounding box')
    self.cbox_enable_class = QCheckBox('Class', self.groupbox_frame_options)
    self.cbox_enable_class.move(10, 170)
    self.cbox_enable_class.setToolTip('Enable/Disable class name')
    self.cbox_enable_conf = QCheckBox('Confidence', self.groupbox_frame_options)
    self.cbox_enable_conf.move(10, 140)
    self.cbox_enable_conf.setToolTip('Enable/Disable confidence score')
    self.cbox_enable_info_background = QCheckBox('Background', self.groupbox_frame_options)
    self.cbox_enable_info_background.move(10, 200)
    self.cbox_enable_info_background.setToolTip('Enable/Disable background box')
    self.cbox_enable_bbox.setChecked(True)
    self.cbox_enable_class.setChecked(True)
    self.cbox_enable_conf.setChecked(True)
    self.cbox_enable_info_background.setChecked(True)

    # statusbar properties
    self.status_bar = QStatusBar()
    self.status_bar.setSizeGripEnabled(False)
    self.status_bar.setProperty('last_msg_time', QDateTime.currentDateTime().toSecsSinceEpoch())
    self.status_bar.setStyleSheet('background-color: #3555a0;font-weight: bold;')
    self.setStatusBar(self.status_bar)
    self.label_class_info = QLabel('Class: -')
    self.status_bar.addPermanentWidget(self.label_class_info)
    self.label_conf = QLabel('Confidence: 0.00')
    self.status_bar.addPermanentWidget(self.label_conf)
    self.label_dim = QLabel('Image size: -')
    self.status_bar.addPermanentWidget(self.label_dim)
    self.label_fps = QLabel('FPS: 0.00')
    self.status_bar.addPermanentWidget(self.label_fps)
    self.label_memory_usage = QLabel('Memory: -')
    self.status_bar.addPermanentWidget(self.label_memory_usage)
    self.label_cpu_usage = QLabel('CPU: -')
    self.status_bar.addPermanentWidget(self.label_cpu_usage)

    # create timer for buttons
    self.timer_start = QTimer()
    self.timer_stop = QTimer()
    self.timer_statusbar_idle = QTimer()
    self.last_update_time = QDateTime.currentDateTime()
    self.status_bar.messageChanged.connect(lambda: update_last_update_time(self))
    self.timer_statusbar_idle.timeout.connect(lambda: check_idle_time(self))
    self.timer_statusbar_idle.start(2000)

    self.button_color_box = QPushButton('', self.groupbox_frame_options)
    self.button_color_box.move(140, 118)
    self.button_color_box.setFixedHeight(20)
    self.button_color_box.setFixedWidth(20)
    self.button_color_class = QPushButton('', self.groupbox_frame_options)
    self.button_color_class.move(140, 178)
    self.button_color_class.setFixedHeight(20)
    self.button_color_class.setFixedWidth(20)
    self.button_color_confidence = QPushButton('', self.groupbox_frame_options)
    self.button_color_confidence.move(140, 148)
    self.button_color_confidence.setFixedHeight(20)
    self.button_color_confidence.setFixedWidth(20)
    self.button_color_bg = QPushButton('', self.groupbox_frame_options)
    self.button_color_bg.move(140, 208)
    self.button_color_bg.setFixedHeight(20)
    self.button_color_bg.setFixedWidth(20)
    self.button_color_box.setStyleSheet(
        f"background-color: rgb({self.box_color[0]}, {self.box_color[1]}, {self.box_color[2]});border: none")
    self.button_color_class.setStyleSheet(
        f"background-color: rgb({self.text_color_class[0]}, {self.text_color_class[1]}, {self.text_color_class[2]});border: none")
    self.button_color_confidence.setStyleSheet(
        f"background-color: rgb({self.text_color_conf[0]}, {self.text_color_conf[1]}, {self.text_color_conf[2]});border: none")
    self.button_color_bg.setStyleSheet(
        f"background-color: rgb({self.text_color_bg[0]}, {self.text_color_bg[1]}, {self.text_color_bg[2]});border: none")

    self.cbox_enable_debug = QCheckBox('Debug Info', self.groupbox_frame_options)
    self.cbox_enable_debug.move(10, 400)
    self.cbox_enable_debug.setToolTip('Enable/Disable debug information in the status bar')
    self.cbox_enable_debug.setChecked(True)
    self.cbox_enable_debug.stateChanged.connect(self.set_debug_mode)

    # slider properties - brightness
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
    self.label_brightness_control = QLabel(str(self.slider_brightness.value()) + '%', self.groupbox_frame_options)
    self.label_brightness_control.move(115, 270)
    self.slider_brightness.valueChanged.connect(
        lambda: update_slider_text(self.slider_brightness, self.label_brightness_control))

    # slider properties - contrast
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
    self.label_contrast_control = QLabel(str(self.slider_contrast.value()) + '%', self.groupbox_frame_options)
    self.label_contrast_control.move(115, 315)
    self.slider_contrast.valueChanged.connect(
        lambda: update_slider_text(self.slider_contrast, self.label_contrast_control))

    self.button_reset_brightness = QPushButton('Reset', self.groupbox_frame_options)
    self.button_reset_contrast = QPushButton('Reset', self.groupbox_frame_options)

    self.button_reset_brightness.setFixedWidth(68)
    self.button_reset_brightness.setFixedHeight(20)
    self.button_reset_contrast.setFixedWidth(68)
    self.button_reset_contrast.setFixedHeight(20)
    self.button_reset_contrast.move(150, 312)
    self.button_reset_brightness.move(150, 267)

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
    self.button_color_box.clicked.connect(lambda: show_color_picker(self, self.button_color_box))
    self.button_color_class.clicked.connect(lambda: show_color_picker(self, self.button_color_class))
    self.button_color_confidence.clicked.connect(lambda: show_color_picker(self, self.button_color_confidence))
    self.button_color_bg.clicked.connect(lambda: show_color_picker(self, self.button_color_bg))
    self.button_reset_brightness.clicked.connect(lambda: self.slider_brightness.setValue(100))
    self.button_reset_contrast.clicked.connect(lambda: self.slider_contrast.setValue(100))

    # load cbox items
    self.update_combobox_camera_list_items()

    # disable stop button on start
    self.button_stop.setEnabled(False)

    # set all groupboxes to specific color
    for groupBox in self.findChildren(QGroupBox):
        groupBox.setStyleSheet('QGroupBox {background-color: #323844;font-weight: bold;}')

    for groupBox in self.findChildren(QGroupBox):
        for widget in groupBox.findChildren(QWidget):
            if not isinstance(widget, QPushButton):
                widget.setStyleSheet('background-color: #323844;font-weight: bold;')
    self.button_reset_brightness.setStyleSheet('QPushButton {'
                                               'font-size: 10px;}'
                                               'QPushButton:enabled {'
                                               'background-color: #4269b9;'
                                               'border: 1px solid white;}')
    self.button_reset_contrast.setStyleSheet('QPushButton {'
                                             'font-size: 10px;}'
                                             'QPushButton:enabled {'
                                             'background-color: #4269b9;'
                                             'border: 1px solid white;}')
    self.button_rotate.setStyleSheet('QPushButton {'
                                     'font-size: 10px;}'
                                     'QPushButton:enabled {'
                                     'background-color: #4269b9;'
                                     'border: 1px solid white;}'
                                     'QToolTip {background-color: #323844; font-weight: bold; }')
    self.button_flip_horizontal.setStyleSheet('QPushButton {'
                                              'font-size: 10px;}'
                                              'QPushButton:enabled {'
                                              'background-color: #4269b9;'
                                              'border: 1px solid white;}'
                                              'QToolTip {background-color: #323844; font-weight: bold; }')
    self.button_flip_vertical.setStyleSheet('QPushButton {'
                                            'font-size: 10px;}'
                                            'QPushButton:enabled {'
                                            'background-color: #4269b9;'
                                            'border: 1px solid white;}'
                                            'QToolTip {background-color: #323844; font-weight: bold; }')
    self.button_start.setStyleSheet('QPushButton:enabled {'
                                    'background-color: #4269b9;'
                                    'border: 1px solid white;}'
                                    'QPushButton:disabled,'
                                    'QPushButton:disabled:hover {'
                                    'background-color: #323844;}'
                                    'QToolTip {background-color: #323844;'
                                    ' font-weight: bold; }')
    self.button_stop.setStyleSheet('QPushButton:enabled {'
                                   'background-color: #4269b9;'
                                   'border: 1px solid white;}'
                                   'QPushButton:disabled,'
                                   'QPushButton:disabled:hover {'
                                   'background-color: #323844;}'
                                   'QToolTip {background-color: #323844;'
                                   'font-weight: bold; }')
    self.button_fullscreen.setStyleSheet('QPushButton:enabled {'
                                         'background-color: transparent;'
                                         'border: none;}'
                                         'QToolTip {background-color: #323844;'
                                         'font-weight: bold;'
                                         'border: none}')
    # self.button_color_box.setStyleSheet('border: 1px solid black')


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
        self:
    """
    color = QColorDialog.getColor()
    if color.isValid():
        # update the color tuple with the new RGB values
        color_tuple = (color.red(), color.green(), color.blue())
        # set the background color of the button using stylesheet
        button.setStyleSheet(f'background-color: rgb({color.red()}, {color.green()}, {color.blue()});border: none')
        # update the original color tuple with the new RGB values
        if button == self.button_color_box:
            self.box_color = color_tuple
        elif button == self.button_color_class:
            self.text_color_class = color_tuple
        elif button == self.button_color_confidence:
            self.text_color_conf = color_tuple
        elif button == self.button_color_bg:
            self.text_color_bg = color_tuple


def update_slider_text(control, label):
    """
    Updates the text of the QLabel besides the slider

    Args:
        control: the control object to read from.
        label: the label to be updated.
    """
    label.setText(str(control.value()) + '%')


def update_last_update_time(self):
    self.last_update_time = QDateTime.currentDateTime()


def check_idle_time(self):
    if self.status_bar.currentMessage() == "Idle":
        return

    current_time = QDateTime.currentDateTime()
    if self.last_update_time.msecsTo(current_time) >= 1000:
        self.status_bar.showMessage('Idle')


def set_border_color(label, color):
    label.setStyleSheet('border: 4px solid {}'.format(color))


def on_button_pressed(button, path):
    button.setIcon(QIcon(path))


def on_button_released(button, path):
    button.setIcon(QIcon(path))
