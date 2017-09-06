import requests
import urllib2
import urllib
import json
import chardet

data = urllib.urlencode({'mid': '7714'})

head = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Referer': 'http://space.bilibili.com/7714',
}

#response = requests.session().post('https://space.bilibili.com/ajax/member/GetInfo', headers=head, data=data)
request = urllib2.Request('https://space.bilibili.com/ajax/member/GetInfo', headers=head, data=data)
response = urllib2.urlopen(request)
js = json.loads(response.read())
name = js['data']['name']
print type(name)

