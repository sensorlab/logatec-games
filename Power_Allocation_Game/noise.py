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
            
        