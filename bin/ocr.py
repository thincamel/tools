#coding:utf-8


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
    r = requests.post(api_url,headers=headers, data=data, files={"image": f})
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
        arg = '/tmp/ocr.jpg'
        with open(arg, 'wb') as f:
            f.write(r.content)
    with open(arg,'rb') as f:
        print ocr_trans(f)
