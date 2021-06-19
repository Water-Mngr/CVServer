'''
Copyrights: ©2021 @Laffery
Date: 2021-06-09 08:28:03
LastEditor: Laffery
LastEditTime: 2021-06-19 15:47:19
'''
import time
import json
import datetime
from io import BytesIO
from PIL import Image
import base64

def time_stamp():
    '''
    @return: 当前时间戳
    '''
    return int(round(time.time() * 1000))

def time_margin(year, month, day):
    '''
    @return 指定日期距今的天数
    '''
    today = time.localtime()
    margin = datetime.date(today.tm_year, today.tm_mon, today.tm_mday) - datetime.date(year, month, day)
    return margin.days

def time_format():
    '''
    @return 当前日期的格式化输出，格式为'yy-mm-dd'
    '''
    today = time.localtime()
    return f'{today.tm_year}-{today.tm_mon}-{today.tm_mday}'

def json_load(filename):
    '''
    @return: json object loaded from file
    '''
    with open(filename, 'r') as fd:
        res = json.load(fd)

    return res

def json_write(obj, filename):
    '''
    write json object to file
    '''
    try:
        with open(filename, 'w') as fd:
            fd.write(json.dumps(obj))
    except Exception as e:
        return False
    return True
        
def base64_to_pil(image_data):
    '''
    Convert base64 image data to PIL image
    '''
    pil_image = Image.open(BytesIO(base64.b64decode(image_data)))
    return pil_image