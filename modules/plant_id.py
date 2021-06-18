'''
Copyrights: ©2021 @Laffery
Date: 2021-04-29 08:23:38
LastEditor: Laffery
LastEditTime: 2021-06-18 21:49:33
'''
import os
import cv2
import numpy as np
from .utils import *

class PlantIdentifier(object):
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.net = cv2.dnn.readNetFromONNX(os.path.join(current_dir, 'models/model.oonx'))
        self.label_name_dict = get_label_name_dict(os.path.join(current_dir, 'models/label_map.txt'))

    def _preprocess(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = resize_image_short(image, 320)
        image = center_crop(image, 299, 299)
        image = image.astype(np.float32)
        image /= 255.0
        image -= np.asarray([0.485, 0.456, 0.406])
        image /= np.asarray([0.229, 0.224, 0.225])
        return image

    def predict(self, image, topk=5):
        try:
            image = normalize_image_shape(image)
        except:
            return None

        image = self._preprocess(image)
        blob = cv2.dnn.blobFromImage(image)
        self.net.setInput(blob)
        results = self.net.forward()
        probs = softmax(results)
        values, indices = find_topk(probs, kth=topk)
        probs = values[0]
        class_names = [self.label_name_dict[ind] for ind in indices[0]]
        return indices[0], probs, class_names
