# coding=utf-8
import time, sys, Queue
from multiprocessing.managers import BaseManager
from multiprocessing import Value
from multiprocessing import Manager
from multiprocessing import freeze_support

class QueueManager(BaseManager):
    pass

users = Queue.PriorityQueue()
users_queue = users.queue
finished = Value(bool, False)



def get_users():
    return users


def get_users_len():
    return len(users_queue)


def get_users_queue():
    return users_queue


def get_flag():
    return finished


def get_min_user():
    return users_queue[0][0]


if __name__ == '__main__':
    QueueManager.register('get_users', callable=get_users)
    QueueManager.register('get_flag', callable=get_flag)
    QueueManager.register('get_users_queue', callable=get_users_queue)
    QueueManager.register('get_users_len', callable=get_users_len)
    QueueManager.register('get_min_user', callable=get_min_user)
    manager = QueueManager(address=('118.114.41.153', 5000), authkey='rzd')
    freeze_support()
    manager.start()
    l = manager.list
    print 'server started'
    print l

    while not manager.get_flag():
        pass
    print manager.get_users_queue()
