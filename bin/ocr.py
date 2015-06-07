#!/usr/bin/env python
#coding:utf-8


# 百度ocr服务：http://apistore.baidu.com/apiworks/servicedetail/146.html
import os
import requests
import base64
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

api_url = "http://apis.baidu.com/apistore/idlocr/ocr"
api_key = os.getenv("BAIDU_API_KEY")

if not api_key:
    raise Exception("baidu api key is none")

def b64encode_image(image):
    with open(image,'rb') as f:
        return base64.b64encode(f.read())

def ocr_trans(f):
    # headers = {'content-type': 'multipart/form-data', 'apikey': api_key, 'Accept': '*/*'}
    headers = {'apikey': api_key}
    data = {}
    data['fromdevice'] = "pc"
    data['clientip'] = "10.10.10.0"
    data['detecttype'] = "LocateRecognize"
    data['languagetype'] = "CHN_ENG"
    data['imagetype'] = 2
    # 233333,百度用文件名来判断是否是jpg文件,全部指定为xx.jpg.
    r = requests.post(api_url,headers=headers, data=data, files={"image": ('xx.jpg', f)})
    result = r.json()
    if str(result['errNum']) != '0':
        print result['errMsg']
        return
    word = ''
    for item in result['retData']:
        word += "%s\n" % item['word']
    return word.rstrip()


if __name__ == "__main__":

    import sys
    arg = sys.argv[1]
    if arg.startswith('http://') or arg.startswith('https://'):
        r = requests.get(arg)
        print ocr_trans(r.content)
    else:
        with open(arg,'rb') as f:
            print ocr_trans(f)
