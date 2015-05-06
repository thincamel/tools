#coding:utf-8
import tornado
import re


def static_url_patch(domain):

    from tornado.template import Template
    old_generate = Template.generate
    def hack_generate(self, **kwargs):
        t = old_generate(self, **kwargs)
        print "hack generate"
        t = re.sub(r'(?<=[\'|"])/static/', r'http://%s/static/' % domain, t)
        return t

    tornado.template.Template.generate = hack_generate

