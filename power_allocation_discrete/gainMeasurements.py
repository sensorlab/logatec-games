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
Contains several methods which can be used for channel gain measurements between VESNA nodes.

@version: 1.4
@author: mihai
"""

import time
import math


def checkConvergenceRule(nrPlayers, dictDirectGains, dictCrossGains, restrictive=False):
    """
    Check power allocation game convergence rule

    Keyword arguments:
    nrPlayers -- number of players playing the power allocation game.
    dictDirectGains -- dictionary containing direct gains for each player, dictionary keys represent player id.
    dictCrossGains -- dictionary containing  cross gains for each player, cross gains are stored for each player in a dictionary.
                     e.g. cross={player_id:{opponent_id:h_ji,opponent_id:h_ji},...}
                     {1:{2:h_21,3:h_31},2:{1:h_12,3:h_32},3:{1:h_13,2:h_23}}
    restrictive -- if True then check that each h_ji/h_ii<1/N
    """
    if len(dictDirectGains.keys()) != len(dictCrossGains.keys()):
        print "Something is wrong, nr of direct gains and cross gains do not match. (%d != %d)" % (
            len(dictDirectGains.keys()), len(dictCrossGains.keys()))
        return False

    if restrictive:
        # compute restrictive version of convergence rule
        b = 1 / float(nrPlayers)
        for i in dictDirectGains.keys():
            for j in dictCrossGains[i]:
                if (dictCrossGains[i][j] / float(dictDirectGains[i])) >= b:
                    print "System is not convergent: h_ji/h_ii = %.3f >= %.3f" % (
                        dictCrossGains[i][j] / float(dictDirectGains[i]), b)
                    return False
    else:
        # compute relaxed version of convergence rule
        b = 1 / float(nrPlayers - 1)
        # get average cross gain
        for i in dictDirectGains.keys():
            mySum = 0
            for j in dictCrossGains[i]:
                mySum += float(dictCrossGains[i][j])
            averCrossG = mySum / float(len(dictCrossGains[i]))
            if (averCrossG / float(dictDirectGains[i])) >= b:
                print "System is not convergent, according to relaxed convergence rule: average(h_ji)/h_ii = %.3f >= %.3f" % (
                    averCrossG / float(dictDirectGains[i]), b)
                return False

    return True


def checkConvergenceRuleTotalInterf(nrPlayers, dictDirectGains, dictCrossGains, restrictive=False):
    """
    Check power allocation game convergence rule

    Keyword arguments:
    nrPlayers -- number of players playing the power allocation game.
    dictDirectGains -- dictionary containing direct gains for each player, dictionary keys represent player id.
    dictCrossGains -- dictionary containing  total measured cross gains for each player
    restrictive -- if True then check that each h_ji/h_ii<1/N
    """
    if len(dictDirectGains.keys()) != len(dictCrossGains.keys()):
        print "Something is wrong, nr of direct gains and cross gains do not match. (%d != %d)" % (
            len(dictDirectGains.keys()), len(dictCrossGains.keys()))
        return False

    if restrictive:
        # compute restrictive version of convergence rule
        b = 1 / float(nrPlayers)
        for i in dictDirectGains.keys():
            if (dictCrossGains[i] / float(dictDirectGains[i])) >= b:
                print "System is not convergent: h_ji/h_ii = %.3f >= %.3f" % (
                    dictCrossGains[i] / float(dictDirectGains[i]), b)
                return False
    else:
        # compute relaxed version of convergence rule
        b = 1 / float(nrPlayers - 1)
        # get average cross gain
        for i in dictDirectGains.keys():
            if (dictCrossGains[i] / float(dictDirectGains[i])) >= b:
                print "System is not convergent: h_ji/h_ii = %.3f >= %.3f" % (
                    dictCrossGains[i] / float(dictDirectGains[i]), b)
                return False

    return True


def checkConvergenceRuleForSearch(nrPlayers, listDirectGains, listCrossGains, restrictive=False):
    """
    Check power allocation game convergence rule

    Keyword arguments:
    nrPlayers -- number of players playing the power allocation game.
    listDirectGains -- list containing direct gains for each player.
    listCrossGains -- list containing  cross gains for each player, cross gains measures as: all tx
                    node transmit and rx receives.
    restrictive -- if True then check that each h_ji/h_ii<1/N
    """
    if len(listDirectGains) != len(listCrossGains):
        print "Something is wrong, nr of direct gains and cross gains do not match. (%d != %d)" % (
            len(listDirectGains), len(listCrossGains))
        return False

    if restrictive:
        # compute restrictive version of convergence rule
        b = 1 / float(nrPlayers)
    else:
        b = 1 / float(nrPlayers - 1)

    for index, elem in enumerate(listDirectGains):
        if (listCrossGains[index] / float(elem) >= b):
            print "System is not convergent: h_ji/h_ii = %.3f >= %.3f" % (listCrossGains[index] / float(elem), b)
            return False

    return True


def getDirectGainsNPl(coordinatorId, nodeObjectsUsed):
    """
    Computes direct gains h_{ii} between nodes in list. List contains node objects for players.
    Return list: [h_{i1}, h_{i2}, ..., h_{in}].
    Method can return errors or invalid measurements if noise power is greater than measured gain

    coordinatorId -- Numerical id for cluster coordinator.
    nodeObjectsUsed -- Vesna node objects for players. ex. nodesObjectsUsed = [1, 2, 3, 4] -> 2 player game,
                player1 tx=1 and rx=2, player2 tx=3 and rx=4
    """
    result = list()
    # Repeat experiment if I get a bad measurement - noise is greater than received power
    for i in range(0, len(nodeObjectsUsed), 2):
        measuredGain = measureGainBetwTxRx(coordinatorId, nodeObjectsUsed[i], nodeObjectsUsed[i + 1], measuringFreq=2422e6)
        result.append(measuredGain)
        if measuredGain is None:
            print "bad measurement between nodes %d and %d" % (
                nodeObjectsUsed[i].getNodeID(), nodeObjectsUsed[i + 1].getNodeID())
            return
        print "wait 15s for things to cool down"
        time.sleep(15)
    return result


def getDirectGainsNPlVers2(coordinatorId, nodeObjectsUsed, waitingTime=5):
    """
    Computes direct gains h_{ii} between nodes in list. List contains node objects for players.
    Return list: [h_{i1}, h_{i2}, ..., h_{in}].
    Method can return errors or invalid measurements if noise power is greater than measured gain

    coordinatorId -- Numerical id for cluster coordinator.
    nodeObjectsUsed -- Vesna node objects for players. ex. nodesObjectsUsed = [1, 2, 3, 4] -> 2 player game,
                player1 tx=1 and rx=2, player2 tx=3 and rx=4
    waitingTime -- time between 2 measurements.
    """
    result = list()
    for i in range(0, len(nodeObjectsUsed), 2):
        attempts = 0
        while attempts < 3:
            measuredGain = measureGainBetwTxRx(coordinatorId, nodeObjectsUsed[i], nodeObjectsUsed[i + 1],
                                               measuringFreq=2422e6)
            if measuredGain is None:
                attempts += 1
            else:
                attempts = 10
        result.append(measuredGain)
        if measuredGain is None:
            print "bad measurement between nodes %d and %d" % (
                nodeObjectsUsed[i].getNodeID(), nodeObjectsUsed[i + 1].getNodeID())
            return
        print "wait %ds for things to cool down" % (waitingTime)
        time.sleep(waitingTime)
    return result


def getCrossGains2Pl(coordinatorId, nodeObjectsUsed):
    """
    Compute cross gains h_{ji} for a two player game. Result list will contain [h_{21}, h_{12}].
    Method can return errors or invalid measurements if noise power is greater than measured gain.

    coordinatorId -- Numerical id for cluster coordinator.
    nodeObjectsUsed -- Vesna node objects for players. ex. nodesObjectsUsed = [1, 2, 3, 4] -> 2 player game,
                player1 tx=1 and rx=2, player2 tx=3 and rx=4
    """
    result = list()
    result.append(measureGainBetwTxRx(coordinatorId, nodeObjectsUsed[2], nodeObjectsUsed[1], measuringFreq=2422e6))
    print "wait 15s for things to cool down"
    time.sleep(15)
    result.append(measureGainBetwTxRx(coordinatorId, nodeObjectsUsed[0], nodeObjectsUsed[3], measuringFreq=2422e6))
    print "wait 5s for things to cool down"
    time.sleep(5)
    return result


def getCrossGains2PlVers2(coordinatorId, nodeObjectsUsed, waitingTime=5):
    """
    Compute cross gains h_{ji} for a two player game. Result list will contain [h_{21}, h_{12}].
    Method can return errors or invalid measurements if noise power is greater than measured gain.

    coordinatorId -- Numerical id for cluster coordinator.
    nodeObjectsUsed -- Vesna node objects for players. ex. nodesObjectsUsed = [1, 2, 3, 4] -> 2 player game,
                player1 tx=1 and rx=2, player2 tx=3 and rx=4
    waitingTime -- time between 2 measurements.
    """
    result = list()
    attempts = 0
    while attempts < 3:
        power = measureGainBetwTxRx(coordinatorId, nodeObjectsUsed[2], nodeObjectsUsed[1], measuringFreq=2422e6)
        if result[0] is None:
            attempts += 1
        else:
            attempts = 10
    result.append(power)
    print "wait %ds for things to cool down" % (waitingTime)
    time.sleep(waitingTime)

    attempts = 0
    while attempts < 3:
        power = measureGainBetwTxRx(coordinatorId, nodeObjectsUsed[0], nodeObjectsUsed[3], measuringFreq=2422e6)
        if result[0] is None:
            attempts += 1
        else:
            attempts = 10
    result.append(power)
    print "wait %ds for things to cool down" % (waitingTime)
    time.sleep(waitingTime)
    return result


def getCrossGainsNPl(coordinatorId, nodeObjectsUsed):
    """
    Compute cross gains h_{ji} for a n player game. Result list will contain [h_{j1}, h_{j2}, ..., h_{jn}].
    When computing h_{ji} nodes transmitting are all others j nodes where i!=j
    Method can return errors or invalid measurements if noise power is greater than measured gain.

    coordinatorId -- Numerical id for cluster coordinator.
    nodeObjectsUsed -- Vesna node objects for players. ex. nodesObjectsUsed = [1, 2, 3, 4] -> 2 player game,
                player1 tx=1 and rx=2, player2 tx=3 and rx=4
    """
    result = list()
    # get tx and rx nodes for each case
    txNodes = list()
    rxNodes = list()
    for i in range(0, len(nodeObjectsUsed), 2):
        txNodes.append(nodeObjectsUsed[i])
        rxNodes.append(nodeObjectsUsed[i + 1])

    for index, i in enumerate(txNodes):
        aux = txNodes[:]
        aux.remove(i)
        rez = measureGainBetwNTxAnd1Rx(coordinatorId, aux, rxNodes[index], measuringFreq=2422e6)
        result.append(rez)
        print "wait 10s for things to cool down"
        time.sleep(10)

    return result


def getCrossGainsNPlVers2(coordinatorId, nodeObjectsUsed, waitingTime=5):
    """
    Compute cross gains h_{ji} for a n player game. Result list will contain [h_{j1}, h_{j2}, ..., h_{jn}].
    When computing h_{ji} nodes transmitting are all others j nodes where i!=j
    Method can return errors or invalid measurements if noise power is greater than measured gain.

    coordinatorId -- Numerical id for cluster coordinator.
    nodeObjectsUsed -- Vesna node objects for players. ex. nodesObjectsUsed = [1, 2, 3, 4] -> 2 player game,
                player1 tx=1 and rx=2, player2 tx=3 and rx=4
    waitingTime -- time between 2 measurements.
    """
    result = list()
    # get tx and rx nodes for each case
    txNodes = list()
    rxNodes = list()
    for i in range(0, len(nodeObjectsUsed), 2):
        txNodes.append(nodeObjectsUsed[i])
        rxNodes.append(nodeObjectsUsed[i + 1])

    for index, i in enumerate(txNodes):
        aux = txNodes[:]
        aux.remove(i)
        attempts = 0
        while attempts < 3:
            rez = measureGainBetwNTxAnd1Rx(coordinatorId, aux, rxNodes[index], measuringFreq=2422e6)
            if rez is None:
                attempts += 1
            else:
                attempts = 10
        result.append(rez)
        print "wait %ds for things to cool down" % (waitingTime)
        time.sleep(waitingTime)

    return result


def measureGainBetwTxRx(coordinatorId, txNode, rxNode, measuringFreq, txPower=0, transDuration=10):
    """
    Measure h_ii between tx and rx node.

    :rtype : int
    Keyword arguments:
    txNode -- GameNode object used for transmitting data.
    rxNode -- GameNode object used for receiving data.
    measuringFreq -- Frequency at which to measure the gain.
    txPower -- transmission power at which the measurement is done.
    transmittingDuration -- transmission duration of the generated signal, taking into account programming times this must be at least 6 seconds.
    """

    waitFor = 1
    sensingDuration = 2

    rxNodeId = rxNode.getNodeID()
    rxNode.setSenseConfiguration(measuringFreq, measuringFreq, 400e3)

    # measure channel noise
    attempts = 0
    while True:
        try:
            """ start sensing
            Observation: Computer clock is not synchronized with the node clock. This is a reason why we choose to start the sensing
            only after a few seconds, otherwise the are cases when node report that "Start time cannot be in the past"
            """
            rxNode.senseStart(time.time() + waitFor, sensingDuration, 5)
            # if everything is fine, break this loop
            break
        except:
            if attempts < 3:
                attempts += 1
                print "Channel noise computation %d: Noise measurement error, retry %d" % (rxNodeId, attempts)
                continue
            else:
                print "Channel noise computation %d: Noise measurement error, return nothing" % (rxNodeId)
                return
    noisePower = getAveragedDataMeasurementsFromFile(coordinatorId, rxNodeId)[1][0]

    # wait 2 seconds for things to cool down
    time.sleep(2)

    # get current time. I want to know when I started the signal generation
    startGenTime = time.time()

    # generate signal and measure received power
    try:
        txNode.setGeneratorConfiguration(measuringFreq, txPower)
        txNode.generatorStart(time.time(), transDuration)
    # txNode.geteratorStart(time.time(), transDuration)
    except:
        print "Gain computation between %d and %d :  Error at generator. Return" % (txNode.getNodeID(), rxNodeId)
        return

    # wait a second just to be sure that receiver senses the signal generated.
    # (With this we take into account other delays that can appear in testbed)
    time.sleep(0.5)

    # sense the spectrum
    attempts = 0
    while True:
        try:
            # start sense after timeAfter seconds from now
            rxNode.senseStart(time.time() + waitFor, sensingDuration, 5)
            # if everything is fine, break this loop
            break;
        except Exception:
            # try a few more times if something went wrong
            if attempts < 2:
                attempts += 1
                print "Compute gain between %d and %d : Receive power measurement error, retry %d" % (
                    txNode.getNodeID(), rxNodeId, attempts)
                continue
            else:
                print "Compute gain between %d and %d : Receive power measurement error, return nothing" % (
                    txNode.getNodeID(), rxNodeId)
                """anyway, at this point there is a signal generated, so I don't want to affect other measurements,
                so we have to wait until signal generation stops
                """
                sleepUntilSignalGenerationStops(startGenTime, transDuration)
                return

    receivedPower = getAveragedDataMeasurementsFromFile(coordinatorId, rxNodeId)[1][0]
    print "Gain computation between tx_%d and rx_%d: Noise power-%.6fE-12, Received power-%.6fE-12" % (
        txNode.getNodeID(), rxNodeId, noisePower * 1e12, receivedPower * 1e12)

    # compute gain
    gain = (receivedPower - noisePower) / (math.pow(10.00, txPower / 10.00) * 0.001)
    if gain < 0:
        # something is wrong, no signal was generated?
        print "Gain computation between %d and %d: Bad measurement!!! noise power is bigger than received_power, omit this measurement" % (
            txNode.getNodeID(), rxNodeId)
        # wait for the signal generation stops
        sleepUntilSignalGenerationStops(startGenTime, transDuration)
        return None

    try:
        print "Gain between node %d and node %d: %.9fE-6  ( %.6f dB)" % (
            txNode.getNodeID(), rxNodeId, gain * 1e6, 10.00 * math.log10(gain))
    except Exception:
        print "Exception when computing log10 from gain, gain is -%.6fE-12" % gain


    # wait until signal generation stops
    sleepUntilSignalGenerationStops(startGenTime, transDuration)

    # wait for things to cool down
    time.sleep(2)

    return gain


def measureGainBetwNTxAnd1Rx(coordinatorId, txNodes, rxNode, measuringFreq, txPower=0, transDuration=10):
    """Measure the instant channel gain between tx nodes given in txNodesIds list and rxNodeId within the coordinatorId
    Compute gain as: Gain_between_i_and_j = (Power received by j - Power noise)/(Power transmitted by i)

    coordinatorId -- Numerical cluster id.
    txNodeIds -- List of vesna transmitting nodes objects.
    rxNodeId -- Receiver nodes objects.
    measuringFreq -- Frequency at which to measure the gain.
    saveResults -- save the results ( append ) in a file or just get instant gain without saving the results.
    transmittingDuration -- transmission duration of the generated signal, taking into account programming times this must be at least 6 seconds.
    """
    waitFor = 1
    sensingDuration = 2

    rxNodeId = rxNode.getNodeID()
    strTxNodes = ','.join(str(x.getNodeID()) for x in txNodes)

    # measure channel noise
    rxNode.setSenseConfiguration(measuringFreq, measuringFreq, 400e3)

    # measure channel noise
    attempts = 0
    while True:
        try:
            """ start sensing
            Observation: Computer clock is not synchronized with the node clock. This is a reason why we choose to start the sensing
            only after a few seconds, otherwise the are cases when node report that "Start time cannot be in the past"
            """
            rxNode.senseStart(time.time() + waitFor, sensingDuration, 5)
            # if everything is fine, break this loop
            break
        except:
            if attempts < 3:
                attempts += 1
                print "Channel noise computation %d: Noise measurement error, retry %d" % (rxNodeId, attempts)
                continue
            else:
                print "Channel noise computation %d: Noise measurement error, return nothing" % (rxNodeId)
                return
    noisePower = getAveragedDataMeasurementsFromFile(coordinatorId, rxNodeId)[1][0]

    # wait 2 seconds for things to cool down
    time.sleep(2)

    # get current time. I want to know when I started the signal generation
    startGenTime = time.time()

    # start transmitting
    try:
        for node in txNodes:
            node.setGeneratorConfiguration(measuringFreq, txPower)
            node.generatorStart(time.time(), transDuration)
    except:
        print "Gain computation between tx nodes %s and %d:  Error at generator. Return" % (strTxNodes, rxNodeId)
        return
    time.sleep(0.5)

    # sense the spectrum
    attempts = 0
    while True:
        try:
            # start sense after timeAfter seconds from now
            rxNode.senseStart(time.time() + waitFor, sensingDuration, 5)
            # if everything is fine, break this loop
            break;
        except Exception:
            # try a few more times if something went wrong
            if attempts < 2:
                attempts += 1
                print "Compute gain between %s and %d : Receive power measurement error, retry %d" % (
                    strTxNodes, rxNodeId, attempts)
                continue
            else:
                print "Compute gain between %s and %d : Receive power measurement error, return nothing" % (
                    strTxNodes, rxNodeId)
                """anyway, at this point there is a signal generated, so I don't want to affect other measurements,
                so we have to wait until signal generation stops
                """
                sleepUntilSignalGenerationStops(startGenTime, transDuration)
                return

    receivedPower = getAveragedDataMeasurementsFromFile(coordinatorId, rxNodeId)[1][0]
    print "Gain computation between tx nodes %s and rx_%d: Noise power-%.6fE-12, Received power-%.6fE-12" % (
        strTxNodes, rxNodeId, noisePower * 1e12, receivedPower * 1e12)

    # compute gain
    gain = (receivedPower - noisePower) / (math.pow(10.00, txPower / 10.00) * 0.001)
    if gain < 0:
        # something is wrong, no signal was generated?
        print "Gain computation between tx nodes %s and %d: Bad measurement!!! noise power is bigger than received_power, omit this measurement" % (
            strTxNodes, rxNodeId)
        # wait for the signal generation stops
        sleepUntilSignalGenerationStops(startGenTime, transDuration)
        return None

    try:
        print "Gain between tx nodes %s and node %d: %.9fE-6  ( %.6f dB)" % (
            strTxNodes, rxNodeId, gain * 1e6, 10.00 * math.log10(gain))
    except Exception:
        print "Exception when computing log10 from gain, gain is -%.6fE-12" % gain

    # wait until signal generation stops
    sleepUntilSignalGenerationStops(startGenTime, transDuration)

    # wait for things to cool down
    time.sleep(2)

    return gain


def getAveragedDataMeasurementsFromFile(coordinatorId, nodeId):
    """When we do the sensing, all data is saved in a .dat file. For the same frequency, we can have multiple samples of RSSI.
    Reads the data from file, average power at every frequency and returns a list with the following structure:
    [[frequency] , [average_power for one specific frequency]], average power returned is linear [ W ]

    coordinatorId -- Numerical cluster id.
    nodeId -- Node id.
    """

    # open the file for reading
    f = open("./data/coor_%d/node_%d.dat" % (coordinatorId, nodeId), "r")

    # read first line, it's a header
    f.readline()

    # make data list with the following structure: [ [frequency]  ,[ [ list of all powers for that frequency] ] ]
    # An example of data_list:  [[freq1, freq2] , [[RSSI1, RSSI2, RSSI3], [RSSI1, RSSI2] ]]
    data_list = [[], []]

    # read the entire file
    while True:
        # read current line. It's a string at this step
        line = f.readline()
        if not line:
            break

        # convert line read to floats
        line_list = convertListElementsToFloat(line.split())
        try:
            # check if this frequency was added in data_list
            if line_list[1] not in data_list[0]:
                # then, we have a new frequency which has to be added in data_list
                data_list[0].append(line_list[1])
                data_list[1].append([math.pow(10.00, line_list[2] / 10.00) * 1e-3])
            else:
                # this frequency was added in data_list
                # get index for that that frequency
                index = data_list[0].index(line_list[1])
                data_list[1][index].append(math.pow(10.00, line_list[2] / 10.00) * 1e-3)
        except:
            continue

        # close the file
        f.close()
        """I want a list of average_data: [[frequency], [average_power for that frequency]].
        It will contain average power for several certain frequencies
        """
        average_data = [[], []]
        for i in range(0, len(data_list[0])):
            average_data[0].append(data_list[0][i])
            average_data[1].append(math.fsum(data_list[1][i]) / len(data_list[1][i]))

        return average_data


def convertListElementsToFloat(stringList):
    """use this when you have a list with string numbers and you want to convert the list elements to float numbers.
    Return list_to_be_converted with float elements.
    Raises exception if something is wrong
    """
    try:
        return [float(x) for x in stringList]
    except Exception:
        print Exception.message
        return None


def sleepUntilSignalGenerationStops(start_gen_time, transmitting_duration):
    """Use this just when you generated a signal and you want to wait until generated signal is over.
    generally this method is used by other methods inside this class
    print "Time passed: %f" %(time.time() - start_gen_time)
    """
    if ((time.time() - start_gen_time) < transmitting_duration):
        # that means we have to wait
        print "Sleep for %f until signal generation stops" % (
            math.ceil(transmitting_duration - (time.time() - start_gen_time)))
        time.sleep(math.ceil(transmitting_duration - (time.time() - start_gen_time)))
    return
