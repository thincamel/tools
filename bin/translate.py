#!/usr/bin/env python
#coding: utf-8


import requests
import urllib


class Trans(object):

    def __init__(self, keyword):

        self.keyword = urllib.urlencode({'q': keyword})

        self.request_url = "http://fanyi.youdao.com/openapi.do?type=data&only=on&doctype=json&version=1.1&relatedUrl=http%3A%2F%2Ffanyi.youdao.com%2Fopenapi%3Fpath%3Dweb-mode&keyfrom=test&key=null&"

        self.request_url = "%s%s" % (self.request_url, self.keyword)

    def trans(self):

        # print self.request_url
        r = requests.get(self.request_url)
        if r.status_code != 200:
            return None
        try:
            json_result = r.json()
        except:
            return None

        return '|'.join(json_result['translation'])


if __name__ == "__main__":

    t = Trans("hello,world")
    print t.trans()



