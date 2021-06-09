'''
Copyrights: ©2021 @Laffery
Date: 2021-06-09 08:28:03
LastEditor: Laffery
LastEditTime: 2021-06-09 09:06:48
'''
import time
import json
from PIL import Image

def timestamp():
    return time.time()

def time_stamp():
    '''
    @return: 当前时间戳
    '''
    return int(round(time.time() * 1000))

def json_load(filename):
    '''
    @return: json object loaded from file
    '''
    with open(filename, 'r') as fd:
        res = json.load(fd)

    return res

def json_write(object, filename):
    '''
    write json object to file
    '''
    try:
        with open(filename, 'w') as fd:
            json.write(json.dumps(object))
    except Exception as e:
        return False
    return True
        
def base64_to_pil(image_data):
    '''
    Convert base64 image data to PIL image
    '''
    pil_image = Image.open(BytesIO(base64.b64decode(image_data)))
    return pil_image