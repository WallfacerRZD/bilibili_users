# coding=utf-8
import urllib2
import random
import json
import Queue
import time
import threading
import urllib
import socket


"多线程"
socket.setdefaulttimeout(5)
class Bilibili_spider(object):
    def __init__(self):
        self.begin_id = 26300000
        self.failed_id = []
        self.user_agent = ["Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
                            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
                            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)",
                            "Mozilla/4.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)",
                            "Mozilla/1.22 (compatible; MSIE 10.0; Windows 3.1)",
                            "Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))",
                            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
                           ]
        self.top_followers_users = Queue.PriorityQueue(40)
        self.threads = []
        self.lock = threading.Lock()
        self.total_ids = 3700000
        self.run_time = 3600 * 18
        self.current_ids = []
        self.proxies = ['127.0.0.1', '140.240.81.16:8888','185.107.80.44:3128', '203.198.193.3:808', '125.88.74.122:85', '125.88.74.122:84', '125.88.74.122:82', '125.88.74.122:83', '125.88.74.122:81', '123.57.184.70:8081']

    def get_followers(self, id):
        try:
            head = {
                    'User-Agent': random.choice(self.user_agent),
                    'Referer': 'http://space.bilibili.com/' + str(id)
                }
            proxy = urllib2.ProxyHandler({'http': random.choice(self.proxies)})
            opener = urllib2.build_opener(proxy)
            response = opener.open(urllib2.Request(url='https://api.bilibili.com/x/relation/stat?vmid=' + str(id), headers=head, ))
            followers = json.loads(response.read())['data']['follower']
            return followers
        except:
            return None

    def get_name(self, id):
        try:
            post_data = urllib.urlencode({'mid': str(id)})
            head = {
                'User-Agent': self.user_agent,
                'Referer': 'https://space.bilibili.com/' + str(id) + '/'
            }
            request = urllib2.Request('https://space.bilibili.com/ajax/member/GetInfo', headers=head, data=post_data)
            response = urllib2.urlopen(request)
            return json.loads(response.read())['data']['name']
        except:
            return str(id)

    def save_failed_id_data(self):
        print 'save-failed'
        with open('logs/failed_id_%s.txt' % self.begin_id, 'w') as f:
            for id in self.failed_id:
                f.write(str(id) + '\n')

    def deal_data(self, data, lock):
        lock.acquire()
        if self.top_followers_users.full():
            min_data = self.top_followers_users.get()
            if data[0] > min_data[0]:
                self.top_followers_users.put(data)
            else:
                self.top_followers_users.put(min_data)
        else:
            self.top_followers_users.put(data)
        print u'id %s succeed' % data[1]
        lock.release()

    def work_thread(self, ids, lock, current_ids, index):
        mid = ids[0]
        current_ids[index][1] = ids[1]
        while mid <= ids[1]:
            current_ids[index][0] = mid
            followers = self.get_followers(mid)
            if followers is not None:
                followers = int(followers)
                data = (followers, mid)
                self.deal_data(data, lock)
            else:
                print 'id %s failed\n' % mid
                self.failed_id.append(mid)
            mid += 1

    def save_datas(self, begin, end):
        print 'save data'
        with open('logs/begin_id_%s.txt' % self.begin_id, 'w') as f:
            while not self.top_followers_users.empty():
                data = self.top_followers_users.get()
                f.write('id:%d followers: %d\n' % (data[1], data[0]))
            f.write('spider has runned %d seconds\n' % (end - begin))
            f.write('end id %s\n' % str(self.current_ids))

    def main(self):
        bg_time = time.time()
        bg_id = self.begin_id
        thread_numbers = 10
        offset = self.total_ids / thread_numbers
        threads = []
        for i in range(thread_numbers):
            self.current_ids.append([1, 1])
        try:
            for i in range(thread_numbers):
                threads.append(threading.Thread(target=self.work_thread, args=((bg_id, bg_id + offset), self.lock, self.current_ids, i)))
                bg_id += offset
            for thread in threads:
                thread.setDaemon(True)
            for thread in threads:
                thread.start()
            while True:
                alive_count = 0
                for thread in threads:
                    if thread.is_alive():
                        alive_count += 1
                if alive_count == 0:
                    print 'alive break'
                    break
                if time.time() - bg_time > self.run_time:
                    print 'time break'
                    break
            # for thread in threads:
            #     thread.join()
            print 'done'
        except Exception, e:
            print str(e)
        finally:
            end = time.time()
            self.save_datas(bg_time, end)
            self.save_failed_id_data()
        print 'Done !!'


if __name__ == '__main__':
    spider = Bilibili_spider()
    spider.main()
