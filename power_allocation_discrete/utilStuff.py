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

'''
Created on Apr 21, 2014

Module containing some utility functions.

@author: mihai
'''

import os
import datetime

def writeListToFile(filePath, listToWrite):
    """
    Write the values of a list to a file.
    
    Keyword arguments:
    filePath -- Statistics file path.
    listToWrite -- list containing values that will be added to the file
    """
    if not os.path.isfile(filePath) or not os.path.exists(filePath):
        # if the file doesn't exits, then create it
        f = open(filePath, "w")
        f.close()
    
    stringToWrite = '\t'.join([str(x) for x in listToWrite])
    
    with open(filePath, 'a') as myFile:
        myFile.write(stringToWrite)
        myFile.write("\n")

def writeSomeListToFile(coordId, filePath, listToWrite):
    """
    Create directories to store result and write the values of a list to a file. 
    
    Keyword arguments:
    coordId -- Id for coordinator node
    filePath -- Statistics file path.
    listToWrite -- list containing values that will be added to the file
    """
    try:
        os.mkdir("./results")
    except OSError:
        pass
    try:
        os.mkdir("./results/coor_%d" % coordId)
    except OSError:
        pass
    if not os.path.isfile(filePath) or not os.path.exists(filePath):
        # if the file doesn't exits, then create it
        f = open(filePath, "w")
        f.close()
    stringToWrite = '\t'.join([str(x) for x in listToWrite])
    with open(filePath, 'a') as myFile:
        myFile.write(stringToWrite)
        myFile.write("\n")

def getFilePathWithDate(coordId, gameType, multiRun=False):
    """
    Get file path for statistics, add date and time to differentiate between different experiments.
    Do this here because the experiment may take a few minutes and I do not want the name to change.
    
    Keyword arguments:
    coordId -- numerical id for cluster coordinator.
    gameType -- numerical id for game played.
    multiRun -- if True then the game will be played for multiple times.    
    """
    try:
        os.mkdir("./results")
    except OSError:
        pass
    try:
        os.mkdir("./results/coor_%d" % coordId)
    except OSError:
        pass
    try:
        os.mkdir("./results/coor_%d/gameType_%d" % (coordId, gameType))
    except OSError:
        pass
    
    crtDate = datetime.datetime.now()
    name = "exp_"
    if multiRun:
        name = "multiRunExp_"
    fileName = name + "exp_%d-%d-%d_%d-%d-%d.dat" % (crtDate.day, crtDate.month, crtDate.year, crtDate.hour, crtDate.minute, crtDate.second)
    filePath = "./results/coor_%d/gameType_%d/%s" % (coordId, gameType, fileName)
    
    return filePath

