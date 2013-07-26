from node import Node
from plot import Plot
from datetime import datetime as DateTime

import time
import math
import os
import datetime



class GainCalculations:
    
    @staticmethod
    def calculateInstantGain(coordinator_id,tx_node_id, rx_node_id, freq_measurement):
        #define two Node objects
        tx_node = Node(coordinator_id, tx_node_id)
        rx_node = Node(coordinator_id, rx_node_id)
        
        #a few measurement parameters
        #frequency measurement [hz]
        freq_measurement = 2420e6
        #transmitting power for measurement [dBm]
        p_tx_measurement = 0
        #transmitting duration [s]. For how much time will the generator generate a signal
        transmitting_duration = 10
        #sensing duration [s] . For how much time will the node sense the spectrum
        sensing_duration = 2
        
        #now measure the noise power, for that it is really important that we have no signal generated
        try:
            #configure rx_node
            rx_node.setSenseConfiguration(freq_measurement, freq_measurement, 400e3)
            #start sensing
            rx_node.senseStart(time.time()+1, sensing_duration, 5)
        except Exception:
            print "Calculate gain between %d and %d : Noise measurement error, return" %(tx_node_id, rx_node_id) 
            return
        
        #plot data just to see what is happening
        #Plot.plotResultsFromFile("./data/coor_%d/node_%d.dat" %(coordinator_id,rx_node.node_id), 0.0001)
        
        #now we have the measured results in a file, we have to read the file and do the average
        #data returned has the following structure: [[frequency], [average power in Watts for that frequency]]. Normally there is only one frequency
        noise_power = GainCalculations.getAverageDataMeasurmentsFromFile(coordinator_id ,rx_node.node_id)[1][0]
        
        #now we have to generate a signal and measure the received power
        #configure and start signal generation
        try:
            tx_node.setGeneratorConfiguration(freq_measurement, p_tx_measurement)
            tx_node.generatorStart(time.time(), transmitting_duration)
        except:
            print "Calculate gain between %d and %d :  Error at generator." %(tx_node_id, rx_node_id) 
            return
        
        #get current time
        start_gen_time = time.time()
        
        #sense the spectrum
        try:
            rx_node.senseStart(time.time()+1, sensing_duration, 5)
        except Exception:
            print "Calculate gain between %d and %d : Receive power measurement error, return" %(tx_node_id, rx_node_id) 
            return
        
        #plot data just to see what is happening
        #Plot.plotResultsFromFile("./data/node_%d.dat" %(rx_node.node_id), 0.0001)
        
        #now we have in file data with the measurements
        received_power = GainCalculations.getAverageDataMeasurmentsFromFile(coordinator_id,rx_node.node_id)[1][0]
        
        print "Noise power: %.6f pW      Received power: %.6f pW" %(noise_power*1e12, received_power*1e12)
        
        #calculate gain
        gain = (received_power - noise_power) / (math.pow(10, p_tx_measurement/10.00) * 0.001)
        if gain<0:
            print "Calculate gain between %d and %d : Bad measurement, noise power is bigger than received_power, omit this measurement" %(tx_node_id, rx_node_id) 
            return
        print "Gain between node %d and node %d: %.9f e-6  ( %.6f db)" %(tx_node.node_id, rx_node.node_id, gain *1e6, 10*math.log10(gain))
        
        #write this gain in a file
        results_list = [gain, received_power, noise_power, math.pow(10, p_tx_measurement/10.00) * 0.001, datetime.datetime.now()]
        GainCalculations.printResultsInAFile(results_list, coordinator_id ,tx_node.node_id, rx_node.node_id)
        
        #wait until signal generation stops
        print "Time passed: %f" %(time.time() - start_gen_time)
        if (time.time() - start_gen_time < transmitting_duration):
            #that means we have to wait
            print "Sleep for %f until signal generation stops" %(math.ceil(transmitting_duration - (time.time() - start_gen_time)))
            time.sleep(math.ceil(transmitting_duration - (time.time() - start_gen_time)))
        
        return gain
    
    @staticmethod    
    def convertListElementsToFloat(list_to_be_converted):
        #return list_to_be_converted with float elements
        #conversion can generate exceptions
        try:
            for i in range(0, len(list_to_be_converted)):
                list_to_be_converted[i] = float(list_to_be_converted[i])
            #return converted_list
            return list_to_be_converted
        except Exception:
            print Exception.message
            return None
        
       
    @staticmethod
    def getAverageGain(coordinator_id ,tx_node_id, rx_node_id):
        #read from file (if it exists) and average all values from file
        
        #first, check if the file exists
        path = "./gain measurements/coor_%d/gain_between_tx_%d_and_rx_%d.dat" %(coordinator_id ,tx_node_id,  rx_node_id)
        if not os.path.isfile(path) and not os.path.exists(path):
            print "There is no average values available for this combination. Trying with gain_between_tx_%d_and_rx_%d.dat" %(rx_node_id, tx_node_id)
            path = "./gain measurements/coor_%d/gain_between_tx_%d_and_rx_%d.dat" %(coordinator_id ,rx_node_id, tx_node_id)
            if not os.path.isfile(path) and not os.path.exists(path):
                print "There is no average values available for this combination."
                return
        
        
        f = open(path, "r")
        
        #read first line, it's a header
        f.readline()
        
        #initialize sum with 0
        s = 0.00
        
        #k will represent the number of values 
        k = 0
        while True:
            line = f.readline()
            if not line:
                break
            
            #line list: [gain , received_power[w] , noise_power[w], transmitted_power[w], date ]
            line_list = line.split()
            try:
                s = s + float(line_list[0])
                k+=1
            except Exception:
                continue
            
        f.close()
        return s/k;
    
    @staticmethod
    def getAverageDataMeasurmentsFromFile(coordinator_id ,node_id):
        #reads the data from file, average power at every frequency
        #returns a list with the following structure: [[frequency] , [average_power for one specific frequency]]
        #average power returned is linear [ W ]
        #open the file for reading
        f = open("./data/coor_%d/node_%d.dat" %(coordinator_id ,node_id) , "r")
        
        #read first line, it's a header
        f.readline()
        
        #data_list [[frequency]  ,[ [ list of all powers for that frequency]  ]]
        #an example of data_list:  [[freq1, freq2] , [[p1, p2, p3], [p1, p2] ]]
        data_list = [[], []]
        
        #read the entire file
        while True:
            #read current line. It's a string at this step
            line = f.readline()
            if not line:
                break
            
            #line structure: "time   frequency_hz   power_dbm"
            #split line string (contains several numbers)
            line_list = line.split()
            #at this step, line_split is something like that: ['123',  '2340e6' , '-90']
            
            #convert data_list elements to float
            line_list = GainCalculations.convertListElementsToFloat(line_list)
            #now , line_List : [123,  2340e6, -90]
            
            try:
                #check if this frequency was added in data_list
                if line_list[1] not in data_list[0]:
                    #then, we have a new frequency which has to be added in data_list
                    data_list[0].append(float(line_list[1]))
                    data_list[1].append([ math.pow(10.00, float(line_list[2])/10.00)*1e-3 ])
                else:
                    #this frequency was added in data_list
                    #get index for that that frequency
                    index = data_list[0].index(float(line_list[1]))
                    data_list[1][index].append(math.pow(10.00, float(line_list[2])/10.00)*1e-3)
            except:
                continue
                
        #close the file
        f.close()
        
        # a list average_data: [[frequency], [average_power for that frequency]]. It will contain average power for one frequency
        average_data = [[],[]]
        for i in range(0, len(data_list[0])):
            average_data[0].append(data_list[0][i])
            average_data[1].append( math.fsum(data_list[1][i])/len(data_list[1][i]))
            
        return average_data
    
    @staticmethod
    def printResultsInAFile(results_list, coordinator_id, tx_node_id, rx_node_id):
        #appends results_list in a file. The results_list contains : [gain , received_power[w] , noise_power[w], transmitted_power[w], date ]
        
        #check if the folder exits. If not then create it
        #try to make a folder
        try:
            os.mkdir("./gain measurements")
        except OSError:
            pass
        
        #try to make a folder
        try:
            os.mkdir("./gain measurements/coor_%d" %coordinator_id)
        except OSError:
            pass
            
        #open file
        #first see if the file exits
        path = "./gain measurements/coor_%d/gain_between_tx_%d_and_rx_%d.dat" %(coordinator_id ,tx_node_id,  rx_node_id)
        if not os.path.isfile(path) and not os.path.exists(path):
            #if the file doesn't exits, then create it
            print "Writing a new file"
            f = open(path, "w")
            f.write("[Gain]                [Received power ]           [Noise power]            [Transmitted power]            [Date]     - all power units in watts\n")
            f.close()
        
        #append new data to file
        f = open(path, "a")
        
        for element in results_list:
            f.write(str(element))
            f.write("        ")
        f.write("\n")
        f.close()
        
    @staticmethod
    def plotGains(coordinator_id ,tx_node_id, rx_node_id):
        #open file and plot results from it
        
        #first, check if the file exists
        path = "./gain measurements/coor_%d/gain_between_tx_%d_and_rx_%d.dat" %(coordinator_id ,tx_node_id,  rx_node_id)
        if not os.path.isfile(path) and not os.path.exists(path):
            print "There is no measurement values available for this combination"
            return
   
        print "Plot gains"
        f = open("./gain measurements/coor_%d/gain_between_tx_%d_and_rx_%d.dat" %(coordinator_id ,tx_node_id,  rx_node_id), "r")
        
        #read first line, it's a header
        f.readline()
        
        #define a gain_list : [[gain], [date]]
        gain_list = [[],[]]
        
        
        while True:
            line = f.readline()
        
            if not line:
                break
                
            #line has the following structure: [gain , received_power[w] , noise_power[w], transmitted_power[w], date ]
            #split line
            line_list = line.split()
            
            #append gain and date to gain_list
            try:
                #2013-07-22 10:10:54.466393
                #in file gains are in linear value, it more comfortable to display in logarithmic scale        
                gain_list[0].append(10 * math.log10(float(line_list[0])))
                gain_list[1].append(DateTime.strptime(  (line_list[4] + " " + line_list[5])[0:16], "%Y-%m-%d %H:%M"  ))
            except Exception:
                continue
            
        #plot results
        Plot.plot_x_y_date_lists(gain_list[1], gain_list[0], "Time", "Gain [dB]", "Gain between: tx%d and rx%d" %(tx_node_id, rx_node_id), False)
        #Plot.plot_list(gain_list[0], "Gain between: tx%d and rx%d" %(tx_node_id, rx_node_id), False)
    
    @staticmethod
    def plotAllGainsWithinCoordinator(coordinator_id):
        path = "gain measurements/coor_%d" %coordinator_id
        
        for i in os.listdir(path):
            tx_node_id = i[ (i.index("tx_") +3) : (i.index("_and"))]
            rx_node_id = i[ (i.index("rx_") +3):  (i.index(".dat"))]
            GainCalculations.plotGains(coordinator_id, int(tx_node_id), int(rx_node_id))