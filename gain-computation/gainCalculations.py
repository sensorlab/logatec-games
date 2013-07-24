from node import Node
from plot import Plot
from datetime import datetime as DateTime

import time
import math
import os
import datetime



class GainCalculations:
    
    @staticmethod
    def calculateInstantGain(coordinator_id,tx_node_id, rx_node_id):
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
        
        #We want to measure noise power, for that it is really important that we have no signal generated
        #first configure rx_node
        rx_node.setSenseConfiguration(freq_measurement, freq_measurement, 400e3)
        #start sensing
        try:
            rx_node.senseStart(time.time(), sensing_duration, 5)
        except Exception:
            print "Error"
            return
        
        #plot data just to see what is happening
        #Plot.plotResultsFromFile("./data/coor_%d/node_%d.dat" %(coordinator_id,rx_node.node_id), 0.0001)
        
        #now we have the measured results in a file, we have to read the file and do the average
        #data returned has the following structure: [[frequency], [average power in Watts for that frequency]]. Normally there is only one frequency
        noise_power = GainCalculations.getAverageDataMeasurmentsFromFile(coordinator_id ,rx_node.node_id)[1][0]
        
        #now we have to generate a signal and measure the received power
        #configure and start signal generation
        tx_node.setGeneratorConfiguration(freq_measurement, p_tx_measurement)
        tx_node.generatorStart(time.time(), transmitting_duration)
        
        #get current time
        start_gen_time = time.time()
        
        #sense the spectrum
        try:
            rx_node.senseStart(time.time(), sensing_duration, 5)
        except Exception:
            print "Error"
            return
        
        #plot data just to see what is happening
        #Plot.plotResultsFromFile("./data/coor_%d/node_%d.dat" %(coordinator_id,rx_node.node_id), 0.0001)
        
        #now we have in file data with the measurements
        received_power = GainCalculations.getAverageDataMeasurmentsFromFile(coordinator_id,rx_node.node_id)[1][0]
        
        print "Noise power: %.6f pW      Received power: %.6f pW" %(noise_power*1e12, received_power*1e12)
        
        #calculate gain
        gain = (received_power - noise_power) / (math.pow(10, p_tx_measurement/10.00) * 0.001)
        print "Gain between node %d and node %d: %.9f" %(tx_node.node_id, rx_node.node_id, gain)
        
        #write this gain in a file
        results_list = [gain, received_power, noise_power, math.pow(10, p_tx_measurement/10.00) * 0.001, datetime.datetime.now()]
        GainCalculations.printResultsInAFile(results_list, coordinator_id ,tx_node.node_id, rx_node.node_id)
        
        #wait until signal generation stops
        print "Time passed: %f" %(time.time() - start_gen_time)
        if (time.time() - start_gen_time < transmitting_duration):
            #that means we have to wait
            print "Sleep for %f" %(math.ceil(transmitting_duration - (time.time() - start_gen_time)))
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
            print "There is no average values available for this combination"
            return
        
        f = open(path, "r")
        
        #read first line, it's a header
        f.readline()
        
        s = 0.00
        
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
        
        # a list average_data: [[frequency], [average_power for that frequency]]. It will contain average power for one frequency
        average_data = [[],[]]
        
        #read the entire file
        while True:
            line = f.readline()
            if not line:
                break
            
            #line structure: [time, frequency_hz, power_dbm]
            #split line string (contains several numbers)
            line_list = line.split()
            #convert data_list elements to float
            line_list = GainCalculations.convertListElementsToFloat(line_list)
            
            try:
                #must see if this frequency exists in average_data
                if float(line_list[1]) not in average_data[0]:
                    #this frequency wasn't added in data_list yet 
                    average_data[0].append(float(line_list[1]))
                    #average_data must contain linear power
                    average_data[1].append(math.pow(10,float(line_list[2])/10.00) * 0.001)
                else:
                    #this frequency was already added in data_list
                    #do the average
                    #get the index in average_data for that frequency
                    index = average_data[0].index(float(line_list[1]))
                    average_data[1][index] = (average_data[1][index] + math.pow(10,float(line_list[2])/10.00) *0.001) / 2.00
            except Exception:
                #print Exception.message
                #may be a white line
                pass
        
        #close the file
        f.close()
        
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
            print "There is no average values available for this combination"
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
                gain_list[0].append(float(line_list[0]))
                gain_list[1].append(DateTime.strptime(  (line_list[4] + " " + line_list[5])[0:16], "%Y-%m-%d %H:%M"  ))
            except Exception:
                continue
            
        #plot results
        Plot.plot_x_y_date_lists(gain_list[1], gain_list[0], "Time", "Gain", "Gain between: tx%d and rx%d" %(tx_node_id, rx_node_id), False)
        #Plot.plot_list(gain_list[0], "Gain between: tx%d and rx%d" %(tx_node_id, rx_node_id), False)
        
def main():
    k = 10
    print GainCalculations.getAverageGain(10001, 2, 25)
    print GainCalculations.getAverageGain(10001, 17, 16)
    GainCalculations.plotGains(10001, 2, 25)
    GainCalculations.plotGains(10001, 17, 16)
    GainCalculations.plotGains(10001, 2, 16)
    GainCalculations.plotGains(10001, 17, 25)
    while k>50:
        GainCalculations.calculateInstantGain(10001, 2, 25)
        GainCalculations.calculateInstantGain(10001, 17, 16)
        GainCalculations.calculateInstantGain(10001, 2, 16)
        GainCalculations.calculateInstantGain(10001, 17, 25)
        time.sleep(30)
        k-=1
#main()
