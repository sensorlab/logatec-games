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

import time
import math

class PlayerTransmitLayer:
    """
    The application part of a game player. It is responsible for signal generation.
    It uses a player and powerAllocation object.
    """

    # time when transmission starts [s]. A new signal is generated only when the old transmission stops.
    timeStartTx = 0

    # transmission duration [s]. How many seconds the player will transmit signal. Can change.
    transmissionDuration = 6

    # frequency used for transmitting signal [Hz]
    txFrequency = 2420e6

    # current transmission power [dBm]. Usually this is updated before transmitting data.
    currentTransmPower = 0.00

    def __init__(self, physicalLayerObjectForTxLayer, gameFrequency=2420e6):
        """
        Constructor for player application layer.

        Keyword arguments:
        playerObject -- Reference to player object. Used to get tx and rx nodes.
        gameFrequency -- Transmission frequency  (default 2420e6 Hz).
        """

        self.physicalLayer = physicalLayerObjectForTxLayer
        self.txFrequency = gameFrequency

    def printPlayerTxLayerInfo(self):
        """Just print player id and some info"""
        print "Transmission layer associated to player %d" % (self.physicalLayer.playerObject.playerNumber)

    def getTransmissionPower(self):
        """Return current transmission power"""
        return self.physicalLayer.currentTxPower

    def isSendingData(self):
        """Return True if player is transmitting data"""
        if time.time() - self.timeStartTx < self.transmissionDuration:
            return True
        else:
            return False

    def sleepUntilSignalGenerationStops(self):
        """Wait for previous transmission to stop."""
        if time.time() - self.timeStartTx < self.transmissionDuration:
            # wait for transmission to stop
            print "Player %d wait for %f seconds until previous transmission ends." % (self.physicalLayer.playerObject.playerNumber, math.ceil(self.transmissionDuration - (time.time() - self.timeStartTx)))
            time.sleep(math.ceil(self.transmissionDuration - (time.time() - self.timeStartTx)))
        return

    def sendData(self, txDuration):
        """Transmit data for a certain amount of time.

        Keyword arguments:
        txDuraiton -- transmission duration.
        """
        self.transmissionDuration = txDuration
        # wait for previous transmission to stop
        self.sleepUntilSignalGenerationStops()

        # get current tx power
        self.currentTransmPower = self.physicalLayer.getCrtTxPower()

        attempts = 0
        while True:
            try:
                self.physicalLayer.txNode.setGeneratorConfiguration(self.txFrequency, self.currentTransmPower)
                self.physicalLayer.txNode.generatorStart(time.time(), self.transmissionDuration)
                self.timeStartTx = time.time()
                print "Player %d is transmitting for %.3f seconds with %.d dBm.\n" % (self.physicalLayer.playerObject.playerNumber, self.transmissionDuration, self.currentTransmPower)
                break
            except:
                attempts += 1
                if attempts >= 10:
                    print "Player %d cannot transmit at current configuration, number of attempts %d.\n" % (self.physicalLayer.playerObject.playerNumber, attempts)
                    break
                print "Player %d failed to transmit at current configuration. Retry number %d.\n" % (self.physicalLayer.playerObject.playerNumber, attempts)
                continue
        return
