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
Created on May 7, 2014

Perform periodic measurements between different players (direct and cross gain).

@author: Mihai
"""
import datetime
import time
import gameNode
from gameNode import GameNode
from gainMeasurements import getDirectGainsNPl,\
    getCrossGains2Pl, measureGainBetwTxRx
from utilStuff import writeSomeListToFile

def main():
    # perform measurements in 5 minute interval until 16:00
    nodesUsed = [51,52,56,59]
    coordId = gameNode.JSI

    # create list of node objects
    vesnaNodes = [GameNode(coordId,ids) for ids in nodesUsed]
    crtDate = datetime.datetime.now()
    filePath = "./results/coor_%d/longTermMeas_%s_exp_%d-%d-%d_%d-%d-%d.dat" % (coordId, ''.join([str(x) for x in nodesUsed]), crtDate.day, crtDate.month, crtDate.year, crtDate.hour, crtDate.minute, crtDate.second)
    #perform gain measurements, at 5 minute intervals, between two players for 4 hours.
    #player 1 - 51->52, player 2 - 56->59
    performMeasurements(coordId,vesnaNodes, crtDate.hour+4, crtDate.minute, filePath)

def performMeasurements(coordonatorId, nodeObjUsed, stopHour, stopMinute, filePath):
    a = 0
    while True:
        if datetime.datetime.now().hour > stopHour and datetime.datetime.now().minute > stopMinute:
            break
        else:
            a += 1
            #directGains = getDirectGainsNPl(coordonatorId,nodeObjUsed)
            #crossGains = getCrossGains2Pl(coordonatorId,nodeObjUsed)
            resultList = [datetime.datetime.now().hour, datetime.datetime.now().minute]
            #h_11
            resultList.append(measureGainBetwTxRx(coordonatorId, nodeObjUsed[0], nodeObjUsed[1], 2422e6, txPower=0, transDuration=6))
            #h_22
            resultList.append(measureGainBetwTxRx(coordonatorId, nodeObjUsed[2], nodeObjUsed[3], 2422e6, txPower=0, transDuration=6))
            time.sleep(5)
            #h_21
            resultList.append(measureGainBetwTxRx(coordonatorId, nodeObjUsed[2], nodeObjUsed[1], 2422e6, txPower=0, transDuration=6))
            #h_12
            resultList.append(measureGainBetwTxRx(coordonatorId, nodeObjUsed[0], nodeObjUsed[3], 2422e6, txPower=0, transDuration=6))
#             for elem in directGains:
#                 resultList.append(elem)
#             for elem in crossGains:
#                 resultList.append(elem)
            writeSomeListToFile(coordonatorId,filePath,resultList)
            print "Measurement %d at %d:%d"%(a,datetime.datetime.now().hour,datetime.datetime.now().minute)
            print "sleep for 5 minutes"
            time.sleep(5*60)
    print "Finish measurements!! :)(:"
#     while datetime.datetime().now().hour < stopHour:
#         directGains = getDirectGainsNPl(coordonatorId,nodeObjUsed)
#         crossGains = getCrossGains2Pl(coordonatorId,nodeObjUsed)
#         resultList = [datetime.datetime.now().hour, datetime.datetime.now().minute]
#         for elem in directGains:
#             resultList.append(elem)
#         for elem in crossGains:
#             resultList.append(elem)
#         writeSomeListToFile(coordonatorId,filePath,resultList)
#         time.sleep(5*60)

if __name__ == '__main__':
    main()