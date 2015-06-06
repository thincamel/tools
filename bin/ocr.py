#coding:utf-8

import os
import requests
import base64

api_url = "http://apis.baidu.com/apistore/idlocr/ocr"
api_key = os.getenv("BAIDU_API_KEY")

def ocr_trans(file):
    headers = {'content-type': 'application/x-www-form-urlencoded', 'apiKey': api_key}
    data = {}
    data['fromdevice'] = "pc"
    data['clientip'] = "10.10.10.0"
    data['detecttype'] = "LocateRecognize"
    data['languagetype'] = "CHN_ENG"
    data['imagetype'] = 1
    with open(file, 'rb') as f:
        image = base64.b64encode(f.read())
        print image
    data['image'] = image

    r = requests.post(api_url, data=data, headers=headers)
    result = r.json()
    if str(result['errNum']) != '0':
        # print result['errMsg']
        return
    word = ''
    for item in result['retData']:
        word += "%s\n" % item['word']
    return word


if __name__ == "__main__":

    print ocr_trans("/Users/superadmin/Desktop/ocr22.jpg")

