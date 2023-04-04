from pathlib import Path
import yolov5

import torch


class Model:
    def __init__(self):
        # path to model
        self.model_path = Path("./model/modelv5.pt")#modelv5.pt")
        print(torch.cuda.is_available())
        #print(torch.cuda.get_device_properties(0).name)
        print(torch.cuda.device_count())
        cuda = torch.device('cuda:0')
        # load model into memory
        self.model = yolov5.load(str(self.model_path),device=cuda)#'cpu'
        # settings for model
        self.model.conf = 0.50  # NMS confidence threshold
        self.model.iou = 0.45  # NMS IoU threshold
        self.model.agnostic = False  # NMS class-agnostic
        self.model.multi_label = False  # NMS multiple labels per box
        self.model.max_det = 1  # maximum number of detections per image

    # return prediction
    def predict(self, image):
        return self.model(image)
