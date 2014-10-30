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
Created on Apr 16, 2014

Just an object to control transmissions and spectrum sensing. 

@version: 1.0
@author: m
'''

import random
import math

from games.myVersionOfPowerGame.playerTransmitLayer import PlayerTransmitLayer
from games.myVersionOfPowerGame.playerSenseLayer import PlayerSenseLayer
from games.myVersionOfPowerGame.gameNode import GameNode

class PlayerPhysicalLayer:
    """
    Control transmission and spectrum sensing for a player.
    """

    # VESNA power generating list. This must be sorted. Powers are in dBm
    #minimum output power for cc2500 according to texas instruments in -30dBm
    availableTxPowers = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18, -20, -22, -24, -26, -28, -30]
    
    # current transmitting power [dBm]
    currentTxPower = random.choice(availableTxPowers)
    
    # previous transmitted_power [dBm]
    previousTxPower = currentTxPower
    bestResponseUntouched = 0
    
    # direct and cross gains
    directGain = 0
    crossGain = 0
    
    # used for sending data
    transmitObject = None
    # used for sensing the spectrum
    senseObject = None
    
    # game type - can be: 1, 2, 3 . Depends on the implementation you want to use
    gameType = 3
    
    # neighborPowerEvent. When this is True, It means that neighbor player changed its power
    neighborPowerEvent = False
    
    # When this is triggered (=True) then it means that equilibrium has been reached and the threads stops here.
    equilibriumDetected = False
    
    def __init__(self, playerObject, txNodeId, rxNodeId, coordinatorId, gameFreq, cost, gameType=3):
        """
        Create a physical layer object and initialize internal parameters.
        
        Keyword arguments:
        coordinatorId -- Numerical cluster id.
        cost -- Energy cost.
        gateType -- Type of game played.
        """
        self.playerObject = playerObject
        self.coordinatorId = coordinatorId
        self.gameFreq = gameFreq
        self.cost = cost
        self.gameType = gameType
        
        # configure tx and rx nodes
        self.txNode = GameNode(coordinatorId, txNodeId)
        self.rxNode = GameNode(coordinatorId, rxNodeId)
        
        # configure sense node. Just need to do this once.
        self.rxNode.setSenseConfiguration(gameFreq, gameFreq, 400e3)
        
        self.currentTxPower = random.choice(self.availableTxPowers)
        self.previousTxPower = self.currentTxPower
        self.bestResponseUntouched = self.currentTxPower
        
        # initialize sense and transmit objects
        self.transmitObject = PlayerTransmitLayer(self, self.gameFreq)
        self.senseObject = PlayerSenseLayer(self, self.gameType)
        
        
        
    def isPrevTxDone(self):
        """Check if previous transmission has finished"""
        if self.transmitObject.isSendingData():
            self.transmitObject.sleepUntilSignalGenerationStops()
        return
    
    def setCost(self,newCost):
        self.cost=newCost
    
    def setInitialBestResponseUntouched(self):
        """Set best response as current tx power, best response untouched in [W]."""
        self.bestResponseUntouched = self.currentTxPower
    
    def setDirectGain(self, hii):
        """Set player direct gain"""
        self.directGain = hii
    
    def getPracticalBestResponseForm1(self, txPowerDBm, rxPowerDBm):
        """
        Compute best response strategy based current game state.
        Return best response power in dBm. Best response = 1/c_i + (I + n_0) / h_ii.
        I + n_0 = receivedPower - usefulReceivedPower
        
        Keyword arguments:
        txPowerDBm -- players' transmitting power.
        rxPowerDBm -- player received power.
        """
        
        # convert powers in W
        txPowerWatts = 1e-3 * math.pow(10.00, float(txPowerDBm) / 10.00)
        rxPowerWatts = 1e-3 * math.pow(10.00, float(rxPowerDBm) / 10.00)
        usefulReceivedPowerWatts = txPowerWatts * self.directGain
        
        if txPowerDBm < -1000:
            # Player does not transmit useful data, consider only noise and interference
            bestResponse = (1.00 / float(self.cost)) - rxPowerWatts / float(self.directGain)
        else:
            bestResponse = (1.00 / float(self.cost)) - (rxPowerWatts - usefulReceivedPowerWatts) / float(self.directGain)

        # Transform in dBm
        try:
            return 10.00 * math.log10(bestResponse / 1e-3) 
        except:
            print "Player %d: negative best response" % (self.playerObject.playerNumber)
            return None  
    
    def getPracticalBestResponseForm2(self, rxPowerDBm):
        """
        Compute best response strategy based current game state.
        Return best response power in dBm. This power is the best power in interference condition.
        This method use the practically formula which will be used in empirical games 
        This formula is based on the received power dBm, which must be only noise and interference
        """
        
        # convert received power in W
        rxPowerWatts = 1e-3 * math.pow(10.00, float(rxPowerDBm) / 10.00)
        bestResponse = (1.00 / float(self.cost)) - rxPowerWatts / float(self.directGain)
        
        # return in dBm
        try:
            return 10.00 * math.log10(bestResponse / 1e-3)
        except:
            print "Player %d: negative best response" % (self.playerObject.playerNumber)
            return None
        
    def computeBestResponseForm1(self, pj, hjiList):
        """
        Compute practical best response based on current tx power a list containing opponents tx 
        powers and a list containing cross gains h_ji for player i.
        Assume hjiList contains gains in [W].
        Do not consider noise!!!
        Return best response in [W]
        
        Keyword arguments:
        pj -- list with player j tx power, in bBm
        hjiList -- list with cross gains in [W] for player i.
        """
        # compute sum(h_ji*pJ)
        crossGainSum = 0
        # must transform each elem of pj in [W]
        temp = [math.pow(10.00, float(x) / 10.00) * 1e-3 for x in pj]
        for index, elem in enumerate(temp):
            crossGainSum += elem * hjiList[index]
        bestResp = (1.00 / float(self.cost) - crossGainSum / float(self.directGain))
        
        # return power in dBm
        try:
            # sometimes the difference is negative, in that case return none
            return 10.00 * math.log10(bestResp / 1.e-3)
        except:
            print "Player %d: negative best response" % (self.playerObject.playerNumber)
            return None
        
    def computeBestResponseForm2(self, receivedPower):
        """
        Compute practical best response based on received power and direct gain.
        Return best response in [W]
        
        Keyword arguments:
        receivedPower -- Measured receiving power, i.e. sum(h_ji * p_j) + n_0
        """
        powerInW = math.pow(10.00, float(receivedPower)/10.00) * 1e-3
        bestResp = (1.00 / float(self.cost) - powerInW/float(self.directGain))
        # return power in dBm
        try:
            # sometimes the difference is negative, in that case return none
            return 10.00 * math.log10(bestResp / 1.e-3)
        except:
            print "Player %d: negative best response" % (self.playerObject.playerNumber)
            return None
        
    def computeBestResponseForm3(self, recP):
        """
        Compute practical best response based on received power and direct gain.
        Return best response in [dBm]
        
        Keyword arguments:
        receivedPower -- Measured receiving power, i.e. sum(h_ji * p_j) + n_0
        """
        bestResp = (1.00 / float(self.cost) - recP/float(self.directGain))
        # return power in dBm
        try:
            # sometimes the difference is negative, in that case return none
            return 10.00 * math.log10(bestResp / 1.e-3)
        except:
            print "Player %d: negative best response" % (self.playerObject.playerNumber)
            return None

    def getAvailTxPower(self, desiredPower):
        """From the available power list get a transmission power. 
        Method will return the closest power from the available ones to the desired power.
        
        Keywords arguments:
        desiredPower -- Desired transmitting power. 
        """
        minDist = float("inf")
        rez = None
        
        for i in range(0, len(self.availableTxPowers)):
            if math.fabs(desiredPower - self.availableTxPowers[i]) < minDist:
                minDist = math.fabs(desiredPower - self.availableTxPowers[i])
                rez = self.availableTxPowers[i]
        
        return rez
    
    def getCrtTxPower(self):
        """Get current transmission power"""
        return self.currentTxPower
    
    def getBestRespUntouched(self):
        """Return best response as real value, not discrete one"""
        return self.bestResponseUntouched
    
    def changeTxPowerRandomly(self):
        """Change current tx power randomly"""
        self.currentTxPower = random.choice(self.availableTxPowers)
        self.previousTxPower = self.currentTxPower
        self.bestResponseUntouched = self.currentTxPower
    
    def changeTxPower(self, newBestResponse):
        """
        Change current tx power, save previous tx power
        
        Keyword arguments:
        newTxPower -- new transmitting power
        """
        self.previousTxPower = self.currentTxPower
        self.bestResponseUntouched = newBestResponse
        self.currentTxPower = self.getAvailTxPower(newBestResponse)
