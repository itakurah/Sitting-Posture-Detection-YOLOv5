import cv2

'''Class for OpenCV properties
'''


def load(self):
    """
    Load the frame properties
    """
    # bounding box options
    # bbox color
    self.box_color = (251, 255, 12)
    # bbox line thickness
    self.box_thickness = 2

    # text options
    # confidence color
    self.text_color_conf = (251, 255, 12)
    # class color
    self.text_color_class = (251, 255, 12)
    # background color
    self.text_color_bg = (0, 0, 0)
    # font thickness
    self.text_thickness = 1
    # font style
    self.text_font = cv2.FONT_HERSHEY_SIMPLEX
    # font scale
    self.text_font_scale = 0.5
