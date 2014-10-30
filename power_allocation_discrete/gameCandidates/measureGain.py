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
Created on Apr 30, 2014


Measure gain between two nodes

@author: m
'''
import math
from games.myVersionOfPowerGame import gameNode
from games.myVersionOfPowerGame.gainMeasurements import measureGainBetwTxRx
from games.myVersionOfPowerGame.gameNode import GameNode

def main():
    coordId = gameNode.JSI
    txId = 54
    rxId = 58
    txNode = GameNode(coordId, txId)
    rxNode = GameNode(coordId, rxId)
    gain = measureGainBetwTxRx(coordId, txNode, rxNode, 2422e6, txPower=0, transDuration=7)
    print gain
    if gain is not None:
        print "%.3f dB" % (10.00 * math.log10(gain))

if __name__ == '__main__':
    main()
