import numpy as np
from scipy.spatial import distance as dist
import cv2

# 定义面部特征点的索引
FACIAL_LANDMARKS_IDXS = {
    "mouth": (48, 68),
    "left_eye": (36, 42),
    "right_eye": (42, 48),
    "nose": (27, 36),
    "jaw": (0, 17),
    "left_eyebrow": (17, 22),
    "right_eyebrow": (22, 27)
}

def shape_to_np(shape):
    # 将dlib的shape对象转换为numpy数组
    coords = np.zeros((shape.num_parts, 2), dtype=np.int)
    for i in range(0, shape.num_parts):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

def calculate_ear(eye):
    # 计算眼睛的两组垂直关键点之间的欧氏距离
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    # 计算眼睛的一组水平关键点之间的欧氏距离
    C = dist.euclidean(eye[0], eye[3])
    # 计算眼睛纵横比
    ear = (A + B) / (2.0 * C)
    return ear

def calculate_mar(mouth):
    # 计算嘴巴的方面比
    A = np.linalg.norm(mouth[2] - mouth[9])
    B = np.linalg.norm(mouth[4] - mouth[7])
    C = np.linalg.norm(mouth[0] - mouth[6])
    mar = (A + B) / (2.0 * C)
    return mar

def process_frame(frame, detector, predictor, EYE_AR_THRESH, MAR_THRESH):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)
    for rect in rects:
        shape = predictor(gray, rect)
        shape = shape_to_np(shape)
        (lStart, lEnd) = FACIAL_LANDMARKS_IDXS["left_eye"]
        (rStart, rEnd) = FACIAL_LANDMARKS_IDXS["right_eye"]
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = calculate_ear(leftEye)
        rightEAR = calculate_ear(rightEye)
        ear = (leftEAR + rightEAR) / 2.0
        (mStart, mEnd) = FACIAL_LANDMARKS_IDXS["mouth"]
        mouth = shape[mStart:mEnd]
        mar = calculate_mar(mouth)
        is_mouth_open = mar > MAR_THRESH
        is_eye_closed = ear < EYE_AR_THRESH
        return bool(is_mouth_open), float(mar), float(ear)
    return False, 0.0, 0.0