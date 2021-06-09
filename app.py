import os
import sys
import base64
from io import BytesIO

import re
import cv2
import datetime
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
from flask_apscheduler import APScheduler
import json

sys.path.insert(0, '..')
from modules import plant_id, plant_cmp, plant_crawler
from utils import base64_to_pil, timestamp, time_stamp, json_load, json_write

plant_info = json_load('model.json')
plant_identifier = plant_id.PlantIdentifier()

def getPlantInfo(name):
    '''
    @name: 植物中名
    @return: 植物信息:d-介绍|w-水依赖|t-温度依赖|l-光照依赖
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

@scheduler.task('cron', id='1', day='*', hour='08', minute='00', second='00')
def grabWeather():
    '''
    每日08：00定时获取当天天气
    '''
    res = plant_crawler.weather()
    weather = json_load('weather.json')
    
    if len(weather['history']) >= 7:
        del(weather['history'][0])

    weather['history'].append(res)
    json_write(weather, 'weather.json')

def waterAdvice(name, rest):
    '''
    @name: 植物种类
    @rest: 当前剩余天数
    '''
    info = plant_info['data'][name]
    return rest if rest > 0 else 0

def getKindName(chinese_name):
    '''
    @chinese_name 包含科名、属名、种名
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
raw_image_dir = os.path.join(root_dir, 'static/raw_images')
tmp_image_dir = os.path.join(root_dir, 'static/images')
os.makedirs(raw_image_dir, exist_ok=True)
os.makedirs(tmp_image_dir, exist_ok=True)

def searchFileStartsWith(keyword, root):
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
        
        new_image_filename = '{}{}'.format(time_stamp(), os.path.splitext(image_filename)[-1])
        raw_image_filename = os.path.join(raw_image_dir, new_image_filename)  
        f.save(raw_image_filename)
 
        img = cv2.imread(raw_image_filename)
        img = plant_id.resize_image_short(img, 512)
        cv2.imwrite(os.path.join(tmp_image_dir, new_image_filename), img)
        
        probs, class_names = plant_identifier.predict(raw_image_filename)
        chinese_names = [item['chinese_name'] for item in class_names]
        latin_names = [item['latin_name'] for item in class_names]
        probs = ['{:.5f}'.format(prob) for prob in probs]
        labels = ['Chinese Name', 'Latin Name', 'description', 'Confidence']
        desc = [getPlantInfo(getKindName(name))['d'] for name in chinese_names]
        records = zip(chinese_names, latin_names, desc, probs)

        return render_template('id_upload_ok.html', 
                               labels=labels,
                               records=records,
                               image_filename=new_image_filename, 
                               timestamp=timestamp())
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

            new_image_filename = '{}{}'.format(time_stamp(), os.path.splitext(image_filename)[-1])
            raw_image_filename = os.path.join(raw_image_dir, new_image_filename)
            file.save(raw_image_filename)
            image = cv2.imread(raw_image_filename, 0)
            images.append(image)
            os.remove(raw_image_filename)

        res = plant_cmp.calculateSimilarity(images[0], images[1])
                
        return render_template('cmp_upload_ok.html',  similarity=res, result='相同' if res > 1 else '不相同')
    
    return render_template('cmp_upload.html')

@app.route('/ui/detect', methods=['GET', 'POST'])
def detectExceptionUI():
    if request.method == 'POST':
        return 'Non-support'
    return 'Non-support'

@app.route('/id', methods=['POST'])
def plantIdentify():
    print('here')
    if request.content_type.startswith('application/json'):
        data = request.get_json()
        image = base64_to_pil(data['image'])
        raw_image_filename = os.path.join(raw_image_dir, '{}.jpg'.format(time_stamp()))  
        image.save(raw_image_filename)

        probs, class_names = plant_identifier.predict(raw_image_filename, topk=1)
        name = class_names[0]['chinese_name']
        kind_name = getKindName(name)

        cache = searchFileStartsWith(kind_name, tmp_image_dir)
        if cache == None:
            refer = plant_crawler.CrabPlantImage(kind_name, tmp_image_dir)
            if not refer:
                refer = plant_crawler.CrabPlantImage(kind_name, tmp_image_dir, method='PBCC')
        else:
            refer = '{}/{}'.format(tmp_image_dir, cache)

        with open(refer, 'rb') as f:
            res = base64.b64encode(f.read())

        return jsonify(sec_name=name.split('_')[0], 
                        gen_name=name.split('_')[1], 
                        kind_name=kind_name,
                        intro=getPlantInfo(kind_name)['d'], 
                        advice=waterAdvice(name, 7), 
                        image=str(res, 'utf-8'))
    return 'Non-support'

@app.route('/compare', methods=['POST'])
def compare2plant():
    print('here')
    if request.content_type.startswith('application/json'):
        data = request.get_json()
        files = [data['src'], data['dst']]
        images = []

        for file in files:
            image = base64_to_pil(file)
            raw_image_filename = os.path.join(raw_image_dir, '{}.jpg'.format(time_stamp())) 
            image.save(raw_image_filename)
            images.append(cv2.imread(raw_image_filename, 0))
            os.remove(raw_image_filename)

        res = plant_cmp.calculateSimilarity(images[0], images[1])
        return jsonify(similarity=res)

    return 'Non-support'

@app.route('/detect', methods=['POST'])
def detectException():
    print('here')
    if request.content_type.startswith('application/json'):
        data = request.get_json()
        image = base64_to_pil(data['image'])
        raw_image_filename = os.path.join(raw_image_dir, '{}.jpg'.format(time_stamp()))  
        image.save(raw_image_filename)

        probs, class_names = plant_identifier.predict(raw_image_filename, topk=1)
        os.remove(raw_image_filename)
        return jsonify(problems='无异常')
    return 'Non-support'

if __name__ == '__main__':
    app.run(debug=True)
