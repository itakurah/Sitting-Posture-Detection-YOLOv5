import sys
from pathlib import Path

import torch
import yolov5

'''Class for loading the Yolo-v5 inference_models
'''


class InferenceModel:
    def __init__(self, model_name):
        self.model_name = model_name
        # path to inference_models
        self.model_path = Path('./data/inference_models/{}'.format(model_name))
        print(self.model_name + ' loaded')
        print('cuda available: ' + str(torch.cuda.is_available()))
        if torch.cuda.is_available():
            print('running GPU inference..')
            device_memory = {}
            # get gpu with the highest memory
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                device_memory[i] = props.total_memory
            device_idx = max(device_memory, key=device_memory.get)
            cuda = torch.device('cuda:{}'.format(device_idx))
            # load inference_models into memory
            try:
                self.model = yolov5.load(str(self.model_path), device=str(cuda))
            except Exception as e:
                print(e)
                print('Could not load model')
                sys.exit(-1)
        else:
            print('running CPU inference..')
            try:
                self.model = yolov5.load(str(self.model_path), device='cpu')
            except Exception as e:
                print(e)
                print('Could not load model')
                sys.exit(-1)
        # inference_models properties
        self.model.conf = 0.50  # NMS confidence threshold
        self.model.iou = 0.50  # NMS IoU threshold
        self.model.classes = [0, 1]  # Only show these classes
        self.model.agnostic = False  # NMS class-agnostic
        self.model.multi_label = False  # NMS multiple labels per box
        self.model.max_det = 1  # maximum number of detections per image
        self.model.amp = True  # Automatic Mixed Precision (AMP) inference

    # return prediction
    def predict(self, image):
        return self.model(image)

    # extract items from results
    @staticmethod
    def get_results(results):
        (bbox_x1, bbox_y1, bbox_x2, bbox_y2, class_name, confidence) = None, None, None, None, None, None
        results = results.pandas().xyxy[0].to_dict(orient="records")
        if results:
            for result in results:
                confidence = result['confidence']
                class_name = result['class']
                bbox_x1 = int(result['xmin'])
                bbox_y1 = int(result['ymin'])
                bbox_x2 = int(result['xmax'])
                bbox_y2 = int(result['ymax'])
        return bbox_x1, bbox_y1, bbox_x2, bbox_y2, class_name, confidence
