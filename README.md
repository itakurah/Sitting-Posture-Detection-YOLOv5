# Real-Time Lateral Sitting Posture Detection using YOLOv5

<div align="center">
  <img src="https://raw.githubusercontent.com/itakurah/SittingPostureDetection/main/data/images/posture.webp" width="80%" height="80%" alt="Sitting Posture"> 

  *Source: https://www.youtube.com/watch?v=HNgTLml_Zi4*
</div>



This repository provides an open-source solution for **real-time sitting posture detection** using [YOLOv5](https://github.com/ultralytics/yolov5), a state-of-the-art object detection algorithm. The program is designed to analyze a user’s sitting posture and offer feedback on whether it aligns with ergonomic best practices, aiming to promote healthier sitting habits.

## Key Features

* **YOLOv5**: The program leverages the power of YOLOv5, which is an object detection algorithm, to accurately detect the user’s sitting posture from a webcam.
* **Real-time Posture Detection**: The program provides real-time feedback on the user's sitting posture, making it suitable for applications in office ergonomics, fitness, and health monitoring.
* **Good vs. Bad Posture Classification**: The program uses a pre-trained model to classify the detected posture as good or bad, enabling users to improve their posture and prevent potential health issues associated with poor sitting habits.
* **Open-source**: Released under an open-source license, allowing users to access, modify, and contribute to the project.


---

### Built With

![Python]

## IEEE Conference Publication

We are pleased to announce that this project has been published in an IEEE conference paper, which provides a comprehensive overview of our methodology, technical approach, and results in applying YOLOv5 for lateral sitting posture detection. This paper, titled **"Lateral Sitting Posture Detection using YOLOv5,"** was presented at the 2024 IEEE International Conference on Biomedical Robotics and Biomechatronics (BioRob). For more in-depth information, please refer to the full paper available at:

**[Read the IEEE Publication on Xplore](https://doi.org/10.1109/BioRob60516.2024.10719953)**

# Getting Started

### Prerequisites

* Python 3.9.X

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

# Model Information
This project uses a custom-trained [YOLOv5s](https://github.com/ultralytics/yolov5/blob/79af1144c270ac7169553d450b9170f9c60f92e4/models/yolov5s.yaml) model fine-tuned on 160 images per class over 146 epochs. It categorizes postures into two classes:
* `sitting_good`
* `sitting_bad`

The trained model file is located under the following directory:
`data/inference_models/small640.pt`
# Architecture
The architecture that is used for the model is the standard YOLOv5s architecture:

<img src="https://raw.githubusercontent.com/itakurah/SittingPostureDetection/main/data/images/architecture.png" width=75% height=75%>



*Fig. 1: YOLOv5s network architecture (based on Liu et al.). The CBS module consists of a Convolutional layer, a Batch Normalization layer, and a Sigmoid Linear Unit (SiLU) activation function. The C3 module consists of three CBS modules and one bottleneck block. The SPPF module consists of two CBS modules and three Max Pooling layers.*

# Model Results
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
Pascal Gerber & Jan Bösch. It was supervised by [André Jeworutzki](https://github.com/AndreJeworutzki) and Jan Schwarzer as part of the [Train Like A Machine](https://csti.haw-hamburg.de/project/TLAM/) module at Hamburg University of Applied Sciences (HAW Hamburg).
The project is actively maintained by Niklas Hoefflin and Tim Spulak.

# Sources

 - Jocher, G. (2020). YOLOv5 by Ultralytics (Version 7.0). https://doi.org/10.5281/zenodo.3908559
 - Fig. 1: H. Liu, F. Sun, J. Gu, and L. Deng, “Sf-yolov5: A lightweight small
object detection algorithm based on improved feature fusion mode,”
Sensors (Basel, Switzerland), vol. 22, no. 15, pp. 1–14, 2022. https://doi.org/10.3390/s22155817

# License

This project is licensed under the MIT License. See the LICENSE file for details.

<!-- MARKDOWN LINKS & IMAGES -->

[Python]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
