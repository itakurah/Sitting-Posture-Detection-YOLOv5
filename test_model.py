import sys

from app_models.load_model import InferenceModel
import cv2
import glob

MODEL_NAME = 'model_l_best.pt'


def load_images_as_arrays(folder_path):
    image_arrays = []
    file_extensions = ('*.jpg', '*.jpeg', '*.png', '*.gif')
    for file_extension in file_extensions:
        file_pattern = folder_path + '/' + file_extension
        image_files = glob.glob(file_pattern)
        for image_file in image_files:
            image_array = cv2.imread(image_file)
            image_arrays.append(image_array)
    return image_arrays


# Specify the folder path where the images are located
folder_path = sys.argv[1]
predicting_class = sys.argv[2]

# Load images from the folder as NumPy arrays
image_arrays = load_images_as_arrays(folder_path)

print(len(image_arrays))
model = InferenceModel(MODEL_NAME)
count_class = 0
# Access the loaded image arrays
for image_array in image_arrays:
    # Process or manipulate the image arrays as needed
    # print(image_array.shape)  # Example: print the shape of the image array
    results = model.predict(image_array)
    (bbox_x1, bbox_y1, bbox_x2, bbox_y2, class_name, confidence) = InferenceModel.get_results(results)
    if int(predicting_class) == class_name:
        count_class += 1
    # print('{} {}'.format(confidence, class_name))
print('total number of correct predictions:')
print('{}/{}'.format(count_class, len(image_arrays)))
