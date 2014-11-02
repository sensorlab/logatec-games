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

Power allocation game implementation for LOG-a-TEC testbed.

Game type:
1 - game step for experiment 3
2 -
3 - multiple run experiments, measure sum(h_ji*p_j)+n_0 individually
4 - multiple run experiments, measure sum(h_ji*p_j)+n_0 when all opponents transmit
5 - dynamic game, i.e. players come and go

@version: 2.0
@author: mihai
"""

import time
import random
import copy
import math

from gamePlayer import GamePlayer
from livePlot import GameLivePlot
from gainMeasurements import measureGainBetwTxRx, \
    checkConvergenceRule, getDirectGainsNPlVers2, getCrossGainsNPlVers2, \
    checkConvergenceRuleTotalInterf
from utilStuff import writeListToFile, getFilePathWithDate


class PowerGame():
    """
    Power allocation game implementation.
    """

    # list of players playing the game
    players = list()

    # dictionary used to store players transmitting powers
    playersCrtTxPovers = dict()

    # store direct and cross gains
    directGains = dict()
    crossGains = dict()
    crossGainsTotalInterf = dict()

    # store equilibrium state for each player
    equilibrium = dict()
    playerEvent = dict()

    dummyDirectGains = dict()
    dummyCrossGains = dict()
    dummyCrossGainsTotalInterf = dict()
    dummyTxPowers = dict()
    useDummyData = False

    # used to avoid infinite loops
    playerIterationsThreshold = 0

    def __init__(self, coordinatorId, playerList, costList, gameFreq, gameType, playerItTh, plot_results=False):
        """
        Create a power game object

        Keyword arguments:
        coordinatorId -- Numerical cluster id.
        playerList -- List of node ids  representing players, e.g [51,23,31,47] two player game
                      with player 1 51->23 (tx node 51, rx node 23), player 2 31->47.
        costList -- List of player costs.
        gameFreq -- Frequency used for transmitting and sensing
        gameType -- Type of game played
        playerItTh: player iterations
        """
        self.coordId = coordinatorId
        self.nodesIdList = playerList
        self.playerCostList = costList
        self.gameFreq = gameFreq
        self.gameType = gameType
        self.playerIterationsThreshold = playerItTh
        self.plot_results = plot_results


        self.players = dict()
        self.equilibrium = dict()
        self.playersCrtTxPovers = dict()
        self.directGains = dict()
        self.crossGains = dict()
        self.crossGainsTotalInterf = dict()
        self.playerEvent = dict()
        self.useDummyData = False

        if self.plot_results:
            self.my_plot = GameLivePlot('Dynamic (cost adaptive) power allocation game')


    def initPlayers(self):
        """Just initialize player objects and check if parameters are ok"""
        self.nrPlayers = len(self.nodesIdList) / 2

        if self.nrPlayers != len(self.playerCostList):
            print "Number of players and costs given do not match!"
            return

        for i in range(0, len(self.nodesIdList), 2):
            self.players[i / 2] = GamePlayer(self.coordId, self.nodesIdList[i], self.nodesIdList[i + 1],
                                             self.playerCostList[i / 2], i / 2, self.gameFreq, self.gameType)
            # get initial tx powers, these powers are random choices from available powers
            self.playersCrtTxPovers[i / 2] = self.players[i / 2].physicalLayer.getCrtTxPower()
            self.equilibrium[i / 2] = False
            self.playerEvent[i / 2] = False

            # test if initialization was successful
            # INITIALIZATION WAS SUCCESFUL
            # for p in self.players:
            # p.physicalLayer.transmitObject.printPlayerTxLayerInfo()
            # p.physicalLayer.senseObject.printPlayerSenseLayerInfo()
            # PLAYERS CAN TRANSMIT
            # self.players[0].physicalLayer.transmitObject.sendData(4)

            # for i in self.playersCrtTxPovers.keys():
            # print "Player %d transmits with %d dBm"%(i,self.playersCrtTxPovers[i])

        # initi plot
        if self.plot_results:
            self.my_plot.init_plot(self.nrPlayers)


    def setGameDummyData(self, dDirectG, dCrossG, dCrossTotG, dictTxPowers=None):
        self.useDummyData = True
        self.dummyDirectGains = dDirectG
        self.dummyCrossGains = dCrossG
        self.dummyCrossGainsTotalInterf = dCrossTotG
        self.setDummiData(self.dummyDirectGains, self.dummyCrossGains, self.crossGainsTotalInterf)
        if dictTxPowers is not None:
            self.dummyTxPowers = dictTxPowers
            for key in dictTxPowers:
                self.playersCrtTxPovers[key] = dictTxPowers[key]
                self.players[key].physicalLayer.changeTxPower(dictTxPowers[key])

    def resetGame(self):
        """Use this when the game is played multiple times."""
        self.resetLogicalDictionary(self.playerEvent, False)
        self.resetLogicalDictionary(self.equilibrium, False)
        for playerId in self.players:
            self.players[playerId].resetPlayerObject()
            self.playersCrtTxPovers[playerId] = self.players[playerId].physicalLayer.getCrtTxPower()
        # need to measure gains and cross gains and scale player costs accordingly
        if self.useDummyData:
            # if self.gameType == 4:
            # self.dummyCrossGainsTotalInterf
            self.setDummiData(self.dummyDirectGains, self.dummyCrossGains, self.dummyCrossGainsTotalInterf)
            # adaugat doar pentru teste cu variatii
            # for key in self.directGains:
        # self.directGains[key] = self.directGains[key] + random.gauss(0,1)*1e-6
        # for key in self.crossGains:
        # for k in self.crossGains[key]:
        # self.crossGains[key][k] = self.crossGains[key][k] + random.gauss(0,1)*1e-6
        else:
            if self.gameType == 4:
                self.measureGainsV2()
            else:
                self.measureGains()
        self.scaleCosts()

    def measureGains(self):
        """Measure h_ii and h_ji between players, store these values in list and dictionary"""

        # txNodes = list()
        # rxNodes = list()

        txPlayers = list()
        rxPlayers = list()

        # measure direct gains
        for p in self.players:
            # get tx and rx nodes, used for cross gain
            txPlayers.append(self.players[p])
            rxPlayers.append(self.players[p])

            self.directGains[self.players[p].getPlayerNumber()] = measureGainBetwTxRx(self.coordId, self.players[
                p].physicalLayer.txNode, self.players[p].physicalLayer.rxNode, self.gameFreq, txPower=0,
                                                                                      transDuration=6)
            self.players[p].physicalLayer.setDirectGain(self.directGains[self.players[p].getPlayerNumber()])
            # wait for things to cool down
            time.sleep(2)

        # measure cross gains
        for p in self.players:
            result = dict()
            aux1 = txPlayers[:]
            aux1.remove(self.players[p])

            for n in aux1:
                result[n.getPlayerNumber()] = measureGainBetwTxRx(self.coordId, n.physicalLayer.txNode,
                                                                  self.players[p].physicalLayer.rxNode, self.gameFreq,
                                                                  txPower=0, transDuration=6)
                # wait for things to cool down
                time.sleep(2)
            # add cross gains to dictionary
            self.crossGains[p] = result

        print self.directGains
        for key in self.crossGains.keys():
            print self.crossGains[key]

    def measureGainsV2(self):
        """Measure h_ii and total h_ji between players, store these values in list and dictionary"""
        # txPlayers = list()
        # rxPlayers = list()
        vesnaNodes = list()
        # direct gains
        for p in self.players:
            # get tx and rx nodes for cross gain
            # txPlayers.append(self.players[p])
            #rxPlayers.append(self.players[p])
            vesnaNodes.append(self.players[p].physicalLayer.txNode)
            vesnaNodes.append(self.players[p].physicalLayer.rxNode)

        dirG = getDirectGainsNPlVers2(self.coordId, vesnaNodes)
        crG = getCrossGainsNPlVers2(self.coordId, vesnaNodes)

        index = 0
        for p in self.players:
            self.directGains[p] = dirG[index]
            self.players[p].physicalLayer.setDirectGain(dirG[index])
            self.crossGainsTotalInterf[p] = crG[index]
            index += 1

    def setDummiData(self, dummyDirect, dummyCross, dummyTotalCross=None, gameT=1):
        """Just set some old measured data and skip the measuring part"""
        self.directGains = dummyDirect
        if gameT == 4 and dummyTotalCross is not None:
            self.crossGainsTotalInterf = dummyTotalCross
        else:
            self.crossGains = dummyCross
        for key in dummyDirect:
            self.players[key].physicalLayer.setDirectGain(dummyDirect[key])
        if self.dummyTxPowers is not None:
            for key in self.dummyTxPowers:
                self.playersCrtTxPovers[key] = self.dummyTxPowers[key]
                self.players[key].physicalLayer.changeTxPower(self.dummyTxPowers[key])

    def scaleCosts(self):
        """
        Scale player cost such that best response is in interval [-30,0] dBm.
        Return True if operation is successful.
        """
        # check if c_i is in [0,1]
        for x in self.playerCostList:
            if x < 0.0 or x > 1.0:
                print "costs must be in interval [0,1]"
                print "c_i = %.2f" % (x)
                return False

        # scale costs based on direct and cross gains
        for plId in self.players:
            if self.gameType == 4:
                self.scaleCostForPlayerV2(plId)
            else:
                self.scaleCostForPlayer(plId)

        return True

    def scaleCostForPlayerWithMask(self, playerId, mask):
        mySum = 0
        for crossGj in self.crossGains[playerId]:
            if mask[crossGj]:
                mySum += self.crossGains[playerId][crossGj] * math.pow(10.00, float(
                    self.playersCrtTxPovers[crossGj]) / 10.00) * 1e-3
        omega = mySum / float(self.directGains[playerId])
        newCost = 1 / (float(1e-3 + omega)) + self.players[playerId].getPlayerCost() * (
            1 / (float(1e-6 + omega)) - 1 / (float(1e-3 + omega)))
        self.players[playerId].setScaledCost(newCost)

    def scaleCostForPlayer(self, playerId):
        """
        Scale player cost such that best response is in interval [-30,0] dBm.

        Keyword arguments:
        playerId -- numerical id identifying player.
        """
        mySum = 0
        for crossGj in self.crossGains[playerId]:
            mySum += self.crossGains[playerId][crossGj] * math.pow(10.00, float(
                self.playersCrtTxPovers[crossGj]) / 10.00) * 1e-3
        omega = mySum / float(self.directGains[playerId])
        newCost = 1 / (float(1e-3 + omega)) + self.players[playerId].getPlayerCost() * (
            1 / (float(1e-6 + omega)) - 1 / (float(1e-3 + omega)))
        self.players[playerId].setScaledCost(newCost)

    def scaleCostForPlayerV2(self, playerId):
        """
        Scale player cost such that best response is in interval [-30,0] dBm. Take into account measured cross gain.

        Keyword arguments:
        playerId -- numerical id identifying player.
        """
        omega = self.crossGainsTotalInterf[playerId] / float(self.directGains[playerId])
        newCost = 1 / (float(1e-3 + omega)) + self.players[playerId].getPlayerCost() * (
            1 / (float(1e-6 + omega)) - 1 / (float(1e-3 + omega)))
        self.players[playerId].setScaledCost(newCost)

    def isConvergent(self, restrictiveCond):
        """Check convergence rule"""
        if checkConvergenceRule(self.nrPlayers, self.directGains, self.crossGains, restrictiveCond):
            return True

        return False

    def areElemEqual(self, logicatDictionary, value=True):
        """
        Check if all elements of a dictionary, containing logical values, are equal

        logicalDicitonary -- python dictionary with logical values, True/False
        value -- logical value to compare with
        """
        for key in logicatDictionary:
            if logicatDictionary[key] != value:
                return False
        return True

    def resetLogicalDictionary(self, dictToReset, value=False):
        """
        Set all values of logical dictionary to False or True

        dictToReset -- python dictionary containing logical values True/False
        value -- set all elements of dictionary to this value
        """
        for key in dictToReset:
            dictToReset[key] = False

    def checkPowerEvent(self):
        """Check if someone has changed his transmitting power"""
        for key in self.playerEvent:
            if self.playerEvent[key]:
                return True
        return False

    def checkPowerEventWithMask(self, mask):
        """
        Check if someone has changed his transmitting power. Consider
        only the players for which mask is True.
        """
        for key in self.playerEvent:
            if self.playerEvent[key] and mask[key]:
                return True
        return False

    def isGameInEquilibrium(self):
        """Check to see if all players reached a stable state"""
        for key in self.equilibrium:
            if not self.equilibrium[key]:
                return False
        return True

    def generateRandomPowerEvent(self):
        """Choose a random player and change its transmitting power"""
        keyPl = random.choice(self.playerEvent.keys())
        # self.players[keyPl].generatePowerEvent()
        # self.playersCrtTxPovers[keyPl] = self.players[keyPl].physicalLayer.getCrtTxPower()
        self.playersCrtTxPovers[keyPl] = self.players[keyPl].generatePowerEvent()
        self.playerEvent[keyPl] = True

    def writeStatToFile(self, nrGameIterations, fileResults, multiRun=False, nrRun=0):
        """
        Write statistics to file.
        Write something like this:
        [run number - if multiple runs],game iterations, player number, player iteration, player cost, player scaled cost, player crt discrete tx power, player crt real tx power
        """
        for key in self.players:
            self.writePlayerStatToFile(key, nrGameIterations, fileResults, multiRun, nrRun)

    def writePlayerStatToFile(self, playerId, nrGameIterations, fileResults, multiRun=False, nrRun=0):
        """
        Write statistics to file for one player.
        Write something like this:
        [run number - if multiple runs],game iterations, player number, player iteration, player cost, player scaled cost, player crt discrete tx power, player crt real tx power
        """
        playerStats = [nrGameIterations, self.players[playerId].playerNumber, self.players[playerId].playerIterations,
                       self.players[playerId].cost, self.players[playerId].scaledCost,
                       self.players[playerId].physicalLayer.getCrtTxPower(),
                       self.players[playerId].physicalLayer.getBestRespUntouched()]
        if multiRun:
            playerStats.insert(0, nrRun)
        writeListToFile(fileResults, playerStats)

    def updatePlayersTxPowers(self, playerId, crtTxPower):
        """Just update the list with players current tx power"""
        self.playersCrtTxPovers[playerId] = crtTxPower

    def measureInterferenceForPlayerI(self, playerId):
        """
        Measure the received power level for player i.
        received power level = sum(h_ji * p_j) + n_0.

        Keyword arguments:
        playerId -- Numerical id for player that will measure power (sense spectrum)
        """
        transmissionTime = 7
        # configure transmitters
        for key in self.players:
            if key != playerId:
                self.players[key].physicalLayer.transmitObject.sendData(transmissionTime)
        # wait a second just to be sure that receiver senses the signal generated.
        time.sleep(0.5)
        # measure power
        receivedPower = self.players[playerId].physicalLayer.senseObject.quickSense()

        # wait for all transmissions to finish
        for key in self.players:
            if key != playerId:
                self.players[key].physicalLayer.transmitObject.sleepUntilSignalGenerationStops()

        return receivedPower

    def playGame(self, nrRuns):
        """
        Play the power allocation game, play the specified type of game

        Keyword arguments:
        number of independent games played.
        nrRuns -- number of independent games to be played.
        """
        if self.gameType == 1:
            filePathResults = getFilePathWithDate(self.coordId, 1)
            self.playGameType1(filePathResults)
        elif self.gameType == 2:
            filePathResults = getFilePathWithDate(self.coordId, 2)
            self.playGameType2(filePathResults)
        elif self.gameType == 3:
            filePathResults = getFilePathWithDate(self.coordId, 3, True)
            self.playGameType3(nrRuns, filePathResults)
        elif self.gameType == 11:
            filePathResults = getFilePathWithDate(self.coordId, 1, True)
            self.playGameType1MultiRun(nrRuns, filePathResults)
        elif self.gameType == 4:
            filePathResults = getFilePathWithDate(self.coordId, 4, True)
            self.playGameType4(nrRuns, filePathResults)
        elif self.gameType == 5:
            filePathResults = getFilePathWithDate(self.coordId, 5, False)
            self.playGameType5(filePathResults)
        else:
            print "Game type %d not implemented!!!" % (self.gameType)
            return

    def playGameType1(self, statFilePath, multipleRuns=False, run=0):
        """
        Game type 1:
        - gains are measured at the beginning and considered constant during the game
        - powerGame class keeps a record of each player transmitting power during each iteration
        - power game class keeps record of players that have reached equilibrium

        Keyword arguments:
        statFilePath -- path to file where statistics are saved.
        multipleRuns -- if True then save statistic in the same file, add run number in statistics file.
        run -- current independent run, consider this only for a multiple run game, i.e. multipleRuns = True
        """
        print "Game type 1 started"
        gameIterations = 0
        timeStartGame = time.time()
        oldPlayerPowerEvent = dict()

        # generate a power event, for a random player, in order to start the game
        self.generateRandomPowerEvent()
        # self.playerEvent[0] = True

        # just print initial state
        self.writeStatToFile(gameIterations, statFilePath, multipleRuns, run)

        # infinite loop
        while True:
            # stop the game if all players have reached a stable state, i.e. equilibrium
            if self.isGameInEquilibrium():
                print "Players have reached a stable state."
                break

            # check for power event
            if self.checkPowerEvent():
                gameIterations += 1
                print "Game iteration %d" % (gameIterations)
                # reset power event
                oldPlayerPowerEvent = copy.deepcopy(self.playerEvent)
                self.resetLogicalDictionary(self.playerEvent)

                if self.areElemEqual(oldPlayerPowerEvent, True):
                    # all players have changed strategy, all players must react and compute best response
                    self.resetLogicalDictionary(oldPlayerPowerEvent, False)

                for key in oldPlayerPowerEvent:
                    # compute best response for each player that did not changed their transmission power
                    if not oldPlayerPowerEvent[key]:
                        # check if the number of player iterations > some threshold (in this way avoid infinite
                        # loops, in some cases 3 strategies repeat with period 3-4 -> infinite loop)
                        if self.players[key].getNrPlayerIterations() > self.playerIterationsThreshold:
                            # compute strategy as average over last 5 strategies
                            self.players[key].updateTxPowerAsAverage()
                            self.equilibrium[key] = True
                        else:
                            self.scaleCostForPlayer(key)
                            self.playerEvent[key] = self.players[key].updateTxPower(self.playersCrtTxPovers,
                                                                                    self.crossGains[key])
                            # check if player has reached a stable state
                            self.equilibrium[key] = self.players[key].isInEquilibrium()
                        self.updatePlayersTxPowers(key, self.players[key].physicalLayer.getCrtTxPower())
                        # save statistics to file
                        self.writePlayerStatToFile(key, gameIterations, statFilePath, multipleRuns, run)
                    else:
                        # check if player has reached a stable state
                        self.equilibrium[key] = self.players[key].isInEquilibrium()
                        # if not oldPlayerPowerEvent[key]:
                        # self.scaleCostForPlayer(key)
                        # self.playerEvent[key] = self.players[key].updateTxPower(self.playersCrtTxPovers, self.crossGains[key])
                        # self.updatePlayersTxPowers(key, self.players[key].physicalLayer.getCrtTxPower())
                        # self.writePlayerStatToFile(key, gameIterations, statFilePath, multipleRuns, run)
                        #                     self.equilibrium[key] = self.players[key].isInEquilibrium()
            else:
                # check if all players reached a stable state, i.e. in equilibrium
                if not self.isGameInEquilibrium():
                    # game has not reached a stable state
                    for key in self.playerEvent: self.playerEvent[key] = True
                else:
                    # all players in equilibrium, stop the game
                    print "Players have reached a stable state."
                    break
        print "Game type 1 finished in %d steps (1 step = players react to another player event) and %.3f seconds." % (
            gameIterations, time.time() - timeStartGame)
        print "For two players 10 steps = each player makes 5 moves."

    def playGameType1MultiRun(self, nrRuns, statFilePath):
        """
        Game type 1, run the game multiple times:
        - gains are measured at the beginning and considered constant during the game
        - powerGame class keeps a record of each player transmitting power during each iteration
        - power game class keeps record of players that have reached equilibrium

        Keyword arguments:
        nrRuns -- number of independent games played.
        statFilePath -- path to file where statistics are saved.
        """
        for crtRun in range(nrRuns):
            print "Crt run: %d" % (crtRun)
            if crtRun > 0:
                self.resetGame()
            self.playGameType1(statFilePath, True, crtRun)
        print "Finish!! :)(:"

    def playGameType2(self, statFilePath):
        """
        Live version of the game. Gains are measured when each player changes its transmitting power.
        - gains are measured at the beginning of the game
        - cross gains are measured for each player when he wants to update power tx level
        - powerGame class keeps a record of each player transmitting power during each iteration
        - power game class keeps record of players that have reached equilibrium

        Keyword argumetns:
        statFilePath -- path to file where statistics are saved.
        """
        iterations = 0
        timeStartGame = time.time()
        print "Game type 1 started"

        oldPlayerPowerEvent = dict()

        # generate a power event, for a random player, in order to start the game
        self.generateRandomPowerEvent()

        # just print initial state
        self.writeStatToFile(iterations, statFilePath)

        # infinite loop
        while True:
            # stop the game if all players have reached a stable state, i.e. equilibrium
            if self.isGameInEquilibrium():
                print "Players have reached a stable state."
                break

            # check for an event
            if self.checkPowerEvent():
                iterations += 1
                print "Iteration %d" % (iterations)
                # reset power event
                oldPlayerPowerEvent = copy.deepcopy(self.playerEvent)
                self.resetLogicalDictionary(self.playerEvent)

                if self.areElemEqual(oldPlayerPowerEvent, True):
                    # all players have changed strategy, all players must react and compute best response
                    self.resetLogicalDictionary(oldPlayerPowerEvent, False)

                for key in oldPlayerPowerEvent:
                    # compute best response for each player that did not changed their transmission power
                    # these players will generate a power event
                    if not oldPlayerPowerEvent[key]:
                        # measure cross gains and noise for player
                        measuredPower = self.measureInterferenceForPlayerI(key)
                        self.playerEvent[key] = self.players[key].updateTxPower1(measuredPower)
                        # scale costs based on direct and cross gains
                        self.scaleCostForPlayer(key)

                    # check if player has reached a stable state
                    self.equilibrium[key] = self.players[key].isInEquilibrium()
                # save stats to file
                self.writeStatToFile(iterations, statFilePath)

            else:
                # check if all players reached a stable state, i.e. in equilibrium
                if not self.isGameInEquilibrium():
                    # game has not reached a stable state
                    for key in self.playerEvent:
                        self.playerEvent[key] = True
                else:
                    # all players in equilibrium, stop the game
                    print "Players have reached a stable state."
                    break
        print "Game type 1 finished in %d steps (1 step = players react to another player event) and %.3f seconds." % (
            iterations, time.time() - timeStartGame)
        print "For two players 10 steps = each player makes 5 moves."

    def playGameType3(self, nrRuns, statFile):
        """
        Game Type 1, run the game multiple times and do a sweep for costs
        - find the cost influence on the results: vary cost in [0,1], for each cost do the experiment nrRuns times
        - costs are adapted dynamically during the game
        - gains are measured at the beginning and considered constant during the game
        - powerGame class keeps a record of each player transmitting power during each iteration
        - power game class keeps record of players that have reached equilibrium
        - measure gains at the beginning of each run

        Keyword arguments:
        nrRuns -- number of independent games played.
        statFile -- path to file where statistics are saved.
        """
        step = 0.05
        crtCost = 0.0
        # TODO: need to check convergence rule after each gain measurement
        for crtCostRun in range(int(1 / step)):
            print "Current Cost run: %d." % (crtCostRun)
            # do specified nr of independent runs for given cost
            for key in self.players:
                # all players have the same cost
                self.players[key].setPlayerCost(crtCost)
            # must measure gains for first run and scale costs according to current situation
            self.useDummyData = True

            self.resetGame()
            # use this measured gains for the nrRuns runs
            # self.dummyDirectGains = copy.deepcopy(self.directGains)
            # self.dummyCrossGains = copy.deepcopy(self.crossGains)
            # self.useDummyData = True
            for crtRun in range(nrRuns):
                print "Current run: %d" % (crtRun)
                if crtRun > 0:
                    self.resetGame()
                # play the game
                self.playGameType1(statFile, True, crtRun)
            # increment costs
            crtCost += step
        print "Finish! :)(:"

    def playGameStep(self, statFilePath, multipleRuns=False, run=0):
        """
        Game step:
        - gains are measured at the beginning and considered constant during the game
        - powerGame class keeps a record of each player transmitting power during each iteration
        - power game class keeps record of players that have reached equilibrium

        Keyword arguments:
        statFilePath -- path to file where statistics are saved.
        multipleRuns -- if True then save statistic in the same file, add run number in statistics file.
        run -- current independent run, consider this only for a multiple run game, i.e. multipleRuns = True
        """
        gameIterations = 0
        timeStartGame = time.time()
        oldPlayerPowerEvent = dict()
        # generate a power event, for a random player, in order to start the game
        self.generateRandomPowerEvent()
        # just print initial state
        self.writeStatToFile(gameIterations, statFilePath, multipleRuns, run)
        # infinite loop
        measureP = False
        while True:
            # stop the game if all players have reached a stable state, i.e. equilibrium
            if self.isGameInEquilibrium():
                print "Players have reached a stable state."
                break
            # check for power event
            if self.checkPowerEvent():
                gameIterations += 1
                print "Game iteration %d" % (gameIterations)

                if measureP and self.useDummyData == False:
                    self.measureGainsV2()

                # reset power event
                oldPlayerPowerEvent = copy.deepcopy(self.playerEvent)
                self.resetLogicalDictionary(self.playerEvent)

                if self.areElemEqual(oldPlayerPowerEvent, True):
                    # all players have changed strategy, all players must react and compute best response
                    self.resetLogicalDictionary(oldPlayerPowerEvent, False)

                for key in oldPlayerPowerEvent:
                    # compute best response for each player that did not changed their transmission power
                    if not oldPlayerPowerEvent[key]:
                        # check if the number of player iterations > some threshold (in this way avoid infinite
                        # loops, in some cases 3 strategies repeat with period 3-4 -> infinite loop)
                        if self.players[key].getNrPlayerIterations() > self.playerIterationsThreshold:
                            # compute strategy as average over last 5 strategies
                            self.players[key].updateTxPowerAsAverage()
                            self.equilibrium[key] = True
                        else:
                            # daca se depasesc 5 iteratii -> mai fac o masuratoare
                            if self.players[key].getNrPlayerIterations() % 5 == 0 and self.players[
                                key].getNrPlayerIterations() > 4:
                                measureP = True

                            self.scaleCostForPlayerV2(key)
                            self.playerEvent[key] = self.players[key].updateTxPower2(self.crossGainsTotalInterf[key])
                            # check if player has reached a stable state
                            self.equilibrium[key] = self.players[key].isInEquilibrium()
                        self.updatePlayersTxPowers(key, self.players[key].physicalLayer.getCrtTxPower())
                        # save statistics to file
                        self.writePlayerStatToFile(key, gameIterations, statFilePath, multipleRuns, run)
                    else:
                        # check if player has reached a stable state
                        self.equilibrium[key] = self.players[key].isInEquilibrium()
            else:
                # check if all players reached a stable state, i.e. in equilibrium
                if not self.isGameInEquilibrium():
                    # game has not reached a stable state
                    for key in self.playerEvent: self.playerEvent[key] = True
                else:
                    # all players in equilibrium, stop the game
                    print "Players have reached a stable state."
                    break
        print "Game type 1 finished in %d steps (1 step = players react to another player event) and %.3f seconds." % (
            gameIterations, time.time() - timeStartGame)
        print "For two players 10 steps = each player makes 5 moves."


    def playGameType4(self, nrRuns, statFile):
        """
        Game Type 1, run the game multiple times and do a sweep for costs
        - find the cost influence on the results: vary cost in [0,1], for each cost do the experiment nrRuns times
        - costs are adapted dynamically during the game
        - gains are measured at the beginning and each 5 player iterations
        - powerGame class keeps a record of each player transmitting power during each iteration
        - power game class keeps record of players that have reached equilibrium
        - measure gains at the beginning of each run

        Keyword arguments:
        nrRuns -- number of independent games played.
        statFile -- path to file where statistics are saved.
        """
        self.measureGainsV2()
        if checkConvergenceRuleTotalInterf(self.nrPlayers, self.directGains, self.crossGainsTotalInterf, False):
            print "Game is convergent"
            print "h_ii ", self.directGains
            print "h_ji ", self.crossGainsTotalInterf
        else:
            print "Topology not convergent"

        step = 0.05
        crtCost = 0.0
        for crtCostRun in range(int(1 / step)):
            print "Current Cost run: %d." % (crtCostRun)
            for key in self.players:
                self.players[key].setPlayerCost(crtCost)
            if crtCostRun > 0:
                self.useDummyData = True
                self.resetGame()
                # if crtCostRun > 0:
                # first set of measurements form convergence condition
            # self.useDummyData=False
            # self.resetGame()
            self.dummyDirectGains = copy.deepcopy(self.directGains)
            self.dummyCrossGainsTotalInterf = copy.deepcopy(self.crossGainsTotalInterf)
            self.useDummyData = True
            for crtRun in range(nrRuns):
                print "Current run: %d" % (crtRun)
                if crtRun > 0:
                    self.resetGame()
                # play the game
                self.playGameStep(statFile, True, crtRun)
            crtCost += step
        print "Finish! :)(:"

    def playGameType5(self, statFilePath):
        """Dynamic game, i.e. players come and go. All 4 players must play initially."""
        print "Game type 5 started."

        # self.measureGains()

        gameIterations = 0
        oldPlayerPowerEvent = dict()
        # used to determine which player plays the power allocation game
        mask = dict()
        chei = list()
        step_tx_powers = list()
        for key in self.players:
            self.players[key].setPlayerCost(self.playerCostList[key])
            mask[key] = True
            chei.append(key)
            step_tx_powers.append(0)
        self.generateRandomPowerEvent()
        self.writeStatToFile(gameIterations, statFilePath)

        if self.plot_results:
            for key in chei:
                step_tx_powers[key] = self.players[key].physicalLayer.getCrtTxPower()
            self.my_plot.plot_tx_powers(step_tx_powers)


        while True:
            if gameIterations == 12:
                print "stop"
            if gameIterations == 50:
                break
            elif gameIterations == 13:
                mask[3] = False
                self.resetLogicalDictionary(self.playerEvent, False)
                self.playerEvent[0] = True
            elif gameIterations == 26:
                mask[3] = True
                self.resetLogicalDictionary(self.playerEvent, False)
                self.playerEvent[3] = True
            elif gameIterations == 39:
                mask[3] = False
                mask[2] = False
                self.resetLogicalDictionary(self.playerEvent, False)
                self.playerEvent[1] = True
            if self.checkPowerEventWithMask(mask):
                gameIterations += 1
                oldPlayerPowerEvent = copy.deepcopy(self.playerEvent)
                self.resetLogicalDictionary(self.playerEvent, False)

                for key in oldPlayerPowerEvent:
                    if not oldPlayerPowerEvent[key] and mask[key]:
                        if self.players[key].getNrPlayerIterations() > self.playerIterationsThreshold:
                            self.players[key].updateTxPowerAsAverage()
                            self.equilibrium[key] = True
                        else:
                            self.scaleCostForPlayerWithMask(key, mask)
                            self.playerEvent[key] = self.players[key].updateTxPowerWithMask(self.playersCrtTxPovers,
                                                                                            self.crossGains[key], mask)
                            # check if player has reached a stable state
                            self.equilibrium[key] = self.players[key].isInEquilibrium()
                        self.updatePlayersTxPowers(key, self.players[key].physicalLayer.getCrtTxPower())
                    else:
                        # check if player has reached a stable state
                        self.equilibrium[key] = self.players[key].isInEquilibrium()

                # if required create plot
                if self.plot_results:
                    for i in chei:
                        if mask[i]:
                            step_tx_powers[i] = self.players[i].physicalLayer.getCrtTxPower()
                        else:
                            step_tx_powers[i] = 0
                    self.my_plot.plot_tx_powers(step_tx_powers)

            self.writeStatToFile(gameIterations, statFilePath)

