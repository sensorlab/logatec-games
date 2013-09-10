from collections import deque

class MyQueue:
    #This class forms a queue of a given size. It has methods for appending data and returning the current queue.
    len = 0
    
    def __init__(self, queue_len):
        self.len = queue_len
        
        self.queue_list = deque([])
        
    def append(self, value):
        if len(self.queue_list) < self.len:
            self.queue_list.appendleft(value)
        elif len(self.queue_list) == self.len:
            self.queue_list.pop()
            self.queue_list.appendleft(value)
    
    def getList(self):
        #return list as the following: [last value added, older value, older value...]
        return list(self.queue_list)
    
    def getListReverse(self):
        #returns list as the following: [oldest value, newer value,. ... , last value added]
        tmp_list = list(self.queue_list)
        tmp_list.reverse()
        return tmp_list
    
    def emptyList(self):
        self.queue_list = deque([])
