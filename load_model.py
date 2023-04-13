from pathlib import Path

import torch
import yolov5


class Model:
    def __init__(self):
        # path to model
        self.model_path = Path("./model/modelv5.pt")  # modelv5.pt")
        if torch.cuda.is_available():
            cuda = torch.device('cuda:0')
            # load model into memory
            self.model = yolov5.load(str(self.model_path), device=cuda)
        else:
            self.model = yolov5.load(str(self.model_path), device='cpu')
        #print(torch.cuda.is_available())
        # print(torch.cuda.get_device_properties(0).name)
        #print(torch.cuda.device_count())
        # settings for model
        self.model.label_conf = 0.50  # NMS confidence threshold
        self.model.iou = 0.70  # NMS IoU threshold
        self.model.agnostic = False  # NMS class-agnostic
        self.model.multi_label = False  # NMS multiple labels per box
        self.model.max_det = 1  # maximum number of detections per image

    # return prediction
    def predict(self, image):
        return self.model(image)
