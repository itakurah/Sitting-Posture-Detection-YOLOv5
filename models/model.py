import cv2

from util.helper.load_model import InferenceModel


class Model:
    def __init__(self, model_name):
        super().__init__()
        self.is_fullscreen = False
        self.fullscreen_window = None
        self.pixmap = None
        self.worker_thread_pause_screen = None
        self.worker_thread_memory = None
        self.label_stream_height = None
        self.label_stream_width = None
        self.slider_brightness = None
        self.text_color_class = None
        self.text_color_conf = None
        self.text_color_bg = None
        self.cbox_enable_conf = None
        self.cbox_enable_class = None
        self.cbox_enable_info_background = None
        self.button_group = None
        self.button_group = None
        self.text_thickness = None
        self.text_thickness = None
        self.text_font = None
        self.text_font = None
        self.box_color = None
        self.slider_contrast = None
        self.text_font_scale = None
        self.timer_stop = None
        self.button_stop = None
        self.label_no_camera = None
        self.box_color: None
        self.box_thickness = None
        self.status_bar = None
        self.status_bar = None
        self.cbox_enable_bbox = None
        self.timer_start = None
        self.combobox_camera_list = None
        self.button_start = None
        self.label_stream = None
        self.label_cpu_usage = None
        self.label_dim = None
        self.label_conf = None
        self.label_class_info = None
        self.cbox_enable_debug = None
        self.label_fps = None
        self.label_memory_usage = None
        self.memory_usage = None
        self.cpu_usage = None
        self.confidence = None
        self.class_name = None
        self.width = None
        self.height = None
        self.fps = None
        with open('./commit_hash.txt', 'r') as file:
            self.commit_hash = file.read()
        # self.model = Model(get_model_name())
        self.prev_frame_time = 0
        self.IMAGE_BOX_SIZE = 600
        self.flag_is_camera_thread_running = True
        self.camera_mapping = {}
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
        self.inference_model = InferenceModel(model_name)

    def get_commit_hash(self):
        return self.commit_hash

