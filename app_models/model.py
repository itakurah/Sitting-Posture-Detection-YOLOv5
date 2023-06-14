import cv2

from app_controllers.utils import camera_helper
from app_models.load_model import InferenceModel


class Model:
    def __init__(self, model_name):
        super().__init__()
        self.is_fullscreen = False
        self.fullscreen_window = None
        self.worker_thread_pause_screen = None
        self.worker_thread_memory = None
        self.memory_usage = None
        self.cpu_usage = None
        self.confidence = None
        self.class_name = None
        self.width = None
        self.height = None
        self.fps = None
        with open('./commit_hash.txt', 'r') as file:
            self.commit_hash = file.read()
        # self.inference_models = Model(get_model_name())
        self.prev_frame_time = 0
        self.IMAGE_BOX_SIZE = 600
        self.flag_is_camera_thread_running = True
        self.camera_mapping = camera_helper.get_camera_mapping(camera_helper.get_connected_camera_alias(),
                                                               camera_helper.get_connected_camera_ids())
        self.camera = None
        self.work_thread_camera = None

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
        self.model_name = model_name
        self.inference_model = InferenceModel(self.model_name)
        self.frame_rotation = 0
        self.frame_orientation_vertical = 0
        self.frame_orientation_horizontal = 0
        self.bbox_mode = 1

    def get_commit_hash(self):
        return self.commit_hash
