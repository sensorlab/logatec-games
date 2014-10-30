# Copyright (C) 2013 SensorLab, Jozef Stefan Institute
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

# Authors: Ciprian Anton
# 		Andrei Toma
#


from node import Node
from gainCalculations import GainCalculations

import time

class Noise:
    #use this class if you want to measure the noise power
    
    @staticmethod
    def getInstantNoise(coordinator_id, node_id ,freq=2420e6):
        #return current noise measured at the specified node
        
        #define a Node object
        rx_node = Node(coordinator_id, node_id)
        
        #for how much time we will measure the spectrum
        sensing_duration = 2
        
        try:
            #configure node
            rx_node.setSenseConfiguration(freq, freq, 400e3)
            #start sensing
            rx_node.senseStart(time.time()+1, sensing_duration, 5)
        except Exception:
            print "Error at sensing start"
            return
        
        #now we have the measured results in a file, we have to read the file and do the average
        #data returned has the following structure: [[frequency], [average power in Watts for that frequency]]. Normally there is only one frequency
        noise_power = GainCalculations.getAverageDataMeasurementsFromFile(coordinator_id ,rx_node.node_id)[1][0]
        print "Noise power %.6fE-12" %(noise_power * 1e12)
        return noise_power
            
        