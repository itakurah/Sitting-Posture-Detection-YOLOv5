
import sys

import qdarktheme
from PyQt5.QtWidgets import QApplication


from app_controllers.controller import Controller
from app_models.model import Model
from app_views.view import View

model_name = "small640.pt"


class App:
    def __init__(self):
        super().__init__()
        self.model = Model(model_name)
        self.view = View(self.model)
        self.controller = Controller(self.model, self.view)
        print("All modules loaded")


if __name__ == '__main__':
    if len(sys.argv) > 2:
        print("Error: Exactly one argument is expected")
        sys.exit(1)
    elif len(sys.argv) == 1:
        print("Info: Loading default inference model: {}".format(model_name))
    else:
        model_name = sys.argv[1]
    qdarktheme.enable_hi_dpi()
    app = QApplication([])
    qdarktheme.setup_theme('dark')
    window = App()
    window.view.show()
    sys.exit(app.exec())
