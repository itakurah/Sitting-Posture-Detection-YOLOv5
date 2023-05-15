from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QLabel, QMainWindow


class FullscreenWindow(QMainWindow):
    fullscreen_closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.label = QLabel()
        self.label.setStyleSheet("background-color: black;")
        self.label.setAlignment(Qt.AlignCenter)
        self.setWindowState(Qt.WindowFullScreen)

    def set_central_widget_content(self, pixmap):
        if pixmap is not None:
            pixmap_scaled = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
            self.label.setPixmap(QPixmap.fromImage(pixmap_scaled))
        self.setCentralWidget(self.label)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape or event.key() == Qt.Key_Q:
            self.close()
            self.fullscreen_closed.emit()
