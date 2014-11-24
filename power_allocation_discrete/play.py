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

import gameNode

from powerGame import PowerGame


# from games.myVersionOfPowerGame import gameNode

def main():
    coordId = gameNode.JSI
    plot_results = True
    # nodesUsed = [51, 52, 58, 59]
    # 3 players
    # nodesUsed = [51, 52, 56, 59, 58, 54]
    # 4 players
    nodesUsed = [51, 52, 56, 59, 54, 58, 57, 53]
    costs = [0.051, 0.051, 0.051, 0.051]
    freq = 2422e6
    playerIterationsThreshold = 40
    gameType = 5
    numberOfIndependentRuns = 1

    # dummyDirectGains = {0: 0.00157761071507, 1: 4.51845687856e-05}
    # dummyCrossGains = {0: {1: 1.80231466854e-05}, 1: {0: 2.33870171972e-05}}
    # caz instabil pt c_i = 0.051
    #dummyDirectGains = {0: 0.000169823673415, 1: 0.000042755567508}
    #dummyCrossGains = {0: {1: 4.475749475e-06}, 1: {0:6.426108043e-06}}

    dummyDirectGains = {0: 0.0009268290613003395, 1: 3.77518487745779e-06, 2: 0.00010864181762973266, 3: 0.0008317625408339001}
    dummyCrossGains = {0:{1: 8.629189815526171e-06, 2: 1.9860138212515864e-05, 3: 0.00010814277139495838}, 1: {0: 1.1528149943349e-06, 2: 1.588459852554849e-05, 3: 4.785576487266305e-06}, 2:{0: 2.7921211726230703e-06, 1: 8.184583907864356e-05, 3: 2.6459159576826786e-06}, 3:{0: 0.00017417959086096514, 1: 1.896643259824681e-05, 2: 0.0003206259020644263}}
    dummyTxPowers = {0: -8, 1: -8}
    powerGame = PowerGame(coordId, nodesUsed, costs, freq, gameType, playerIterationsThreshold, plot_results)
    powerGame.initPlayers()

    powerGame.measureGains()


    # powerGame.setGameDummyData(dummyDirectGains, dummyCrossGains, None)
    powerGame.playGame(numberOfIndependentRuns)
    #
    # measure h_ii and h_ji for each player
    # powerGame.setGameDummyData(dummyDirectGains, dummyCrossGains,dictTxPowers=dummyTxPowers)


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
