'''
Copyrights: ©2021 @Laffery
Date: 2021-05-12 09:16:32
LastEditor: Laffery
LastEditTime: 2021-06-09 15:28:07
'''
# conding=utf-8
import requests
import os
import sys
import base64
import json
import re
import func_timeout

from time import sleep
from bs4 import BeautifulSoup

referer='http://ppbc.iplant.cn'
ua='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.56'

headers = {
    'User-Agent': ua,
    'Referer': referer
}

def CrabImage(url, path):
    
    #增加headers参数
    response = requests.get(url=url, headers=headers)
    response.encoding = 'utf-8'
    content = response.content
    with open(path, 'wb') as file:
        file.write(content)
    return path

def CrabPlantPageListID(name):
    url = 'http://ppbc.iplant.cn/list?keyword=' + name
    response = requests.get(url=url, headers=headers)
    response.encoding = 'utf-8'

    return response.url.split('/')[-1]

def CrabPlantSrcPPBC(name):
    cid = CrabPlantPageListID(name)
    url = 'http://ppbc.iplant.cn/ashx/getphotopage.ashx?t=0.2&n=1&group=sp&&cid=' + cid
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'

    try:
        res = json.loads(response.text)
    except:
        return False

    res = res['retS']
    html = str(base64.b64decode(res), 'utf-8')
    soup = BeautifulSoup(html, features='html.parser')
    return soup.find_all('img')[0].get('src')

def CrabPlantSrcNSII(name, path='NormalPath'):
    url = 'http://site.nsii.org.cn/API/SiteGallery.ashx?a=listphotosbysitetype&n={}&sitetype=CampusFlora'.format(name)
    response = requests.get(url=url, headers={'User-Agent': ua})
    response.encoding = 'utf-8'
    list = json.loads(response.text)

    if not len(list): 
        return False

    return 'http://site.nsii.org.cn/{}'.format(list[0][path])


def CrabPlantImage(name, DIRPath, method='NSII'):
    if method == 'NSII':
        src = CrabPlantSrcNSII(name)
        if src == False:
            return False
        return CrabImage(src, '{}/{}_NSII.jpg'.format(DIRPath, name))
    else:
        src = CrabPlantSrcPPBC(name)
        if src == False:
            return False
        return CrabImage(src, '{}/{}_PPBC.jpg'.format(DIRPath, name))

def load_list(filename, encoding=None, start=0, stop=None, step=1):
    '''
    from file load plant list
    '''
    assert isinstance(start, int) and start >= 0
    assert stop is None or (isinstance(stop, int) and stop > start)
    assert isinstance(step, int) and step >= 1
    
    lines = []
    with open(filename, 'r', encoding=encoding) as f:
        for _ in range(start):
            f.readline()
        for k, line in enumerate(f):
            if (stop is not None) and (k + start > stop):
                break
            if k % step == 0:
                lines.append(line.rstrip())
    return lines

def get_label_name_dict(filename):
    '''
    obtain plant name list
    '''
    records = load_list(filename, 'utf8')
    label_name_dict = {}
    for record in records:
        label, chinese_name, _ = record.split(',')
        kind_name = chinese_name.split('_')[-1]
        patterns = re.findall(r'[(](.*?)[)]', kind_name)
        if len(patterns):
            kind_name = patterns[0]
        label_name_dict[int(label)] = kind_name

    return label_name_dict

@func_timeout.func_set_timeout(5)
def CrabPlantInfo(name):
    '''
    grab plant infomation
    '''
    url = 'https://baike.baidu.com/item/{}'.format(name)
    response = requests.get(url=url, headers={'User-Agent': ua})
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features='html.parser')

    res = { 
            'd': soup.find(attrs={"name":"description"})['content'], # description
            'w': 0, # water
            'l': 0, # light
            't': 0, # temperature
        }

    if len(soup.findAll(text=re.compile('喜(潮|湿|阴|涝)'))):
        res['w'] = 1
    elif len(soup.findAll(text=re.compile('喜(热|阳|光|旱|温|亮)'))):
        res['w'] = -1
    
    # print(json.dumps(res, indent=4, ensure_ascii=False))
    return res

def loading(i, tot):
    '''
    进度条函数
    '''
    # sleep(1e-4)
    num = int(100*i/ tot)
    if num == 100:
        process = "\r[%3s%%]: |%-100s| completed!\n" % (num, '#' * num)
    else:
        process = "\r[%3s%%]: |%-100s|" % (num, '#' * num)

    print(process, end='', flush=True)

def weather():
    url = 'http://wthrcdn.etouch.cn/weather_mini?city={}'.format('上海')
    response = requests.get(url)
    response.encoding ='utf-8'
    return json.loads(response.text)['data']['forecast'][0]

if __name__ == '__main__':
    dict = get_label_name_dict('./modules/plant_id/models/label_map.txt')
    info = { 'data': {}, 'size': len(dict) }
    total = info['size']

    for i in range(0, total):
        try:
            info['data'][dict[i]] = CrabPlantInfo(dict[i])
        except func_timeout.exceptions.FunctionTimedOut:
            pass
        except Exception as e:
            pass

        loading(i+1, total)

    info['size'] = len(info['data'])

    with open('model.json', 'w') as fd:
        fd.write(json.dumps(info))

    # with open('model.json', 'r') as fd:
    #     info = json.load(fd)
    # print(info['size'])
    # # CrabPlantInfo('虎耳草')
