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
Created on Mar 12, 2014

Configuring VESNA nodes for generating signal, and spectrum sensing. Class has helper methods used for testing nodes.
Based on: https://github.com/sensorlab/logatec-games/tree/master/Power_Allocation_Game

@version: 2.0
@author: mihai
"""

import logging
import time
import os

from vesna import alh
from vesna.alh.spectrumsensor import SpectrumSensor, SpectrumSensorProgram
from vesna.alh.signalgenerator import SignalGenerator, TxConfig, SignalGeneratorProgram
from vesna.spectrumsensor import SweepConfig

INDUSTRIAL_ZONE = 10001
CITY_CENTER = 10002
JSI = 9501

class GameNode:

    # transmitting and receiving configurations
    sweepConfig = None
    txConfig = None
    # reference to sensor and generator objects
    sensorNode = None
    generatorNode = None


    def __init__(self, coordinatorId, nodeId, showLog=True):
        """node constructor

        Keywords arguments:
        coordinatorId -- Numerical cluster id.
        nodeId -- id number of node.
        """

        # get coordinator object
        self.coordinator = alh.ALHWeb("https://crn.log-a-tec.eu/communicator", coordinatorId)
        # get node object
        self.node = alh.ALHProxy(self.coordinator, nodeId)
        # save Ids
        self.coordinatorId = coordinatorId
        self.nodeId = nodeId

        if showLog:
            logging.basicConfig(level=logging.INFO)

    def nodeTest(self):
        """Print a string if node is active"""
        print self.node.get("sensor/mcuTemp")

    def coordinatorTest(self):
        """Print a string if coordinator is active"""
        print self.coordinator.get("hello")

    def getNodeID(self):
        return self.nodeId

    def getSenseConfig(self):
        """just get a configuration list so I can see it"""
        SpectrumSensor(self).get_config_list()

    def getGeneratorConfig(self):
        """just get a configuration list so I can see it"""
        SignalGenerator(self).get_config_list()

    def setSenseConfiguration(self, startFreqHz, endFreqHz, stepFerqHz):
        """Set sensing configuration.
        Measure the power in frequency band [startFrewHz, endFreqHz] with a predefined step.

        startFreqHz -- Lower bound of the frequency band to check (inclusive)
        endFreqHz -- Upper bound of the frequency band to check (inclusive)
        stepFerqHz -- Frequency step
        """
        self.sensorNode = SpectrumSensor(self.node)
        sensorConfigList = self.sensorNode.get_config_list()
        self.sweepConfig = sensorConfigList.get_sweep_config(startFreqHz, endFreqHz, stepFerqHz)

        if self.sweepConfig is None:
            raise Exception("Something went wrong with the sweepConfig. sweepConfig is None")

    def setSenseConfigurationChannel(self, startCh, endCh, stepCh):
        """Set sensing configuration.
        Measure the power from start_ch to stop_ch with predefined step

        startCh -- Lowest frequency channel to sweep
        endCh -- One past the highest frequency channel to sweep
        stepCh -- How many channels in a step
        """
        self.sensorNode = SpectrumSensor(self.node)
        sensorConfigList = self.sensorNode.get_config_list()
        self.sweepConfig = SweepConfig(sensorConfigList.get_config(0, 0), startCh, endCh, stepCh)

        if self.sweepConfig is None:
            raise Exception("Something went wrong with the sweepConfig. sweepConfig is None")

    def setSenseConfigurationFuulSweep(self):
        """Set sensing configuration.
        This method will sense the entire band that device supports.
        """
        self.sensorNode = SpectrumSensor(self.node)
        sensorConfigList = self.sensorNode.get_config_list()
#         self.sweepConfig = SpectrumSensor(self.node).get_config_list().get_config(0,0).get_full_sweep_config()
        self.sweepConfig = sensorConfigList.get_config(0, 0).get_full_sweep_config()
        if self.sweepConfig is None:
            raise Exception("Something went wrong with the sweepConfig. sweepConfig is None")

    def senseStart(self, timeStart, timeDuration, slotID):
        """Start spectrum sensing on node with predefined configuration (self.sweep_config).
        May perform a few frequency sweeps, depends on the time duration.
        If sweepConfig is None raise exception.

        timeStart -- Time to start the task (UNIX timestamp).
        timeDuration -- Duration of the task in seconds.
        slotID -- Numerical slot id used for storing measurements.
        """
        if self.sweepConfig is None:
            print "Cannot start Sensing. Configuration is missing!!"
            return None

        # get program object
        program = SpectrumSensorProgram(self.sweepConfig, timeStart, timeDuration, slotID)

        # get sensor object and program the node
        self.sensorNode.program(program)

        # wait for sensor to finish the job
        while not self.sensorNode.is_complete(program):
            print "waiting..."
            time.sleep(1)

            if time.time() > (program.time_start + program.time_duration + 60):
                raise Exception("Something went wrong when sensing")

        print "Sensing finished, retrieving data."
        result = self.sensorNode.retrieve(program);

        # for simplicity save data in a folder
        try:
            os.mkdir("./data")
        except OSError:
            pass
        try:
            os.mkdir("./data/coor_%d" % (self.coordinatorId))
        except OSError:
            pass

        # write data, overwrite existing file
        result.write("./data/coor_%d/node_%d.dat" % (self.coordinatorId, self.nodeId))

    def senseStartQuick(self):
        """returns a list : [[frequencies] , [power_dbm]]
        Starts spectrum sensing on node with predefined configuration (self.sweepConfig).
        This method will do a quick step. Use this if time is critical!
        Bandwidth you can measure in this case is limited.
        This will perform a single frequency step with the sweep method defined in the SpectrumSensor class.

        If sweepConfig is None raise exception.
        """
        if self.sweepConfig is None:
            print "Cannot start Sensing. Configuration is missing!!"
            return None

        sweep = SpectrumSensor(self.node).sweep(self.sweepConfig)

        # get frequency list
        fHz = self.sweepConfig.get_hz_list()

        dataReceived = []
        dataReceived.append(fHz)
        dataReceived.append(sweep.data)

        return dataReceived

    def setGeneratorConfiguration(self, fHz, powerDBm):
        """Set configuration for signal generation.

        fHz -- Frequency to generate.
        powerDBm -- Transmission power.
        """
        self.generatorNode = SignalGenerator(self.node)
        generatorConfigList = self.generatorNode.get_config_list()
        self.txConfig = generatorConfigList.get_tx_config(fHz, powerDBm)

        if self.txConfig is None:
            raise Exception("Something went wrong with configuration, txConfig is None.")

    def setGeneratorConfigurationChannel(self, fCh, powerDBm):
        """Set configuration for signal generation.

        fHz -- Frequency to generate.
        powerDBm -- Transmission power.
        """
        self.generatorNode = SignalGenerator(self.node)
        generatorConfigList = self.generatorNode.get_config_list()
        self.txConfig = TxConfig(generatorConfigList.get_config(0, 0), fCh, powerDBm)

        if self.txConfig is None:
            raise Exception("Something went wrong with configuration, txConfig is None.")

    def generatorStart(self, timeStart, timeDuration):
        """Start signal generation with predefined configuration (txConfig).
        If txConfig is None raise exception.

        timeStart -- Time when node starts transmitting.
        timeDuration -- Time for which node is transmitting.
        """
        if self.txConfig is None:
            print "Cannot start signal generating, configuration is missing"
            return None

        # get a program object
        program = SignalGeneratorProgram(self.txConfig, timeStart, timeDuration)
        self.generatorNode.program(program)
