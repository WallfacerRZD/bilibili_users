# coding=utf-8
import urllib2
import sys
import re
import json
import Queue
import time
import threading
import urllib
import chardet
pattern = re.compile('.*?"follower":(.*?)}.*?', re.S)


class Bilibili_spider(object):
    def __init__(self):
        self.new_id = set()
        self.crawled_id = set()
        self.data_queue = Queue.Queue()
        self.failed_id = Queue.Queue()
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
        self.referer = 'http://space.bilibili.com/'
        self.begin_id = int(sys.argv[1])
        self.top_followers_users = Queue.PriorityQueue(40)
        self.threads = []

    def get_followers(self, id):
        try:
            head = {
                    'User-Agent': self.user_agent,
                    'Referer': self.referer + str(id)
                }
            request = urllib2.Request(url = 'https://api.bilibili.com/x/relation/stat?vmid=' + str(id) + '&jsonp=jsonp&callback=_jsonpuwtgc3seorc', headers=head)
            response = urllib2.urlopen(request)
            page = response.read()
            return re.findall(pattern, page)[0]
        except:
            return None

    def get_name(self, id):
        try:
            post_data = urllib.urlencode({'mid': str(id)})
            head = {
                'User-Agent': self.user_agent,
                'Referer': self.referer + str(id)
            }
            request = urllib2.Request('https://space.bilibili.com/ajax/member/GetInfo', headers=head, data=post_data)
            response = urllib2.urlopen(request)
            return json.loads(response.read())['data']['name'].decode('utf-8')
        except:
            return str(id)

    def save_failed_id_data(self):
        print 'save-failed'
        with open('logs/failed_id_%s.txt' % self.begin_id, 'w') as f:
            while not self.failed_id.empty():
                f.write(str(self.failed_id.get()) + '\n')

    def get_data(self, ids):
        try:
            for id in ids:
                followers = self.get_followers(id)
                # name = self.get_name(id)
                if followers is not None:
                    followers = int(followers)
                    data = (followers, id)
                    if self.top_followers_users.full():
                        min_data = self.top_followers_users.get()
                        if data[0] > min_data[0]:
                            self.top_followers_users.put(data)
                        else:
                            self.top_followers_users.put(min_data)
                    else:
                        self.top_followers_users.put(data)
                    print 'id %d succeed' % id
                else:
                    print 'id %d failed' % id
                    self.failed_id.put(id)
            print '%s end' % threading.current_thread().name
        except Exception, e:
            print str(e)

    def deal_data(self, data):
        if self.top_followers_users.full():
            min_data = self.top_followers_users.get()
            if data[0] > min_data[0]:
                self.top_followers_users.put(data)
            else:
                self.top_followers_users.put(min_data)
        else:
            self.top_followers_users.put(data)

    def save_datas(self):
        print 'save data'
        with open('logs/begin_id_%d.txt' % self.begin_id, 'w') as f:
            while not self.top_followers_users.empty():
                user = self.top_followers_users.get()
                f.write('id:%s followers: %d\n' % (user[1], user[0]))

    def start(self):
        bg = self.begin_id
        for i in range(10):
            self.threads.append(threading.Thread(target=self.get_data, args=(range(bg, bg + 100), )))
            bg += 100
        begin = time.time()
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()
        print 'Done!!'
        end = time.time()
        self.save_datas()
        self.save_failed_id_data()
        with open('logs/begin_id_%d.txt' % self.begin_id, 'a') as f:
            f.write('run time: %d seconds' % (end - begin))

if __name__ == '__main__':
    spider = Bilibili_spider()
    spider.start()
