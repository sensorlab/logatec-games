# Copyright (C) 2014 SensorLab, Jozef Stefan Institute
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

# Authors: Mihai Suciu
#
"""
Created on Mar 18, 2014

Based on: https://github.com/sensorlab/logatec-games/tree/master/Power_Allocation_Game

@version: 2.0
@author: mihai
"""

from collections import deque

class MyQueue:
    """This class forms a queue of a given size. It has methods for appending data and returning the current queue.
    As implemented: https://github.com/sensorlab/logatec-games/tree/master/Power_Allocation_Game

    """
    len = 0

    def __init__(self, queueLen):
        self.len = queueLen

        self.queueList = deque([])

    def append(self, value):
        if len(self.queueList) < self.len:
            self.queueList.appendleft(value)
        elif len(self.queueList) == self.len:
            self.queueList.pop()
            self.queueList.appendleft(value)

    def getList(self):
        # return list as the following: [last value added, older value, older value...]
        return list(self.queueList)

    def getListReverse(self):
        # returns list as the following: [oldest value, newer value,. ... , last value added]
        tmpList = list(self.queueList)
        tmpList.reverse()
        return tmpList

    def emptyList(self):
        self.queueList = deque([])
