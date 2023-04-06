from PyQt5 import QtCore


class WorkerThreadMemory(QtCore.QThread):
    update_memory = QtCore.pyqtSignal()

    def __init__(self):
        # Use super() to call __init__() methods in the parent classes
        super(WorkerThreadMemory, self).__init__()
        # The boolean variable to break the while loop in self.run() method
        self.running = True

    def run(self):
        while self.running:
            self.update_memory.emit()
            self.msleep(500)

    def stop(self):
        # terminate the while loop in self.run() method
        self.running = False
