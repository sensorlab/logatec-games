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
Created on Mar 13, 2014

@version: 1.6
@author: mihai
"""

import scipy
import linecache
import time

from games.myVersionOfPowerGame.gameCandidates.combComputations import getNodeCombinations, \
    printBadResultToFile, printPAPUtoFile
from games.myVersionOfPowerGame.gameNode import GameNode
from games.myVersionOfPowerGame.gainMeasurements import getDirectGainsNPl, \
    getCrossGains2Pl, getCrossGainsNPl, checkConvergenceRuleForSearch

class CandidateNodes:
    """
    class for finding candidate nodes for PAPU game 
    """

    # dictionary that stores node coordinates used for theoretical computation of h_ii, h_ji
    # contains coordinates for all nodes, even those that do not work
    coordIndustrial = {}
    coordIndustrial[1] = [45.934021, 14.23709800000006]
    coordIndustrial[2] = [45.930763, 14.237070000000017]
    coordIndustrial[3] = [45.936363, 14.237102999999934]
    coordIndustrial[4] = [45.935535, 14.236095999999975]
    coordIndustrial[5] = [45.936272, 14.236591999999973]
    coordIndustrial[6] = [45.93478, 14.237919000000034]
    coordIndustrial[11] = [45.93615, 14.23761400000000]
    coordIndustrial[12] = [45.935589, 14.238655999999992]
    coordIndustrial[13] = [45.935009, 14.238424000000009]
    coordIndustrial[14] = [45.935123, 14.23890700000004]
    coordIndustrial[15] = [45.935879, 14.238149000000021]
    coordIndustrial[16] = [45.932877, 14.237293000000022]
    coordIndustrial[17] = [45.932266, 14.237428000000023]
    coordIndustrial[24] = [45.934841, 14.236890000000017]
    coordIndustrial[25] = [45.931019, 14.23769500000003]
    coordIndustrial[26] = [45.935131, 14.236271999999985]
    
    coordCityCenter = {}
    coordCityCenter[22] = [45.916973, 14.22264999999993]
    coordCityCenter[23] = [45.918102, 14.222789000000034]
    coordCityCenter[30] = [45.917473, 14.225422999999978]
    coordCityCenter[31] = [45.918514, 14.223529999999982]
    coordCityCenter[32] = [45.917591, 14.22311400000001]
    coordCityCenter[33] = [45.916592, 14.220371999999998]
    coordCityCenter[34] = [45.917233, 14.223891999999978]
    coordCityCenter[35] = [45.917606, 14.226001999999994]
    coordCityCenter[38] = [45.916485, 14.219846999999959]
    coordCityCenter[41] = [45.91774, 14.223022000000014]
    coordCityCenter[42] = [45.917358, 14.224658999999974]
    coordCityCenter[44] = [45.918098, 14.223318999999947]
    coordCityCenter[45] = [45.916828, 14.221884000000045]
    coordCityCenter[46] = [45.917397, 14.223228000000063]
    coordCityCenter[49] = [45.917076, 14.223236000000043]
    coordCityCenter[50] = [45.916676, 14.220974999999953]
    

    def __init__(self, coordinatorId, nodeIDs):
        """
        Constructor
        
        Keyword arguments:
        coordinatorId -- id number of coordinator server
        nodesIDs -- list of node ids to test
        """
        self.coordinatorId = coordinatorId
        self.nodeIDsList = nodeIDs
        self.nodeIDsList.sort()
        self.nrNodes = len(self.nodeIDsList)
        self.nrPayrs = self.nrNodes / 2
        
    def findNodes(self, nrPlayers, nrCases, startWithRowFromFile=2):
        """ Find candidate nodes, exhaustive search. Do real world measurements and check convergence rule.
        First create a list of node objects and pass elements of this list, identified by their id read 
        from file, to methods that compute instant and cross gain.
        
        
        nrPlayers -- number of players to check for
        nrCases -- stop the search when the number of cases sought is found, for 
                    a 5 player game there a re 3.6e6 possible combinations!!
        startWithRowFromFile -- if something goes wrong experiments can resume from 
                    a specific combination. Read line numbering starts from 1 not from 0!!
        """
        # check if we have enough nodes
        if self.nrNodes < 4:
            raise Exception("The node ID list must contain at least 4 nodes!! "
                            "A player is formed by a transmitter node and a receiver node.")
        
        # check if the number of players can be realized by the available nodes
        if self.nrPayrs < nrPlayers:
            raise Exception("The number of available nodes cannot cover the number "
                            "searched players. (nrAvailableNodes/2) should be > nrPlayers")
        
        totalExperiments = scipy.math.factorial(self.nrNodes) / scipy.math.factorial(self.nrNodes - nrPlayers * 2) - startWithRowFromFile
        question = "total number of possible experiments %d proceed? - yes/no:" % (totalExperiments)
        choice = raw_input(question)
        if choice.lower() == "no":
            print "finishing..."
            return
        else:
            print "ok let's proceed"
            # create a list of vesna nodes and pass these nodes to methods
            vesnaNodes = [GameNode(self.coordinatorId, ids) for ids in self.nodeIDsList]
            path = getNodeCombinations(self.coordinatorId, self.nodeIDsList, nrPlayers)
            print "read permutations from", path
            
            casesFound = 0
            while casesFound < nrCases:
                """Repeat experiments with different node permutations until I find nrCases that satisfy
                PAPU algorithm convergence condition.
                """   
                for i in range(startWithRowFromFile, totalExperiments):
                    # get line that contains node ids, first line is a header
                    line = linecache.getline(path, i)
                    # use ids like this: tx_1, rx_1, tx_2, rx_2...
                    nodesUsed = map(int, line.split())
                    print "nodes used in this experiment ", nodesUsed
                    nodeObjects = list()
                    # get object list of nodes used in this experiment
                    for j in nodesUsed:
                        nodeObjects.append(vesnaNodes[self.nodeIDsList.index(j)])
                    # compute direct gains for nodes used in experiment
                    directGains = getDirectGainsNPl(self.coordinatorId, nodeObjects)
                    if nrPlayers == 2:
                        # reuse some code
                        crossGains = getCrossGains2Pl(self.coordinatorId, nodeObjects)
                    else:
                        crossGains = getCrossGainsNPl(self.coordinatorId, nodeObjects)
                    # if lists contain None then a bad measurement has occur, i.e. noise > gain
                    badMeasurement = False
                    for x in directGains:
                        if x is None:
                            badMeasurement = True
                    for x in crossGains:
                        if x is None:
                            badMeasurement = True
                    if badMeasurement:
                        printBadResultToFile(self.coordinatorId, nrPlayers, self.nodeIDsList, nodesUsed, directGains, crossGains, badMeasurement)
                    else:
                        # check convergence condition
                        if not checkConvergenceRuleForSearch(nrPlayers, directGains, crossGains):
                            print "nodes:", nodesUsed, "do not satisfy PAPU convergence rule"
                            printBadResultToFile(self.coordinatorId, nrPlayers, self.nodeIDsList, nodesUsed, directGains, crossGains, badMeasurement)
                        else:
                            # save results to file
                            casesFound += 1
                            printPAPUtoFile(self.coordinatorId, nrPlayers, self.nodeIDsList, nodesUsed, directGains, crossGains)

    def testSpecificPermutation(self, nrPlayers, nodesIdList):
        """
        Check power allocation game convergence rule for specific setup.
        
        Keyword arguments:
        nrPlayers -- number of players
        nodesIdList -- list describing player setup, e.g. [1,2,3,4] 2 player game, player 1 tx node is 1, rx node is 2, 
                       player 2 tx node is 3, rx node is 4.
        """
        nodeObjects = [GameNode(self.coordinatorId, ids) for ids in nodesIdList]
        directGains = getDirectGainsNPl(self.coordinatorId, nodeObjects)
        # check if bad measurement, if so then stop - no reason to continue
        badMeasurements = False
        if directGains is None:
            badMeasurements = True
        else:
            for x in directGains:
                if x is None: badMeasurements = True
        if not badMeasurements:
            # wait for things to cool down
            time.sleep(10)
            if nrPlayers == 2:
                # reuse some code
                crossGains = getCrossGains2Pl(self.coordinatorId, nodeObjects)
            else:
                crossGains = getCrossGainsNPl(self.coordinatorId, nodeObjects)
            if crossGains is None: 
                badMeasurements = True
            else:
                for x in crossGains:
                    if x is None: badMeasurements = True
        
        if badMeasurements:
            print "BAD MEASUREMENT"
        else:
            print "\n"
            print "h_ii: %s" % (', '.join([str(x) for x in directGains]))
            print "h_ii: %s" % (', '.join([str(x) for x in crossGains]))
            if not checkConvergenceRuleForSearch(nrPlayers, directGains, crossGains):
                print "nodes:", nodesIdList, "DO NOT MEET PAPU convergence rule"
            else:
                print "nodes SATISFY convergence condition"
                stringToAppend = '\t'.join([str(x) for x in nodesIdList]) + '\t' + '\t'.join([str(x) for x in directGains])
                stringToAppend += '\t' + '\t'.join([str(x) for x in crossGains])
                print stringToAppend
        
                    
        
