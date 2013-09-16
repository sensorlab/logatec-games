from node import Node
from plot import Plot
from datetime import datetime as DateTime
from myQueue import MyQueue
import kalmanImplementation
import time
import math
import os
import datetime

class GainCalculations:
    #contains several static methods which can be used for channel gain measurements between the VESNA nodes
    #you can either use the measured channel gains saved in .dat files or perform new measurements
    
    @staticmethod
    def calculateInstantGain(coordinator_id,tx_node_id, rx_node_id, measuring_freq = 2420e6, saveresults = True , transmitting_duration = 10):
        #this method measures the instant channel gain between tx_node_id and rx_node_id within the coordinator_id
        #calculate gain as the following: Gain_between_i_and_j = (Power received by j - Power noise)/(Power transmitted by i)
        #you can specify the frequency at which you want to measure the gain
        #you can save the results ( append ) in a file or you can just get instant gain without saving the results
        #you can specify transmitting_duration of the generated signal. Taking into account the programming times I recommend using at least 6 seconds
        
        #define two Node objects
        tx_node = Node(coordinator_id, tx_node_id)
        rx_node = Node(coordinator_id, rx_node_id)
        
        #a few measurement parameters
        #transmitting power [dBm]
        p_tx_dBm = 0
        
        #transmitting duration [s]. For how long will the generator generate a signal. This parameter is given in the method parameters
        
        #sensing duration [s] . For how much time will the node sense the spectrum.
        sensing_duration = 2
        
        #specify when to start the sensing (after 1-2 seconds). Note: the packet which I send to the node, includes a time (when to transmit), but, there takes some time until packet arrives at node.
        time_after = 1.5
        
        #First we want to measure the noise power, for that it is really important that no signal is generated
        attempts = 0
        while True:
            try:
                #configure rx_node
                rx_node.setSenseConfiguration(measuring_freq, measuring_freq, 400e3)
                #start sensing
                rx_node.senseStart(time.time()+time_after, sensing_duration, 5)
                #Observation: Computer clock is not synchronized with the node clock. This is a reason why we choose to start the sensing only after a few seconds, otherwise the are cases when node report that "Start time cannot be in the past"
                
                #if everything is fine, break this loop
                break
            except:
                if attempts<3:
                    attempts+=1
                    print "Calculate gain between %d and %d: Noise measurement error, retry %d" %(tx_node_id, rx_node_id, attempts) 
                    continue
                else:
                    print "Calculate gain between %d and %d: Noise measurement error, return nothing" %(tx_node_id, rx_node_id) 
                    return
                    
        #now we have the measured results in a file, we have to read the file and do the average.
        #data returned has the following structure: [[frequency], [average power in W for that frequency]]. Normally there is only one frequency because we've set the nodes to sense and generate signal only on a single channel
        noise_power = GainCalculations.getAverageDataMeasurementsFromFile(coordinator_id ,rx_node.node_id)[1][0]
        
        #now we have to generate a signal and measure the received power
        #configure and start the signal generation
        try:
            tx_node.setGeneratorConfiguration(measuring_freq, p_tx_dBm)
            tx_node.generatorStart(time.time(), transmitting_duration)
        except:
            print "Calculate gain between %d and %d :  Error at generator. Return" %(tx_node_id, rx_node_id) 
            return
        
        #get current time. I want to know when I started the signal generation
        start_gen_time = time.time()
        #wait a second just to be sure that receiver senses the signal generated. (With this we take into account other delays that can appear in testbed)
        time.sleep(0.5)
        #sense the spectrum
        attempts =0
        while True:
            try:
                #start sense after time_after seconds from now
                rx_node.senseStart(time.time()+time_after, sensing_duration, 5)
               
                #if everything is fine, break this loop               
                break
            except Exception:
                #try a few more times if something went wrong
                if attempts < 2:
                    attempts += 1
                    print "Calculate gain between %d and %d : Receive power measurement error, retry %d" %(tx_node_id, rx_node_id, attempts) 
                    continue
                else:
                    print "Calculate gain between %d and %d : Receive power measurement error, return nothing" %(tx_node_id, rx_node_id)
                    #anyway, at this point there is a signal generated, so I don't want to affect other measurements, so we have to wait until signal generation stops
                    GainCalculations.sleepUntilSignalGenerationStops(start_gen_time, transmitting_duration)
                    return
        
        #now we have in file data with the measurements. Average data from the file: [[frequencies], [average power in W for a specific frequency]]
        received_power = GainCalculations.getAverageDataMeasurementsFromFile(coordinator_id,rx_node.node_id)[1][0]
        
        print "Gain calculation between tx_%d and rx_%d : Noise power: %.6fE-12      Received power: %.6fE-12" %(tx_node_id, rx_node_id,noise_power*1e12, received_power*1e12)
        
        #calculate gain
        gain = (received_power - noise_power) / (math.pow(10.00, p_tx_dBm/10.00) * 0.001)
        if gain<0:
            #in this case, something wrong happened, no signal was generated
            print "Calculate gain between %d and %d : Bad measurement, noise power is bigger than received_power, omit this measurement" %(tx_node_id, rx_node_id) 
            #wait for the signal generation stops
            GainCalculations.sleepUntilSignalGenerationStops(start_gen_time, transmitting_duration)
            return None
        
        print "Gain between node %d and node %d: %.9fE-6  ( %.6f dB)" %(tx_node.node_id, rx_node.node_id, gain *1e6, 10.00*math.log10(gain))
        
        #write this gain in a file if this is what we want
        results_list = [gain, received_power, noise_power, math.pow(10, p_tx_dBm/10.00) * 0.001, datetime.datetime.now()]
        
        #save results
        if(saveresults):
            GainCalculations.printResultsInAFile(results_list, coordinator_id ,tx_node.node_id, rx_node.node_id)
        
        #wait until signal generation stops
        GainCalculations.sleepUntilSignalGenerationStops(start_gen_time, transmitting_duration)
        
        #return gain
        return gain
    
    @staticmethod 
    def sleepUntilSignalGenerationStops(start_gen_time, transmitting_duration):
        #use this just when you generated a signal and you want to wait until generated signal is over.
        #generally this method is used by other methods inside this class
        #print "Time passed: %f" %(time.time() - start_gen_time)
        if ( (time.time() - start_gen_time) < transmitting_duration):
            #that means we have to wait
            print "Sleep for %f until signal generation stops" %(math.ceil(transmitting_duration - (time.time() - start_gen_time)))
            time.sleep(math.ceil(transmitting_duration - (time.time() - start_gen_time)))
        return
    
    @staticmethod    
    def convertListElementsToFloat(list_to_be_converted):
        #use this when you have a list with string numbers and you want to convert the list elements to float numbers.
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
    def getFileResults(coordinator_id, tx_node_id, rx_node_id, year=None, month=None, day=None):
        #reads the file which contains the saved measurements. Reads only the gains measurements made until the specified date. If no date is specified, then all available gains will be returned 
        
        #first, check if the file exists
        path = "./gain measurements/coor_%d/gain_between_tx_%d_and_rx_%d.dat" %(coordinator_id ,tx_node_id,  rx_node_id)
        
        if not os.path.isfile(path) or not os.path.exists(path):
            return None
            
        f = open(path, "r")
        
        #read first line, it's a header
        f.readline()
        
        #gains will have the following form : [ [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], .. ]
        gains = []
        
        while True:
            line = f.readline()
            if not line:
                #end of file
                break
            
            line_list = line.split()
            
            try:
                #check the date
                date = DateTime.strptime((line_list[4] + " " + line_list[5])[0:16], "%Y-%m-%d %H:%M")
                if (year!=None and month != None and day!=None):
                    if date.year > year:
                        break
                    if date.year == year and date.month>month:
                        break
                    if date.year == year and date.month == month and date.day > day:
                        break
                
                gains.append([float(line_list[0]), float(line_list[1]), float(line_list[2]), float(line_list[3]), line_list[4] + " " +line_list[5]])
            except:
                continue
        f.close()
        
        #The file might exists, but you may not have results until the specified date
        if len(gains) ==0:
            print "No measurements for this date or file exists, but it's empty"
            return None
        
        return gains
    
    @staticmethod
    def getMinMaxGain(coordinator_id, tx_node_id, rx_node_id, year=None, month=None, day=None):
        #read from file (if it exists) and return the minimum and maximum gain
        #specify year, month, day if you only want to take into account gain measurements made until that date. If those are not specified, then all measurements will be taken into account.
        
        #first get data from the file
        gains = GainCalculations.getFileResults(coordinator_id, tx_node_id, rx_node_id, year=year, month=month, day=day)
        #gains will have the following form : [ [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], .. ]
        
        if gains is None:
            aux = tx_node_id
            tx_node_id = rx_node_id
            rx_node_id = aux
            print "There are no values available for this combination. Trying with gain_between_tx_%d_and_rx_%d.dat? (yes or no)" %(tx_node_id, rx_node_id)
            choice = raw_input("")
            
            if choice.lower() == "no":
                print "You have chosen no"
                return None
            elif choice.lower() == "yes":
                gains = GainCalculations.getFileResults(coordinator_id, tx_node_id, rx_node_id, year=year, month=month, day=day)
                if gains is None:
                    print "Sorry, there are no measurements for this combination at all"
                    return None
            else:
                print "Invalid input, you were supposed to enter yes or no"
                return None
            
        max_gain = -float("inf")
        min_gain = float("inf")
        for i in gains:
            if i[0]>max_gain:
                max_gain = i[0]
            if i[0]<min_gain:
                min_gain = i[0]
                
        return [min_gain, max_gain]
    
    @staticmethod
    def getMinMaxNoise(coordinator_id, tx_node_id, rx_node_id, year=None, month=None, day=None):
        #read from file (if it exists) and return the minimum and maximum noise
        #specify year, month, day if you only want to take into account gain measurements made until that date. If those are not specified, then all measurements will be taken into account.
        
        #first get data from the file
        gains = GainCalculations.getFileResults(coordinator_id, tx_node_id, rx_node_id, year=year, month=month, day=day)
        #gains will have the following form : [ [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], .. ]
        
        if gains is None:
            aux = tx_node_id
            tx_node_id = rx_node_id
            rx_node_id = aux
            print "There are no values available for this combination. Trying with gain_between_tx_%d_and_rx_%d.dat? (yes or no)" %(tx_node_id, rx_node_id)
            choice = raw_input("")
            
            if choice.lower() == "no":
                print "You have chosen no"
                return None
            elif choice.lower() == "yes":
                gains = GainCalculations.getFileResults(coordinator_id, tx_node_id, rx_node_id, year=year, month=month, day=day)
                if gains is None:
                    print "Sorry, there are no measurements for this combination at all"
                    return None
            else:
                print "Invalid input, you were supposed to enter yes or no"
                return None
            
        max_noise = -float("inf")
        min_noise = float("inf")
        for i in gains:
            if i[2]>max_noise:
                max_noise = i[2]
            if i[2]<min_noise:
                min_noise = i[2]
                
        return [min_noise, max_noise]
            
    @staticmethod
    def getMostRecentGainMeasurments(coordinator_id, tx_node_id, rx_node_id, number = 6):
        #number represents the number of measurements to be returned. How many measurements you want to get. Example: if number=3, return last 3 measurements made
        #use this method when you want to get a list with a specified number of last measurements made
        if number == 0:
            #that means nothing
            return None
        
        #define a queue
        queue = MyQueue(number)
    
        #read from file (if it exists)
        #first, check if the file exists
        path = "./gain measurements/coor_%d/gain_between_tx_%d_and_rx_%d.dat" %(coordinator_id ,tx_node_id,  rx_node_id)
        
        if not os.path.isfile(path) or not os.path.exists(path):
            return None
        
        f = open(path, "r")
        
        #read first line, it's a header
        f.readline()
        
        #read file line by line
        while True:
            line = f.readline()
            if not line:
                break
            
            #define a line list: [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ] - this is how results are saved in the file
            line_list = line.split()
            try:
                queue.append(float(line_list[0]))
            except:
                pass
        
        f.close()
        return queue.getListReverse()
    
    @staticmethod
    def getUpdatedPredictedGain(coordinator_id ,tx_node_id, rx_node_id, number = 6):
        #this method will take a new gain measurement (update) and based on "number" measurements done before and saved in a .dat file, it will predict the next gain
        
        #get last measurements made
        recentMeasurements = GainCalculations.getMostRecentGainMeasurments(coordinator_id, tx_node_id, rx_node_id, number)    
        if recentMeasurements is None:
            #invert tx with rx
            aux = tx_node_id
            tx_node_id = rx_node_id
            rx_node_id = aux
            print "There are no measurements available for this combination. Trying with gain_between_tx_%d_and_rx_%d.dat?(yes or no)" %(tx_node_id, rx_node_id)
            choice = raw_input("")
            if choice.lower() == "no":
                print "You have chosen no"
                return None
            
            elif choice.lower() =="yes":
                recentMeasurements = GainCalculations.getMostRecentGainMeasurments(coordinator_id, tx_node_id, rx_node_id, number)
                if recentMeasurements is None:
                    print "There are no measurements available for this combination at all."
                    return None
            else:
                print "Invalid input, you were supposed to enter yes or no"
                return None
            
        #take a new measurement
        instant_gain= GainCalculations.calculateInstantGain(coordinator_id, tx_node_id, rx_node_id, measuring_freq=2420e6, saveresults=False, transmitting_duration=6)
        #append the instant gain to the end of the recentMeasurements list
        if instant_gain is None:
            print "Cannot measure instant gain"
            return None
        recentMeasurements.append(instant_gain)
        
        predicted_gain = kalmanImplementation.getPredictedValuesVer2(recentMeasurements, standard_deviation=GainCalculations.getStandardDeviation(coordinator_id, tx_node_id, rx_node_id))[-1]
        print "Gain measurement between tx_%d and rx_%d: instant gain: %.3f dB   predicted gain: %.3f dB" %(tx_node_id, rx_node_id, 10.00 * math.log10(instant_gain),  10.00*math.log10(predicted_gain) )
        return predicted_gain
        
    @staticmethod
    def getStandardDeviation(coordinator_id ,tx_node_id, rx_node_id, year=None, month=None, day=None):    
        #use this method when you want to calculate the standard deviation from the saved gain measurements
        #read from file (if it exists)
        
        #first get data from the file
        gains = GainCalculations.getFileResults(coordinator_id, tx_node_id, rx_node_id, year=year, month=month, day=day)
        #gains will have the following form : [ [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], .. ]
        
        if gains is None:
            aux = tx_node_id
            tx_node_id = rx_node_id
            rx_node_id = aux
            print "There are no values available for this combination. Trying with gain_between_tx_%d_and_rx_%d.dat? (yes or no)" %(tx_node_id, rx_node_id)
            choice = raw_input("")
            
            if choice.lower() == "no":
                print "You have chosen no"
                return None
            elif choice.lower() == "yes":
                gains = GainCalculations.getFileResults(coordinator_id, tx_node_id, rx_node_id)
                if gains is None:
                    print "Sorry, there are no measurements for this combination at all"
                    return None
            else:
                print "Invalid input, you were supposed to enter yes or no"
                return None
           
        #we are interested only in gains, not other data
        gain_measurements = []
        for i in gains:
            gain_measurements.append(i[0])
        
        return kalmanImplementation.getStandardDeviation(gain_measurements)
        
    @staticmethod
    def getAverageGain(coordinator_id ,tx_node_id, rx_node_id, year=None, month=None, day=None):
        #returns the average gain from the saved gain measurements.
        #specify year, month, day if you only want to take into account gain measurements made until that date. If those are not specified, then all measurements available will be taken into account.
        #read from file (if it exists)
        
        #first get data from the file
        gains = GainCalculations.getFileResults(coordinator_id, tx_node_id, rx_node_id, year=year, month=month, day=day)
        #gains will have the following form : [ [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], .. ]
        
        if gains is None:
            aux = tx_node_id
            tx_node_id = rx_node_id
            rx_node_id = aux
            print "There are no values available for this combination. Trying with gain_between_tx_%d_and_rx_%d.dat? (yes or no)" %(tx_node_id, rx_node_id)
            choice = raw_input("")
            
            if choice.lower() == "no":
                print "You have chosen no"
                return None
            elif choice.lower() == "yes":
                gains = GainCalculations.getFileResults(coordinator_id, tx_node_id, rx_node_id, year=year, month=month, day=day)
                if gains is None:
                    print "Sorry, there are no measurements for this combination at all"
                    return None
            else:
                print "Invalid input, you were supposed to enter yes or no"
                return None
            
        sum = 0.00
        k = 0.00
        for i in gains:
            sum+=i[0]
            k+=1
            
        return sum/k
    
    @staticmethod
    def getAverageNoise(coordinator_id ,tx_node_id, rx_node_id, year=None, month=None, day=None):
        #returns the average noise from the saved gain measurements. Every time a gain measurement is performed, noise power is also measured
        #specify year, month, day if you only want to take into account measurements made until that date. If those are not specified, then all measurements available will be taken into account.
        #read from file (if it exists)
        
        #first get data from the file
        gains = GainCalculations.getFileResults(coordinator_id, tx_node_id, rx_node_id, year=year, month=month, day=day)
        #gains will have the following form : [ [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], .. ]
        
        if gains is None:
            aux = tx_node_id
            tx_node_id = rx_node_id
            rx_node_id = aux
            print "There are no values available for this combination. Trying with gain_between_tx_%d_and_rx_%d.dat? (yes or no)" %(tx_node_id, rx_node_id)
            choice = raw_input("")
            
            if choice.lower() == "no":
                print "You have chosen no"
                return None
            elif choice.lower() == "yes":
                gains = GainCalculations.getFileResults(coordinator_id, tx_node_id, rx_node_id, year=year, month=month, day=day)
                if gains is None:
                    print "Sorry, there are no measurements for this combination at all"
                    return None
            else:
                print "Invalid input, you were supposed to enter yes or no"
                return None
    
        sum = 0.00
        k = 0.00
        for i in gains:
            sum+=i[2]
            k+=1
            
        return sum/k
    
    ''' 
    @staticmethod
    def getPredictionGainUsingKalmanFilter(coordinator_id ,tx_node_id, rx_node_id, year=year, month=month, day=day):
        #apply Kalman filter for all measurements made. This will return a list which will contains predicted values. I use this just in gains plots.
        
        #first get data from the file
        gains = GainCalculations.getFileResults(coordinator_id, tx_node_id, rx_node_id, year=year, month=month, day=day)
        #gains will have the following form : [ [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], .. ]
        
        if gains is None:
            aux = tx_node_id
            tx_node_id = rx_node_id
            rx_node_id = aux
            print "There are no values available for this combination. Trying with gain_between_tx_%d_and_rx_%d.dat? (yes or no)" %(tx_node_id, rx_node_id)
            choice = raw_input("")
            
            if choice.lower() == "no":
                print "You have chosen no"
                return None
            elif choice.lower() == "yes":
                gains = GainCalculations.getFileResults(coordinator_id, tx_node_id, rx_node_id, year=year, month=month, day=day)
                if gains is None:
                    print "Sorry, there are no measurements for this combination at all"
                    return None
            else:
                print "Invalid input, you were supposed to enter yes or no"
                return None
            
        gain_list = []
        for i in gains:
            gain_list.append(i[0])
        
        return kalmanImplementation.getPredictedValuesVer2(gain_list)
    '''    
    
    @staticmethod
    def getAverageDataMeasurementsFromFile(coordinator_id ,node_id):
        #when we do the sensing, all data is saved in a .dat file. For the same frequency, we can have multiple samples of RSSI. We want the average of the measured powers from that file
        #reads the data from file, average power at every frequency
        #returns a list with the following structure: [[frequency] , [average_power for one specific frequency]]
        #average power returned is linear [ W ]
        
        #open the file for reading
        f = open("./data/coor_%d/node_%d.dat" %(coordinator_id ,node_id) , "r")
        
        #read first line, it's a header
        f.readline()
        
        #I want to make a data_list with the following structure: [ [frequency]  ,[ [ list of all powers for that frequency] ] ]
        #An example of data_list:  [[freq1, freq2] , [[RSSI1, RSSI2, RSSI3], [RSSI1, RSSI2] ]]
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
        #I want a list average_data: [[frequency], [average_power for that frequency]]. It will contain average power for several certain frequencies
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
        if not os.path.isfile(path) or not os.path.exists(path):
            #if the file doesn't exits, then create it
            print "Writing a new file"
            f = open(path, "w")
            f.write("[Gain]                [Received power ]           [Noise power]            [Transmitted power]            [Date]     - all power units in W\n")
            f.close()
        
        #append new data to file
        f = open(path, "a")
        
        for element in results_list:
            f.write(str(element))
            f.write("        ")
        f.write("\n")
        f.close()
        
    @staticmethod
    def plotGains(coordinator_id ,tx_node_id, rx_node_id, year = None, month = None, day = None):
        #call the method when you want to plot the results from the file
        #open file with measurements and plot results from it
        #specify year, month, day if you only want to take into account gain measurements made until that date. If those are not specified, then all measurements will be taken into account.
        
        #first get data from the file
        gains = GainCalculations.getFileResults(coordinator_id, tx_node_id, rx_node_id, year=year, month=month, day=day)
        #gains will have the following form : [ [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], [gain - linear , received_power[w] , noise_power[w], transmitted_power[w], date ], .. ]
        
        if gains is None:
            aux = tx_node_id
            tx_node_id = rx_node_id
            rx_node_id = aux
            print "There are no values available for this combination. Trying with gain_between_tx_%d_and_rx_%d.dat? (yes or no)" %(tx_node_id, rx_node_id)
            choice = raw_input("")
            
            if choice.lower() == "no":
                print "You have chosen no"
                return None
            elif choice.lower() == "yes":
                gains = GainCalculations.getFileResults(coordinator_id, tx_node_id, rx_node_id, year=year, month=month, day=day)
                if gains is None:
                    print "Sorry, there are no measurements for this combination at all"
                    return None
            else:
                print "Invalid input, you were supposed to enter yes or no"
                return None
            
        print "Plot gains"    
            
        #define a gain_list : [[gain_dB], [date]]
        gain_list = [[],[]]
        
        for i in gains:
            date = DateTime.strptime((i[4])[0:16], "%Y-%m-%d %H:%M")
            gain_list[0].append(10.00 * math.log10(i[0]) )
            gain_list[1].append(date)
            
        #plot results
        Plot.plotGains(gain_list[1], gain_list[0], "Number of measurements", "Gain [dB]", "Gain between tx%d and rx%d" %(tx_node_id, rx_node_id), False)
        
    @staticmethod
    def plotAllGainsWithinCoordinator(coordinator_id):
        #if you want to plot all gains within a coordinator call this method.
        path = "gain measurements/coor_%d" %coordinator_id
        
        for i in os.listdir(path):
            tx_node_id = i[ (i.index("tx_") +3) : (i.index("_and"))]
            rx_node_id = i[ (i.index("rx_") +3):  (i.index(".dat"))]
            GainCalculations.plotGains(coordinator_id, int(tx_node_id), int(rx_node_id))