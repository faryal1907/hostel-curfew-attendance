import face_recognition
import numpy as np
import base64
import cv2
import json
from backend.utils.benchmarking import benchmark_timer


def base64_to_image(base64_str):
    img_data = base64.b64decode(base64_str.split(",")[1])
    np_arr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)


@benchmark_timer
def get_embedding(image):
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb)

    if len(encodings) == 0:
        return None

    return encodings[0]


@benchmark_timer
def compare_faces(known_embeddings, new_embedding):
    distances = face_recognition.face_distance(known_embeddings, new_embedding)
    min_dist = np.min(distances)
    return min_dist, np.argmin(distances)