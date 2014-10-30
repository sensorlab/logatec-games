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

class PlayerSenseLayer:
    """Responsible with transmission power allocation, i.e. spectrum sensing."""

    
    def __init__(self, physicalLayerObjectForSenseLayer, gameType):
        """
        Sense layer constructor
        
        Keyword arguments:
        gameType -- type of game played, i.e. how to compute the best response function
        """
        self.physicalLayer = physicalLayerObjectForSenseLayer
        self.gameType = gameType
    
    def printPlayerSenseLayerInfo(self):
        """Just print some info"""
        print "Sense layer associated to player %d" % (self.physicalLayer.playerObject.playerNumber)

    def quickSense(self):
        """
        Perform a quick spectrum sense.
        Return measured power in [dBm]
        """
        receivedPower = self.physicalLayer.rxNode.senseStartQuick()
        return receivedPower[1][0]
