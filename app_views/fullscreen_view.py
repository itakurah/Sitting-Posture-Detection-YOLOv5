from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel, QMainWindow, QDesktopWidget


class FullscreenView(QMainWindow):
    fullscreen_closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.label = QLabel()
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry(desktop.primaryScreen())
        self.label.setFixedWidth(screen_rect.width())
        self.label.setFixedHeight(screen_rect.height())
        self.setGeometry(screen_rect)
        self.label.setStyleSheet('background-color: black;')
        self.label.setAlignment(Qt.AlignCenter)
        self.setWindowState(Qt.WindowFullScreen)

    def set_central_widget_content(self, pixmap):
        pixmap = pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
        if pixmap is not None:
            self.label.setPixmap(pixmap)
        self.setCentralWidget(self.label)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape or event.key() == Qt.Key_Q:
            self.fullscreen_closed.emit()
            self.close()
