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

@author: m
'''
from games.myVersionOfPowerGame.powerGame import PowerGame
from games.myVersionOfPowerGame import gameNode

def main():
    coordId = gameNode.JSI
    nodesUsed = [51, 52, 56, 59]
    # 3 players
    #nodesUsed = [51, 52, 56, 59, 58, 54]
    # 4 players
    #nodesUsed = [51, 52, 56, 59, 54, 58, 57, 53]
    costs = [0.051, 0.051]
    freq = 2422e6
    playerIterationsThreshold = 40
    gameType = 3
    numberOfIndependentRuns = 20
    
#     dummyDirectGains = {0: 0.0007345132269475385, 1: 5.063783578829797e-05}
#     dummyCrossGains = {0: {1: 5.186798124854993e-06}, 1: {0:2.0839321031212163e-07}}
    # caz instabil pt c_i = 0.051
    dummyDirectGains = {0: 0.000169823673415, 1: 0.000042755567508}
    dummyCrossGains = {0: {1: 4.475749475e-06}, 1: {0:6.426108043e-06}}
    dummyTxPowers = {0:-8, 1:-8}
    powerGame = PowerGame(coordId, nodesUsed, costs, freq, gameType, playerIterationsThreshold)
    powerGame.initPlayers()
    
    powerGame.playGame(numberOfIndependentRuns)
    
    # measure h_ii and h_ji for each player
    # powerGame.setGameDummyData(dummyDirectGains, dummyCrossGains,dictTxPowers=dummyTxPowers)
#     powerGame.measureGains()
    
    # scale costs
#     try:
#         powerGame.scaleCosts()
#     except:
#         print "Error when scaling costs"
#         return
#     if not powerGame.scaleCosts(costs):
#         print "Erorr when scaling costs"
#         return
    
#     if powerGame.isConvergent(False):
#         print "Node topology satisfies convergence rule"
#         powerGame.playGame(numberOfIndependentRuns)
#     else:
#         print "bad topology"
#         return
    


if __name__ == '__main__':
    main()
