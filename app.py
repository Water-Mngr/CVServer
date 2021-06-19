import os
import sys
import base64

import re
import cv2
import time
import datetime
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
from flask_apscheduler import APScheduler
import json

from modules import plant_id, plant_cmp, plant_crawler, plant_detect
from utils import base64_to_pil, time_stamp, time_margin, json_load, json_write

plant_info = json_load('model.json')
plant_identifier = plant_id.PlantIdentifier()

def getPlantInfo(name):
    '''
    @name: 植物种名 \\
    @return: 植物信息: d-介绍|w-水依赖|t-温度依赖|l-光照依赖
    '''
    data = plant_info['data']
    return data[name] if data[name] else { 'd': 'unknown', 'w': 0, 't': 0, 'l': 0}

class Config(object):
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.send_file_max_age_default = datetime.timedelta(seconds=1)
app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# @scheduler.task('interval', id='do_job_1', seconds=3, misfire_grace_time=900)
@scheduler.task('cron', id='1', day='*', hour='08', minute='00', second='00')
def grabWeather():
    '''
    每日08：00定时获取当天天气
    '''
    date = time.localtime()
    today = plant_crawler.weather()
    weather = json_load('weather.json')

    weather['history']['{}-{}-{}'.format(date.tm_year, date.tm_mon, date.tm_mday)] = {
        'high': int(re.findall(r'\d+', today['high'])[0]),
        'type': today['type']
    }

    json_write(weather, 'weather.json')

def parseYYmmDD(yymmdd):
    '''
    @yymmdd: 日期，格式为`yy-mm-dd` \\
    @return: 年月日(int)
    '''
    _tuple = re.findall(r'\d+')
    return int(_tuple[0]), int(_tuple[1]), int(_tuple[2])

def waterAdvice(name, lastdate='2021-06-18'):
    '''
    @name: 植物种类 \\
    @lastdate: 上一次浇水的日期，格式为`yy-mm-dd` \\
    @return: 剩余浇水日期，等于0则说明今天需要浇水
    '''
    year, month, day = parseYYmmDD(lastdate)
    margin = time_margin(year, month, day) # 距离上次浇水天数
    weather = json_load('weather.json')
    info = getPlantInfo(name)['w'] + 1

    refer = [7, 4, 2] # 推荐剩余浇水天数
    rest = refer[info]

    def handleHighTemperature(high):
        if high:
            r = [0, 1, 2] # 遇到高温要缩减的天数
            rest -= r[info]

    def handleWeather(weather):
        if weather == '大雨':
            r = [5, 3, 2] # 遇到大雨需要延长的天数
        elif weather == '中雨':
            r = [4, 2, 1] # 遇到中雨需要延长的天数
        else:
            r = [3, 1, 0] # 其它天气需要延长的天数
        rest += r[info]

    for i in range(margin):
        date = datetime.datetime(year, month, day) + datetime.timedelta(days=i)
        w = weather['history']['{}-{}-{}'.format(date.year, date.month, date.day)]

        handleHighTemperature(w['high'] > 30)
        handleWeather(w['type'])

    rest -= margin
    return rest if rest > 0 else 0

def getKindName(chinese_name):
    '''
    @chinese_name 包含科名、属名、种名 \\
    @return 植物种名
    '''
    kind_name = chinese_name.split('_')[-1]
    patterns = re.findall(r'[(](.*?)[)]', kind_name) # 如果有括号
    return patterns[0] if len(patterns) else kind_name

def allowed_file_type(filename):
    '''
    @return 允许的扩展名
    '''
    ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp']
    extension = os.path.splitext(os.path.basename(filename))[1]
    return extension.lower() in ALLOWED_EXTENSIONS

un_allowed_file_type_msg = 'Please check image file format, only support png, jpg, jpeg, bmp'

root_dir = os.path.dirname(__file__)
image_dir = os.path.join(root_dir, 'static/images')
os.makedirs(image_dir, exist_ok=True)

def searchFileStartsWith(keyword, root):
    '''
    search file which starts with `keyword` in dir root 
    '''
    dirs = os.listdir(root)
    for file in dirs:
        if file.startswith(keyword):
            return file

    return None

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/ui/id', methods=['POST', 'GET'])
def plantIdentifyUI():
    if request.method == 'POST':
        f = request.files['image']
        image_filename = os.path.basename(f.filename)

        if not (f and allowed_file_type(image_filename)):
            return jsonify({'error': 1001, 'message': un_allowed_file_type_msg})
        
        new_filename = '{}{}'.format(time_stamp(), os.path.splitext(image_filename)[-1])
        image_filename = os.path.join(image_dir, new_filename)  
        f.save(image_filename)

        _, probs, class_names = plant_identifier.predict(cv2.imread(image_filename))
        chinese_names = [item['chinese_name'] for item in class_names]
        probs = ['{:.5f}'.format(prob) for prob in probs]
        desc = [getPlantInfo(getKindName(name))['d'] for name in chinese_names]
        records = zip(chinese_names, desc, probs)

        return render_template(
                                'id_upload_ok.html', 
                                labels=['Chinese Name', 'Description', 'Confidence'],
                                records=records,
                                image_filename=new_filename, 
                                timestamp=time.time()
                            )
    return render_template('id_upload.html')

@app.route('/ui/compare', methods=['GET', 'POST'])
def compare2plantUI():
    if request.method == 'POST':
        f1 = request.files['image1']
        f2 = request.files['image2']
        files = [f1, f2]
        images = []

        for file in files:
            image_filename = os.path.basename(file.filename)
            if not (file and allowed_file_type(image_filename)):
                return jsonify({'error': 1001, 'message': un_allowed_file_type_msg})

            new_filename = '{}{}'.format(time_stamp(), os.path.splitext(image_filename)[-1])
            image_filename = os.path.join(image_dir, new_filename)
            file.save(image_filename)
            images.append(cv2.imread(image_filename))
            os.remove(image_filename)

        ind0, _, _ = plant_identifier.predict(images[0])
        ind1, _, _ = plant_identifier.predict(images[1])
        res = plant_cmp.compare(images[0], images[1], ind0, ind1)
                
        return render_template('cmp_upload_ok.html',  similarity=res, result='相同' if res >= 1 else '不相同')
    
    return render_template('cmp_upload.html')

@app.route('/ui/detect', methods=['GET', 'POST'])
def detectExceptionUI():
    if request.method == 'POST':
        f = request.files['image']
        image_filename = os.path.basename(f.filename)

        if not (f and allowed_file_type(image_filename)):
            return jsonify({'error': 1001, 'message': un_allowed_file_type_msg})
        
        new_filename = '{}{}'.format(time_stamp(), os.path.splitext(image_filename)[-1])
        image_filename = os.path.join(image_dir, new_filename)  
        f.save(image_filename)

        res = plant_detect.detect(image_filename)
                
        return render_template(
                                'detect_upload_ok.html', 
                                image_filename=new_filename, 
                                timestamp=time.time(), 
                                result=res
                            )
    
    return render_template('detect_upload.html')

@app.route('/id', methods=['POST'])
def plantIdentify():
    if request.content_type.startswith('application/json'):
        data = request.get_json()
        image = base64_to_pil(data['image'])
        image_filename = os.path.join(image_dir, '{}.jpg'.format(time_stamp()))  
        image.save(image_filename)

        _, probs, class_names = plant_identifier.predict(image_filename, topk=1)
        name = getKindName(class_names[0]['chinese_name'])

        return jsonify(
                        name=name,
                        intro=getPlantInfo(name)['d'], 
                        advice=waterAdvice(name), 
                        image=plant_crawler.CrabPlantImageUrl(name)
                    )
    return 'Non-support'

@app.route('/compare', methods=['POST'])
def compare2plant():
    if request.content_type.startswith('application/json'):
        data = request.get_json()
        files = [data['src'], data['dst']]
        images = []

        for file in files:
            image = base64_to_pil(file)
            image_filename = os.path.join(image_dir, '{}.jpg'.format(time_stamp())) 
            image.save(image_filename)
            images.append(cv2.imread(image_filename))
            os.remove(image_filename)

        ind0, _, _ = plant_identifier.predict(images[0])
        ind1, _, _ = plant_identifier.predict(images[1])
        res = plant_cmp.compare(images[0], images[1], ind0, ind1)
        return jsonify(match=res)

    return 'Non-support'

@app.route('/detect', methods=['POST'])
def detectException():
    if request.content_type.startswith('application/json'):
        data = request.get_json()
        image = base64_to_pil(data['image'])
        image_filename = os.path.join(image_dir, '{}.jpg'.format(time_stamp()))  
        image.save(image_filename)
        res = plant_detect.detect(image_filename)
        os.remove(image_filename)
        return res
    return 'Non-support'

if __name__ == '__main__':
    app.run(debug=True)
