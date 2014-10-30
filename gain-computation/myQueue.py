# Copyright (C) 2013 SensorLab, Jozef Stefan Institute
# http://sensorlab.ijs.si
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. */

# Authors: Andrei Toma
#   	Ciprian Anton
#

from collections import deque

class MyQueue:
    #This class form a queue with a given size. It has methods for appending data and returning the current queue.
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
