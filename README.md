# Lateral Sitting Posture Detection using YOLOv5

<div align="center">
  <img src="https://raw.githubusercontent.com/itakurah/SittingPostureDetection/main/data/images/posture.webp" width="80%" height="80%" alt="Sitting Posture"> 

  *Source: https://www.youtube.com/watch?v=HNgTLml_Zi4*
</div>



This GitHub repository contains a posture detection program that utilizes [YOLOv5](https://github.com/ultralytics/yolov5), an advanced object detection algorithm, to detect and predict lateral sitting postures. The program is designed to analyze the user's sitting posture in real-time and provide feedback on whether the posture is good or bad based on predefined criteria. The goal of this project is to promote healthy sitting habits and prevent potential health issues associated with poor posture.

Key Features:

* YOLOv5: The program leverages the power of YOLOv5, which is an object detection algorithm, to
  accurately detect the user's sitting posture from a webcam.
* Real-time Posture Detection: The program provides real-time feedback on the user's sitting posture, making it suitable
  for use in applications such as office ergonomics, fitness, and health monitoring.
* Good vs. Bad Posture Classification: The program uses a pre-trained model to classify the detected posture as good or
  bad, enabling users to improve their posture and prevent potential health issues associated with poor sitting habits.
* Open-source: The program is released under an open-source license, allowing users to access the source code, modify
  it, and contribute to the project.

### Built With

![Python]

# Getting Started

### Prerequisites

* Python 3.9.x

### Installation  
If you have an NVIDIA graphics processor, you can activate GPU acceleration by installing the GPU requirements. Note that without GPU acceleration, the inference will run on the CPU, which can be very slow.  
#### Windows  
  
1. `git clone https://github.com/itakurah/SittingPostureDetection.git`  
2. `python -m venv venv`  
3. `.\venv\scripts\activate.bat`  
##### Default/NVIDIA GPU support:  
4.  `pip install -r ./requirements_windows.txt` **OR** `pip install -r ./requirements_windows_gpu.txt`

#### Linux  
  
1. `git clone https://github.com/itakurah/SittingPostureDetection.git`  
2. `python3 -m venv venv`  
3. `source venv/bin/activate`
##### Default/NVIDIA GPU support:  
4. `pip3 install -r requirements_linux.txt` **OR** `pip3 install -r requirements_linux_gpu.txt`


### Run the program

`python application.py <optional: model_file.pt>` **OR** `python3 application.py <optional: model_file.pt>`

The default model is loaded if no model file is specified.

# Model
The program uses a custom trained [YOLOv5s](https://github.com/ultralytics/yolov5/blob/79af1144c270ac7169553d450b9170f9c60f92e4/models/yolov5s.yaml) model that is trained on about 160 images per class for 146 epochs. The model has two classes: sitting_good and sitting_bad to give feedback about the current sitting posture.
## Architecture
The architecture that is used for the model is the standard YOLOv5s architecture:

<img src="https://raw.githubusercontent.com/itakurah/SittingPostureDetection/main/data/images/architecture.png" width=75% height=75%>



*Fig. 1: YOLOv5s network architecture (based on Liu et al.). The CBS module consists of a Convolutional layer, a Batch Normalization layer, and a Sigmoid Linear Unit (SiLU) activation function. The C3 module consists of three CBS modules and one bottleneck block. The SPPF module consists of two CBS modules and three Max Pooling layers.*

## Model Results
The validation set contains 80 images (40 sitting_good, 40 sitting_bad). The results are as follows:
|Class|Images|Instances|Precision|Recall|mAP50|mAP50-95|
|--|--|--|--|--|--|--|
|all| 80 | 80 | 0.87 | 0.939 | 0.931 | 0.734 |
|sitting_good| 40 |  40| 0.884 | 0.954 | 0.908 |0.744  |
|sitting_bad| 80 | 40 | 0.855 | 0.925 | 0.953 | 0.724 |

F1, Precision, Recall, and Precision-Recall plots:

<p align="middle">
<img src="https://raw.githubusercontent.com/itakurah/SittingPostureDetection/main/data/images/F1_curve.png" width=40% height=40%>
<img src="https://raw.githubusercontent.com/itakurah/SittingPostureDetection/main/data/images/P_curve.png" width=40% height=40%>
<img src="https://raw.githubusercontent.com/itakurah/SittingPostureDetection/main/data/images/R_curve.png" width=40% height=40%>
<img src="https://raw.githubusercontent.com/itakurah/SittingPostureDetection/main/data/images/PR_curve.png" width=40% height=40%>
</p>

# About

This project was developed by [Niklas Hoefflin](https://github.com/itakurah), [Tim Spulak](https://github.com/T-Lak),
Pascal Gerber & Jan Bösch and supervised by [André Jeworutzki](https://github.com/AndreJeworutzki)
and Jan Schwarzer as part of the [Train Like A Machine](https://csti.haw-hamburg.de/project/TLAM/) module.

# Sources

 - Jocher, G. (2020). YOLOv5 by Ultralytics (Version 7.0). https://doi.org/10.5281/zenodo.3908559
 - Fig. 1: H. Liu, F. Sun, J. Gu, and L. Deng, “Sf-yolov5: A lightweight small
object detection algorithm based on improved feature fusion mode,”
Sensors (Basel, Switzerland), vol. 22, no. 15, pp. 1–14, 2022. https://doi.org/10.3390/s22155817

# License

This project is licensed under the MIT License. See the LICENSE file for details.

<!-- MARKDOWN LINKS & IMAGES -->

[Python]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
