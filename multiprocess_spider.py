# coding=utf-8
import sys
import urllib2
import multiprocessing
import json
import Queue
import time
import threading
import urllib
import socket


"多进程 处理数据进程, 获取数据进程"

socket.setdefaulttimeout(5)
task_queue = multiprocessing.Queue()


def get_followers(mid):
    try:
        head = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
                'Referer': 'http://space.bilibili.com/' + str(mid)
            }
        response = urllib2.urlopen(urllib2.Request(url='https://api.bilibili.com/x/relation/stat?vmid=' + str(mid), headers=head))
        followers = json.loads(response.read())['data']['follower']
        return followers
    except:
        return None

# def get_name(self, id):
#     try:
#         post_data = urllib.urlencode({'mid': str(id)})
#         head = {
#             'User-Agent': self.user_agent,
#             'Referer': 'https://space.bilibili.com/' + str(id) + '/'
#         }
#         request = urllib2.Request('https://space.bilibili.com/ajax/member/GetInfo', headers=head, data=post_data)
#         response = urllib2.urlopen(request)
#         return json.loads(response.read())['data']['name']
#     except:
#         return str(id)

def save_failed_id_data():
    print 'save-failed'
    with open('logs/failed_id_%s.txt' % begin_id, 'w') as f:
        for mid in failed_id:
            f.write(str(mid) + '\n')


def deal_data_process(task_queue, begin_id, current_ids):
    bg_time = time.time()
    top_followers_users = Queue.PriorityQueue(40)
    while True:
        try:
            data = task_queue.get(timeout=5)
            if top_followers_users.full():
                min_data = top_followers_users.get()
                if data[0] > min_data[0]:
                    top_followers_users.put(data)
                else:
                    top_followers_users.put(min_data)
            else:
                top_followers_users.put(data)
            print u'id %s succeed' % data[1]
        except:
            break
    end_time = time.time()
    save_datas(bg_time, end_time, top_followers_users, begin_id, current_ids)


def work_thread(task_queue, failed_id, ids, current_ids, index):
    mid = ids[0]
    while mid <= ids[1]:
        try:
            current_ids[index] = mid
            followers = get_followers(mid)
            if followers is not None:
                followers = int(followers)
                data = (followers, mid)
                task_queue.put(data)
            else:
                print 'id %s failed!\n' % mid
                failed_id.append(mid)
        except Exception, e:
            print str(e)
        finally:
            mid += 1


def save_datas(begin, end, top_followers_users, begin_id, current_ids):
    print 'save data'
    with open('logs/begin_id_%s.txt' % begin_id, 'w') as f:
        while not top_followers_users.empty():
            data = top_followers_users.get()
            f.write('id:%d followers: %d\n' % (data[1], data[0]))
        f.write('spider has runned %d seconds\n' % (end - begin))
        f.write('end id %s\n' % str(current_ids))


def get_data_process(task_queue, failed_id, offset, thread_numbers, bg_id, run_time, current_ids):
    threads = []
    bg_time = time.time()
    try:
        for i in range(thread_numbers):
            threads.append(threading.Thread(target=work_thread, args=(task_queue, failed_id, (bg_id, bg_id + offset), current_ids, i)))
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
            if time.time() - bg_time > run_time:
                print 'time break'
                break
    except Exception, e:
        print str(e)
    finally:
        pass

if __name__ ==  '__main__':
    total_ids = 2 * 3600 * 8
    thread_numbers = 10
    offset = total_ids / thread_numbers
    run_time = 20
    task_queue = multiprocessing.Queue()
    manager = multiprocessing.Manager()
    failed_id = manager.list()
    current_ids = manager.list()
    begin_id = 1
    for i in range(thread_numbers):
        current_ids.append(1)
    try:
        process1 = multiprocessing.Process(target=get_data_process, args=(task_queue, failed_id, offset, thread_numbers, begin_id, run_time, current_ids))
        process2 = multiprocessing.Process(target=deal_data_process, args=(task_queue, begin_id, current_ids))
        process1.start()
        process2.start()
        process1.join()
        process2.join()
    except Exception, e:
        print str(e)
    finally:
        end = time.time()
        save_failed_id_data()
    print 'Done !!'

