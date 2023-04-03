from pathlib import Path
import yolov5

import torch


class Model:
    def __init__(self):

        self.model_path = Path("./model/modelv5.pt")#modelv5.pt")
        #self.model_name = "modelv5.pt"
        #self.model = yolov5.load(str(self.model_path))
        #self.model = torch.hub.load('ultralytics/yolov5', 'custom', path='model/best.pt',force_reload=True)
        #self.model = torch.hub.load('./yolov5', 'custom', path=str( self.model_path),source='local')
        print(torch.cuda.is_available())
        #print(torch.cuda.get_device_properties(0).name)
        print(torch.cuda.device_count())
        cuda = torch.device('cuda:0')
        self.model = yolov5.load(str(self.model_path),device=cuda)#'cpu'
        #self.model = torch.hub.load('.', 'custom', 'modelv5.pt', source='local')

    def predict(self, image):
        return self.model(image)
