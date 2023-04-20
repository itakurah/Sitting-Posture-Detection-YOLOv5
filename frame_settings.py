import cv2


def load(self):
    # settings bounding box drawing
    self.box_color = (251, 255, 12)
    self.box_thickness = 2

    # settings text drawing
    self.text_color_conf = (251, 255, 12)
    self.text_color_class = (251, 255, 12)
    self.text_color_bg = (0, 0, 0)
    self.text_thickness = 1
    self.text_font = cv2.FONT_HERSHEY_SIMPLEX
    self.text_font_scale = 0.5