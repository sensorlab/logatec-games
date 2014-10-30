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
Created on Mar 14, 2014

Module containing methods for combinatoric computations used in automatic identification of
potential nodes for power allocation game.

@author: mihai
"""

import os
import datetime

from timeit import itertools

def transform(t):
    """Transform a list of tuple in a list of list"""
    if type(t) == list or type(t) == tuple:
        return [transform(i) for i in t]
    return t

def getNodeCombinations(coordID, nodeIDsList, nrPlayers):
    """Compute all permutations for nodes."""
    # check if folders exits. If not then create them
    try:
        os.mkdir("./permutations/")
    except OSError:
        pass
    try:
        os.mkdir("./permutations/coor_%d" % coordID)
    except OSError:
        pass
        
    nodesStr = ''.join([str(x) for x in nodeIDsList])
    path = "./permutations/coor_%d/%dplayersNodes%s.dat" % (coordID, nrPlayers, nodesStr)
    if not os.path.isfile(path) or not os.path.exists(path):
        # file does not exist so create it
        createPermutationFile(path, nodeIDsList, nrPlayers)
        
    # return file path
    return path

def createPermutationFile(filePath, nodeIdList, nrPlayers):
    """Create all permutations for nodes in nodeIdList and write them in a file for future use"""
    myFile = open(filePath, 'w+')
    # write header
    myFile.write("permutations for nodes: %s\n" % (', '.join([str(x) for x in nodeIdList])))
    # get list of all permutations and write it in file
    rez = itertools.permutations(nodeIdList, nrPlayers * 2)
    if nrPlayers < 5:
        combList = transform(list(rez))
        for elem in combList:
            myFile.write('\t'.join([str(x) for x in elem]))
            myFile.write("\n")
    else:
        # listaTuple = list(rez)
        # write permutations to file
        for item in rez:
            aux = list(item)
            myFile.write("\t".join([str(x) for x in aux]))
            myFile.write("\n")
    myFile.close()

def printBadResultToFile(coordinatorId, nrPlayers, nodeIdsList, permutationList, directGains, crossGains, badMeasurement=False):
    """Append to a file nodes that do not satisfy PAPU convergence rule."""
    try:
        os.mkdir("./permutations")
    except OSError:
        pass
    try:
        os.mkdir("./permutations/coor_%d" % coordinatorId)
    except OSError:
        pass
    try:
        os.mkdir("./permutations/coor_%d/results" % coordinatorId)
    except OSError:
        pass
    
    path = "./permutations/coor_%d/results/result%dplayersNodes%s.dat" % (coordinatorId, nrPlayers, ''.join([str(x) for x in nodeIdsList]))
    if not os.path.isfile(path) or not os.path.exists(path):
        # if the file doesn't exits, then create it
        print "Writing a new file"
        f = open(path, "w")
        f.write("[node permutations]                [direct gains]           [cross gains]            [Date]     - all power units in W\n")
        f.close()
    
    stringToAppend = '\t'.join([str(x) for x in permutationList])
    if directGains is not None:
        stringToAppend += '\t' + '\t'.join([str(x) for x in directGains])
    if crossGains is not None:
        stringToAppend += '\t' + '\t'.join([str(x) for x in crossGains])
    if badMeasurement:
        stringToAppend += "\tBAD MEASUREMENT"
    else:
        stringToAppend += "\tNODES DO NOT MEET CONVERGENCE RULE"
    stringToAppend += '\t' + str(datetime.datetime.now())
    with open(path, 'a') as myFile:
        myFile.write(stringToAppend)
        myFile.write("\n")
    
def printPAPUtoFile(coordinatorId, nrPlayers, nodeIdsList, permutationList, directGainList, crossGainList):
    """Append nodes that satisfy PAPU convergence rule to a file.
    
    coordinatorId -- Id for coordinator node
    nrPlayers -- number of players that play the game
    nodeIdList -- id of nodes for which we compute permutations
    permutationList -- list containing nrPlayers pairs of transmitter receiver node id
    directGainList -- list containing direct gains, e.g. [h_11, h_22] for a 2 player game
    crossGainList -- list containing cross gains, e.g. [h21, h12] for a 2 player game 
    """
    try:
        os.mkdir("./permutations")
    except OSError:
        pass
    try:
        os.mkdir("./permutations/coor_%d" % coordinatorId)
    except OSError:
        pass
    try:
        os.mkdir("./permutations/coor_%d/results" % coordinatorId)
    except OSError:
        pass
    
    path = "./permutations/coor_%d/results/result%dplayersNodes%s.dat" % (coordinatorId, nrPlayers, ''.join([str(x) for x in nodeIdsList]))
    if not os.path.isfile(path) or not os.path.exists(path):
        # if the file doesn't exits, then create it
        print "Writing a new file"
        f = open(path, "w")
        f.write("[node permutations]                [direct gains]           [cross gains]            [Date]     - all power units in W\n")
        f.close()
    
    # apend new data to file
    stringToAppend = '\t'.join([str(x) for x in permutationList]) + '\t' + '\t'.join([str(x) for x in directGainList])
    stringToAppend += '\t' + '\t'.join([str(x) for x in crossGainList]) + '\t' + str(datetime.datetime.now())
    with open(path, 'a') as myFile:
        myFile.write(stringToAppend)
        myFile.write("\n")

def printTheoreticalResultToFile(coordinatorId, nrPlayers, nodeIdsList, permutationList, directGainList, crossGainList, badResult=False):
    """
    Append nodes that satisfy/do not satisfy PAPU convergence rule to a file.
    Check convergence based on theoretical h_ii, h_ji. h_ii = d^(-4)
    
    coordinatorId -- Id for coordinator node
    nrPlayers -- number of players that play the game
    nodeIdList -- id of nodes for which we compute permutations
    permutationList -- list containing nrPlayers pairs of transmitter receiver node id
    directGainList -- list containing direct gains, e.g. [h_11, h_22] for a 2 player game
    crossGainList -- list containing cross gains, e.g. [h21, h12] for a 2 player game 
    badResult -- if True -> nodes do not meet power allocation game convergence condition
    """
    try:
        os.mkdir("./permutations")
    except OSError:
        pass
    try:
        os.mkdir("./permutations/coor_%d" % coordinatorId)
    except OSError:
        pass
    try:
        os.mkdir("./permutations/coor_%d/results" % coordinatorId)
    except OSError:
        pass
    path = "./permutations/coor_%d/results/theoreticalResult%dplayersNodes%s.dat" % (coordinatorId, nrPlayers, ''.join([str(x) for x in nodeIdsList]))
    path2 = "./permutations/coor_%d/results/theoreticalSugestions%dplayers.dat" % (coordinatorId, nrPlayers)
    if not os.path.isfile(path) or not os.path.exists(path):
        # if the file doesn't exits, then create it
        print "Writing a new file"
        f = open(path, "w")
        f.write("[node permutations]                [direct gains]           [cross gains]            [Date]     - all power units in W\n")
        f.close()
        f1 = open(path2, "w")
        f1.write("[node permutations that should work]")
        f1.close()
    
    stringToAppend = '\t'.join([str(x) for x in permutationList])
    if badResult:
        stringToAppend += "\tNODES DO NOT MEET CONVERGENCE RULE"
    else:
        stringToAppend += '\t' + '\t'.join([str(x) for x in directGainList])
        stringToAppend += '\t' + '\t'.join([str(x) for x in crossGainList])
        stringToAppend2 = '\t'.join([str(x) for x in permutationList])
        
        with open(path2, 'a') as myFile2:
            myFile2.write(stringToAppend2)
            myFile2.write("\n")
        
    stringToAppend += '\t' + str(datetime.datetime.now())
    with open(path, 'a') as myFile:
        myFile.write(stringToAppend)
        myFile.write("\n")
