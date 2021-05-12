import requests
import os
import sys
import base64
import json

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
        return CrabImage(src, '{}/{}_PBCC.jpg'.format(DIRPath, name))
