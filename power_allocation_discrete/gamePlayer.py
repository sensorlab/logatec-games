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
Created on Mar 18, 2014

Based on: https://github.com/sensorlab/logatec-games/tree/master/Power_Allocation_Game

@version: 2.0
@author: mihai
'''

import math

from games.myVersionOfPowerGame.playerPhysicalLayer import PlayerPhysicalLayer
from games.myVersionOfPowerGame.myQueue import MyQueue

class GamePlayer:
    """
    Defines a game player (tx node, rx node, tx characteristics..)
    Has attached a playerApp and a powerAllocation object. 
    """

    # player power cost [1/W], must be in [0,1]
    cost = 0
    scaledCost = 0

    # channel gains, dimensionless
    directGain = 0.0
    crossGain = 0.0
    
    # noise power, must be measured
    noisePower = 6.43e-13
    
    # player number used for identification
    playerNumber = None
    
    # current transmission power [dBm]. updated based in game iterations 
    currentTxPower = 0.0
    
    # used for transmitting data and sensing the spectrum
    physicalLayer = None
    
    # compute best response only if player is not the source of the event
    sourceOfEvent = False
    
    # count number of iterations 
    playerIterations = 0
    
    # save result in this list
    queueList = None
    
    # threshold_power. This can be set any time. We need this when we determine if Nash equilibrium was reached
    thresholdPower = 0.8

    def __init__(self, coordinatorId, txNodeId, rxNodeId, cost, playerNumber, gameFreq, gameType=0):
        """
        Create a player and initialize internal parameters.
        
        Keyword arguments:
        coordinatorId -- Numerical cluster id.
        txNodeId -- Numerical id for transmission node.
        rxNodeId -- Numerical id for receiver node.
        cost -- Energy cost.
        playerNumber -- Numerical number used to identify players.
        gateType -- Type of game played.
        """
        
        self.coordinatorId = coordinatorId
        self.cost = cost
        self.playerNumber = playerNumber
        self.gameFreq = gameFreq
        self.gameType = gameType
        
        self.txNodeId = txNodeId
        self.rxNodeId = rxNodeId
        
        self.sourceOfEvent = False
        
        self.queueList = MyQueue(5)
        self.playerIterations = 0
        
        # initialize physical layer
        self.physicalLayer = PlayerPhysicalLayer(self, txNodeId, self.rxNodeId, self.coordinatorId, self.gameFreq, self.cost, self.gameType)

    def resetPlayerObject(self):
        """Use this to reset player variables, used for multiple runs"""
        self.queueList.emptyList()
        self.playerIterations = 0
        self.physicalLayer.changeTxPowerRandomly()

    def getPlayerNumber(self):
        return self.playerNumber
    
    def getPlayerCost(self):
        return self.cost
    
    def setPlayerCost(self, newCost):
        self.cost = newCost
    
    def getScaledCost(self):
        return self.scaledCost
    
    def setScaledCost(self, newScaledCost):
        self.scaledCost = newScaledCost
        self.physicalLayer.setCost(self.scaledCost)
    
    def getNrPlayerIterations(self):
        return self.playerIterations
    
    def generatePowerEvent(self):
        """Generate new tx power"""
        self.sourceOfEvent = True
        self.physicalLayer.changeTxPowerRandomly()
        return self.physicalLayer.getCrtTxPower()
    
    def updateTxPowerAsAverage(self):
        """Update current transmission power as average of last 5 tx powers"""
        bestRespList = self.queueList.getList()
        nrBestResp = len(bestRespList)
        mySum = 0
        
        for i in range(0, nrBestResp):
            mySum += float(bestRespList[i])
            
        avgTxPw = mySum / float(nrBestResp)
        self.physicalLayer.changeTxPower(avgTxPw)
        self.queueList.append(self.physicalLayer.getCrtTxPower())
    
    def updateTxPower(self, pTxj, hjiDict):
        """
        Update current transmission power based on best response relation.
        Must extract from pj a list of tx power for adversaries, delete from list tx power of current player
        
        Keyword arguments:
        pTxj -- dictionary with players tc powers in [dBm]
        hjiList -- dictionary with player cross gains for current player, e.g. {2:h_21,3:h_31}
        """
        # create list with opponent tx powers and cross gains
        self.playerIterations += 1
        
        opponentPowers = list()
        crossG = list()
        updateResult = False
        
        for key in pTxj:
            if key != self.playerNumber:
                opponentPowers.append(pTxj[key])
                crossG.append(hjiDict[key])
        
        bestResp = self.physicalLayer.computeBestResponseForm1(opponentPowers, crossG)
        if bestResp is not None:
            # sometimes the difference in best response in negative
            # in that case do nothing, player will continue to transmit
            # with current power
            updateResult = True
            self.physicalLayer.changeTxPower(bestResp)
        
        # self.result.append([iteration, self.physicalLayer.getCrtTxPower(), self.physicalLayer.bestResponseUntouched, self.cost])
        # TODO: in jocul facut de studenti cond de echilibru e verificata pe val reala, mai corect e pt cea discretizata  
        self.queueList.append(self.physicalLayer.getCrtTxPower())
        
        return updateResult
    
    def updateTxPower1(self, measuredRxPower):
        """
        Update current transmission power based on best response relation, and measured power.
        
        Keyword arguments:
        measuredRxPower -- Measured receiving power, i.e. sum(h_ji * p_j) + n_0
        """
        self.playerIterations += 1
        bestResp = self.physicalLayer.computeBestResponseForm2(measuredRxPower)
        if bestResp is not None:
            # sometimes the difference in best response in negative
            # in that case do nothing, player will continue to transmit
            # with current power
            updateResult = True
            self.physicalLayer.changeTxPower(bestResp)
        
        self.queueList.append(self.physicalLayer.getCrtTxPower())
        
        return updateResult
    
    def updateTxPower2(self, measuredRxpower):
        """
        Update current transmission power based on best response relation, and measured power.
        
        Keyword arguments:
        measuredRxPower -- Measured receiving power, i.e. sum(h_ji * p_j) + n_0
        """
        self.playerIterations += 1
        bestResp = self.physicalLayer.computeBestResponseForm3(measuredRxpower)
        if bestResp is not None:
            updateResult = True
            self.physicalLayer.changeTxPower(bestResp)
        else:
            updateResult = False
        self.queueList.append(self.physicalLayer.getCrtTxPower())
        return updateResult
        
    def setThresholdPower(self, newThresholdPower):
        """Set threshold power used to determine if player has reached equilibrium"""    
        self.thresholdPower = newThresholdPower
        print "Player %d : threshold power was set to: %.3f" % (self.playerObject.playerNumber, self.thresholdPower)
    
    
    def isInEquilibrium(self, equalCondition=True):
        """
        Check if player has reached a stable state
        
        Keyword arguments:
        equalCondition -- true->all elements from history must be equal.
        """
        bestrespList = self.queueList.getList()
        length = self.queueList.len
        
        if len(bestrespList) != length:
            return False
        
        if equalCondition:
            # all best responses must be equal
            for i in range(1, len(bestrespList)):
                if float(bestrespList[0]) != float(bestrespList[i]):
                    return False
            print "Player %d has reached a stable state, i.e. equilibrium." % (self.playerNumber)
            return True
        else:
            for i in range(1, len(bestrespList)):
                if math.fabs(math.fabs(float(list[0])) - math.fabs(float(bestrespList[i]))) > float(self.thresholdPower):
                    return False
            print "Player %d has reached a stable state, i.e. equilibrium." % (self.playerNumber)
            return True
        
