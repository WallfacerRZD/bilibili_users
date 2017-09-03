import urllib2
import re
from Queue import PriorityQueue
import time
from multiprocessing import Pool
import threading
from multiprocessing.managers import BaseManager
from multiprocessing import Lock

pattern = re.compile('.*?"follower":(.*?)}.*?', re.S)


class QueueManager(BaseManager):
    pass


def get_followers(id):
    try:
        url = 'https://api.bilibili.com/x/relation/stat?vmid=' + str(id) + '&jsonp=jsonp&callback=_jsonpuwtgc3seorc'
        response = urllib2.urlopen(url)
        page = response.read()
        return re.findall(pattern, page)[0]
    except:
        return None


# def get_name(id):
#     url = 'https://space.bilibili.com/ajax/member/GetInfo'
#     data = urllib.urlencode({
#         'mid': str(id),
#     })
#     print data
#     request = urllib2.Request(url, data)
#     response = urllib2.urlopen(request)
#     print response.code

def process_users(begin_id):
    # process_lock.acquire()
    lock = threading.Lock()
    threads = []
    for i in range(20):
        threads.append(threading.Thread(target=deal_id, args=(range(begin_id, begin_id + 1000), lock)))
        begin_id += 1000

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
    # process_lock.release()

def deal_id(ids, lock):
    for id in ids:
        followers = get_followers(id)
        if followers is not None:
            followers = int(followers)
            print 'id %d done' % id
            lock.acquire()
            try:
                if len(users.queue) < 40:
                    users.put((followers, id))
                else:
                    if followers > users.queue[0][0]:
                        users.get()
                        users.put((followers, id))
                    else:
                        pass
            finally:
                lock.release()
        else:
            print 'id %d failed' % id
            pass
users = PriorityQueue()
if __name__ == '__main__':
    #process_lock = Lock()
    begin = time.time()
    p = Pool(4)
    begin_id = 1
    for i in range(4):
        # p.apply_async(process_users, args=(begin_id, process_lock))
        p.apply_async(process_users, args=(begin_id,))
        begin_id += 20000
    print 'all process are runing'
    p.close()
    p.join()
    print 'Done!!'
    end = time.time()
    with open('log.txt', 'w') as f:
        while not users.empty():
            user = users.get()
            f.write('id:%d followers: %d\n' % (user[1], user[0]))
        f.write('run time: %d seconds' % (end - begin))

