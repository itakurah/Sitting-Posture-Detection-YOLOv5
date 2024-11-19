from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QScrollArea, QGroupBox, QDialog


class AboutWindow(QDialog):
    def __init__(self, view, model):
        super().__init__()
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setEnabled(True)
        self.resize(420, 506)
        self.setFixedSize(420, 506)
        self.parent = view
        self.center_relative_to_parent()
        self.setWindowIcon(QtGui.QIcon('data/images/logo.png'))
        self.setWindowTitle("About")
        self.setWindowOpacity(1.000000000000000)
        self.setInputMethodHints(Qt.ImhNone)
        self.app_icon_label = QLabel(self)
        self.app_icon_label.move(20, 20)
        self.app_icon_label.setFixedHeight(64)
        self.app_icon_label.setFixedWidth(64)
        app_icon_pixmap = QPixmap('data/images/logo.png')
        self.app_icon_label.setPixmap(
            app_icon_pixmap.scaled(self.app_icon_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.SmoothTransformation))
        self.label = QLabel(self)
        self.label.setGeometry(QRect(100, 20, 150, 16))
        self.label_2 = QLabel(self)
        self.label_2.setGeometry(QRect(100, 170, 301, 16))
        self.label_2.setOpenExternalLinks(True)
        self.label_3 = QLabel(self)
        self.label_3.setGeometry(QRect(100, 93, 90, 71))
        self.label_4 = QLabel(self)
        self.label_4.setGeometry(QRect(20, 100, 47, 13))
        self.label_5 = QLabel(self)
        self.label_5.setGeometry(QRect(100, 40, 57, 13))
        self.label_6 = QLabel(self)
        self.label_6.setGeometry(QRect(20, 170, 41, 13))
        self.groupBox = QGroupBox(self)
        self.groupBox.setGeometry(QRect(20, 270, 380, 221))
        self.groupBox.setAlignment(Qt.AlignCenter)
        self.groupBox.setCheckable(False)
        self.groupBox.setStyleSheet("QGroupBox{background-color: transparent;};QGroupBox::title {"
                                    "subcontrol-origin: margin;"
                                    "subcontrol-position: top center;}")
        self.groupBox.setTitle('MIT License')
        self.scrollArea = QScrollArea(self.groupBox)
        self.scrollArea.setEnabled(True)
        self.scrollArea.setGeometry(QRect(10, 20, 361, 191))
        self.scrollArea.setInputMethodHints(Qt.ImhNone)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 322, 513))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)

        self.label_7 = QLabel(self.scrollAreaWidgetContents)
        self.label_7.setEnabled(True)
        self.label_7.setInputMethodHints(Qt.ImhNone)
        self.label_7.setTextFormat(Qt.AutoText)
        self.label_7.setScaledContents(False)
        self.label_7.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)
        self.label_7.setWordWrap(True)
        self.label_7.setTextInteractionFlags(Qt.NoTextInteraction)
        self.verticalLayout.addWidget(self.label_7)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.label_8 = QLabel(self)
        self.label_8.setGeometry(QRect(20, 200, 47, 13))
        self.label_9 = QLabel(self)
        self.label_9.setGeometry(QRect(100, 240, 151, 16))
        self.label_9.setTextFormat(Qt.MarkdownText)
        self.label_9.setOpenExternalLinks(True)
        self.label_11 = QLabel(self)
        self.label_11.setGeometry(QRect(255, 240, 126, 16))
        self.label_11.setTextFormat(Qt.MarkdownText)
        self.label_11.setOpenExternalLinks(True)
        self.label_12 = QLabel(self)
        self.label_12.setGeometry(QRect(255, 220, 126, 16))
        self.label_12.setTextFormat(Qt.MarkdownText)
        self.label_12.setOpenExternalLinks(True)
        self.label_13 = QLabel(self)
        self.label_13.setGeometry(QRect(100, 200, 166, 16))
        self.label_13.setTextFormat(Qt.MarkdownText)
        self.label_13.setOpenExternalLinks(True)
        self.label_14 = QLabel(self)
        self.label_14.setGeometry(QRect(100, 220, 151, 16))
        self.label_14.setTextFormat(Qt.MarkdownText)
        self.label_14.setOpenExternalLinks(True)
        self.label_15 = QLabel(self)
        self.label_15.setGeometry(QRect(150, 40, 60, 13))
        self.label_15.setStyleSheet('QLabel{color: purple;}')
        self.app_icon_label.setText("")
        self.label.setText("Sitting Posture Detector")
        self.label_3.setText("<html><head/><body>Niklas Hoefflin<br/>Tim Spulak<br/>Jan B\u00f6sch<br/>Pascal "
                             "Gerber</body></html>")
        self.label_3.setStyleSheet('QLabel{font-weight: normal}')
        self.label_4.setText("Authors:")
        self.label_4.setStyleSheet('QLabel{font-weight: normal;}')
        self.label_5.setText("Commit:")
        self.label_15.setText('{}'.format(model.commit_hash))
        self.label_6.setText("GitHub:")
        self.label_6.setStyleSheet('QLabel{font-weight: normal;}')
        self.label_2.setText("<html><head/><body><p><a href=\"https://github.com/itakurah/SittingPostureDetection"
                             "\"><span style=\" text-decoration: underline; "
                             "color:#4269b9;\">https://github.com/itakurah/SittingPostureDetection</span></a></p"
                             "></body></html>")
        self.label_2.setStyleSheet('QLabel{font-weight: normal;}')
        self.label_7.setStyleSheet('QLabel{font-weight: normal;}')
        self.label_7.setText(
            "<html><head/><body><p><span style=\" font-family:'Courier New';\">MIT License</span></p><p><span "
            "style=\" font-family:'Courier New';\">Copyright (c) 2023 Niklas Hoefflin</span></p><p><span style=\" "
            "font-family:'Courier New';\">Permission is hereby granted, free of charge, to any person obtaining a "
            "copy of this software and associated documentation files (the &quot;Software&quot;), to deal in the "
            "Software without restriction, including without limitation the rights to use, copy, modify, merge, "
            "publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the "
            "Software is furnished to do so, subject to the following conditions:</span></p><p><span style=\" "
            "font-family:'Courier New';\">The above copyright notice and this permission notice shall be included in "
            "all copies or substantial portions of the Software.</span></p><p><span style=\" font-family:'Courier "
            "New';\">THE SOFTWARE IS PROVIDED &quot;AS IS&quot;, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, "
            "INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND "
            "NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR "
            "OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN "
            "CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.</span></p></body></html>")
        self.label_8.setText("Icons:")
        self.label_8.setStyleSheet('QLabel{font-weight: normal;}')
        self.label_9.setText("<html><head/><body><p><a href=\"https://icons8.com/icon/37303/informationen\"><span "
                             "style=\" text-decoration: underline; color:#4269b9;\">Information</span></a> icon by <a "
                             "href=\"https://icons8.com\"><span style=\" text-decoration: underline; "
                             "color:#4269b9;\">Icons8</span></a></p></body></html>")
        self.label_9.setStyleSheet('QLabel{font-weight: normal;}')
        self.label_11.setText("<html><head/><body><p><a href=\"https://icons8.com/icon/37308/rotate\"><span style=\" "
                              "text-decoration: underline; color:#4269b9;\">Rotate</span></a> icon by <a "
                              "href=\"https://icons8.com\"><span style=\" text-decoration: underline; "
                              "color:#4269b9;\">Icons8</span></a></p></body></html>")
        self.label_11.setStyleSheet('QLabel{font-weight: normal;}')
        self.label_12.setText("<html><head/><body><p><a href=\"https://icons8.com/icon/8183/expand\"><span style=\" "
                              "text-decoration: underline; color:#4269b9;\">Expand</span></a> icon by <a "
                              "href=\"https://icons8.com\"><span style=\" text-decoration: underline; "
                              "color:#4269b9;\">Icons8</span></a></p></body></html>")
        self.label_12.setStyleSheet('QLabel{font-weight: normal;}')
        self.label_13.setText("<html><head/><body><p><a href=\"https://icons8.com/icon/8162/flip-horizontal\"><span "
                              "style=\" text-decoration: underline; color:#4269b9;\">Flip Horizontal</span></a> icon "
                              "by <a href=\"https://icons8.com\"><span style=\" text-decoration: underline; "
                              "color:#4269b9;\">Icons8</span></a></p></body></html>")
        self.label_13.setStyleSheet('QLabel{font-weight: normal;}')
        self.label_14.setText("<html><head/><body><p><a href=\"https://icons8.com/icon/8171/flip-vertical\"><span "
                              "style=\" text-decoration: underline; color:#4269b9;\">Flip Vertical</span></a> icon by "
                              "<a href=\"https://icons8.com\"><span style=\" text-decoration: underline; "
                              "color:#4269b9;\">Icons8</span></a></p></body></html>")
        self.label_14.setStyleSheet('QLabel{font-weight: normal;}')

    def showEvent(self, event):
        # Calculate the center position based on the parent window
        # self.move(self.parent_center.x() - self.width() // 2, self.parent_center.y() - self.height() // 2)
        self.center_relative_to_parent()
        super().showEvent(event)

    def center_relative_to_parent(self):
        parent_position = self.parent.pos()
        parent_size = self.parent.size()
        parent_center = QPoint(parent_position.x() + parent_size.width() // 2,
                               parent_position.y() + parent_size.height() // 2)

        child_size = self.size()
        child_position = QPoint(parent_center.x() - child_size.width() // 2,
                                parent_center.y() - child_size.height() // 2)

        self.move(child_position)
