#-*- encoding: utf-8 -*-

import sys
reload(sys).setdefaultencoding("utf8")

import urllib
import urllib2
import json

def reply(url, s):
    try:
        response = urllib2.urlopen(url + urllib.quote(s.encode("utf8")) +"今天的天气")
        data = response.read()
        result = json.loads(data.decode("utf8"))
        re = result['text']
        return re.decode("utf8")
    except:
        return "玩坏掉了。"