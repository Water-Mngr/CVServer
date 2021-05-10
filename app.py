import os
import sys
import time
import base64
from io import BytesIO

import cv2
from datetime import timedelta
from PIL import Image
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

sys.path.insert(0, '..')
from modules import plant_id, plant_cmp


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.send_file_max_age_default = timedelta(seconds=1)

plant_identifier = plant_id.PlantIdentifier()

def time_stamp():
    '''@return: 当前时间戳
    '''
    return int(round(time.time() * 1000))

def allowed_file_type(filename):
    '''
    Define what file extentsion is allowed
    '''
    ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp']
    extension = os.path.splitext(os.path.basename(filename))[1]
    return extension.lower() in ALLOWED_EXTENSIONS

un_allowed_file_type_msg = 'Please check image file format, only support png, jpg, jpeg, bmp'

def base64_to_pil(image_data):
    '''
    Convert base64 image data to PIL image
    '''
    pil_image = Image.open(BytesIO(base64.b64decode(image_data)))
    return pil_image

base_dir = os.path.dirname(__file__)
 
raw_image_dir = os.path.join(base_dir, 'static/raw_images')
tmp_image_dir = os.path.join(base_dir, 'static/images')
os.makedirs(raw_image_dir, exist_ok=True)
os.makedirs(tmp_image_dir, exist_ok=True)

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
        labels = ['Chinese Name', 'Latin Name', 'Confidence']
        records = zip(chinese_names, latin_names, probs)

        return render_template('id_upload_ok.html', 
                               labels=labels, records=records, 
                               image_filename=new_image_filename, 
                               timestamp=time.time())
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
        return jsonify(class_names=class_names[0]['chinese_name'], intro='这种植物喜温寒，特别香', advice='3~5天')
    return 'Non-support'

@app.route('/id/list', methods=['POST'])
def plantIdentifyList():
    print('here')
    if request.content_type.startswith('application/json'):
        data = request.get_json()
        image = base64_to_pil(data['image'])
        raw_image_filename = os.path.join(raw_image_dir, '{}.jpg'.format(time_stamp()))  
        image.save(raw_image_filename)

        probs, class_names = plant_identifier.predict(raw_image_filename)
        os.remove(raw_image_filename)
        probs = ['{:.5f}'.format(prob) for prob in probs]
        class_names = [name['chinese_name'] for name in class_names]

        return jsonify(class_names=class_names, probs=probs)
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
