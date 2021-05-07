import os
import sys
import time

import cv2

sys.path.insert(0, '..')
import plantid


def get_all_filenames(dirname):
    all_filenames = []
    dirname = os.path.expanduser(dirname)
    for root, _, filenames in os.walk(dirname):
        all_filenames += [os.path.join(root, filename) for filename in filenames]
    return all_filenames


if __name__ == '__main__':
    src_dir = r'E:\\CV\\Proj\\hrc.jpg'
    filenames = get_all_filenames(src_dir)
    
    plant_identifier = plantid.PlantIdentifier()
    start_time = time.time()
    for k, name in enumerate(filenames):
        probs, class_names = plant_identifier.predict(name)
        print('[{}/{}] Time: {:.3}s  {}'.format(k+1, len(filenames), time.time() - start_time, name))
        start_time = time.time()
        print(class_names[0], probs[0])


