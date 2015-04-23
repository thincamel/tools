#!/usr/bin/env python
#coding: utf-8


import requests
import urllib
import sys


class Trans(object):

    def __init__(self, keyword):

        self.keyword = urllib.urlencode({'q': keyword})

        self.request_url = "http://fanyi.youdao.com/openapi.do?type=data&only=on&doctype=json&version=1.1&relatedUrl=http%3A%2F%2Ffanyi.youdao.com%2Fopenapi%3Fpath%3Dweb-mode&keyfrom=test&key=null&"

        self.request_url = "%s%s" % (self.request_url, self.keyword)

    def trans(self):

        # print self.request_url
        try:
            r = requests.get(self.request_url)
        except:
            sys.stderr.write("请求API失败\n")
            sys.exit(1)
        if r.status_code != 200:
            sys.stderr.write("请求API失败,状态码不为200\n")
            sys.exit(1)
        try:
            json_result = r.json()
        except:
            sys.stderr.write("转换json失败\n")
            sys.exit(1)

        return '|'.join(json_result['translation'])


if __name__ == "__main__":

    keyword = ' '.join(sys.argv[1:])
    t = Trans(keyword)
    print t.trans()



