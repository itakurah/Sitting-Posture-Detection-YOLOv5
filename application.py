import os
import sys
import tempfile

from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet

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
    window = App()
    with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
        # Write the XML string to the temporary file
        tmp.write(style.encode('utf-8'))
        # Close the temporary file
        tmp.close()
        apply_stylesheet(app, theme=tmp.name, css_file='app_views/custom.css')
    os.unlink(tmp.name)
    window.view.show()
    sys.exit(app.exec())
