import math
import threading
import time
import random
import os
import datetime

from gainCalculations import GainCalculations
from plot import Plot
from myQueue import MyQueue


class PowerAllocation(threading.Thread):
    #This class is responsible with the allocation of powers which players application can use
    #Needs a player object and playerApp object in order to work
  
    #VESNA power generating list. This must be sorted. Powers are in dBm
    available_generating_powers = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18, -20, -22, -24, -26, -28, -30, -55]
  
    #current transmitting power [dBm]
    current_transmitting_power = random.choice(available_generating_powers)
    
    #previous transmitted_power [dBm]
    previous_transmitted_power = current_transmitting_power
    
    #neighbor current_transmitting power [dBm]
    neighbor_current_transmitting_power = random.choice(available_generating_powers)
    
    #neighbor previous transmitted_power [dBm]
    neighbor_previous_transmitted_power = neighbor_current_transmitting_power
    
    #temporary - this best response is not truncated according to VESNA power list 
    best_response_untouched = current_transmitting_power
    
    #game type - can be: 1, 2, 3 . Depends on the implementation you want to use
    game_type = 3
    
    #neighborPowerEvent. When this is True, It means that neighbor player changed its power
    neighborPowerEvent = False
    
    #threshold_power. This can be set any time. We need this when we determine if Nash equilibrium was reached
    threshold_power = 0.8
    
    #A list in which we will save experiment results
    results_list = []
    
    #a boolean variable which tells the program if the cost is fixed or adaptive [not implemented yet]
    adaptive_cost = False
    
    #When this is triggered( =True ) then it means that equilibrium has been reached and the threads stops here.
    equilibriumDetected = False
    
    def __init__(self, playerObject ,playerAppObject, gameType = 3):
        print "Player power Allocation"
        threading.Thread.__init__(self)
        
        #save player object, that way, I can have any data I want from this player. Player object contains info about nodes (tx and rx), gains, cost..
        self.player = playerObject
        
        #Save playerAppObject this is how I can communicate with the PlayerApp object.
        self.playerApp = playerAppObject
        
        #configure sense node here, it's enough to be done only once
        self.player.rx_node.setSenseConfiguration(self.playerApp.frequency, self.playerApp.frequency, 400e3)
    
        #Let playerApp have this powerAllocationObject
        self.playerApp.setPowerAllocationOjbect(self)
        
        #save gameType
        self.game_type = gameType
        
    def printPowerAllocationInfo(self):
        print "PowerAllocation associated to player %d" %self.player.player_number    
    
    def setGameType(self, game_type):
        if game_type<1 or game_type>3:
            print "Game type can be 1, 2 or 3"
            self.game_type = 1
            return
        self.game_type = game_type    
        
    def setNeighborPowerAllocationObject(self, powerAllocationObject):
        #This is how I can communicate with the neighbor player
        #save powerAllocationObject
        self.neighborPowerAllocation = powerAllocationObject
        
    def setThresholdPower(self, threshold_power):    
        self.threshold_power = threshold_power
        print "Player %d : threshold power was set to: %.3f" %(self.player.player_number, self.threshold_power)
        
    def getTransmittingPower(self):
        #if PlayerApp needs to know the power which he can use, it's calling this method and he will get the allowed transmitting power
        #return self.current_transmitting_power
        return self.getTheNearestPower(self.current_transmitting_power)
    
    #there are several bestReponse methods
    def getBestResponseTheoreticallyForm(self):
        #based on the cost, cross gain, direct gain , neighbor power transmitting and noise we can determine new power
        #for best understanding see the formula in the article
        #We want to return a power in dBm. This power is the best power in interference condition 
        #this formula anticipates the received power basing on constant gains and noise
        
        #convert power from dBm to W
        #I need to know what power my neighbor is using. I know this from self.neighbor_current_transmitting_power, but is always worth checking.
        if (self.neighborPowerAllocation.current_transmitting_power != self.neighbor_current_transmitting_power):
            #Update neighbor_current_transmiting_power
            print "Neighbor current transmitting power uncertainty.Updating neighbor_current_transmitting_power"
            self.neighbor_current_transmitting_power = self.neighborPowerAllocation.current_transmitting_power
            
        #convert power to W
        neighbor_transmitting_power = math.pow(10.00, float(self.neighbor_current_transmitting_power) / 10.00) * 0.001
        best_response = (1.00/float(self.player.cost)) - (self.player.cross_gain * neighbor_transmitting_power  + self.player.noise_power) / float(self.player.direct_gain)
        
        #return a dBm power
        try:
            return 10.00 * math.log10(best_response/0.001)  
        except:
            print "Player %d: negative best response" %(self.player.player_number)
            return None  
    
    def getBestResponsePracticallyForm1(self, transmitted_power_dbm, received_power_dbm):
        #For best understanding see the formula in the article
        #This method returns a power in dBm. This power is the best power in interference condition
        #This method use the practically formula which will be used in empirical games
        #this formula will take into account the useful transmitted power 
        
        #parameters are  powers in dBm, we must convert them to W 
        transmitted_power_watts = math.pow(10.00, float(transmitted_power_dbm)/10.00) * 0.001
        useful_received_power_watts = transmitted_power_watts * self.player.direct_gain
        received_power_watts = math.pow(10.00, float(received_power_dbm)/10.00) * 0.001
        
        #now we have everything we need to calculate the new power based on formula: 1/c  -  (I+N)/gain, where I+N = received_power - useful_received_power
        if (transmitted_power_dbm < -1000):
            #In this case we consider that current player is not sending something useful, so he measured only noise and interference
            best_response = (1.00/float(self.player.cost)) - (received_power_watts)/float(self.player.direct_gain)
        else :
            best_response = (1.00/float(self.player.cost)) - (received_power_watts - useful_received_power_watts)/float(self.player.direct_gain)

        #I want to return a dBm power, because that is what we are sending to the nodes
        try:
            return 10.00 * math.log10(best_response/0.001) 
        except:
            print "Player %d: negative best response" %(self.player.player_number)
            return None
       
    def getBestResponsePracticallyForm2(self, received_power_dbm):
        #For best understanding see the formula in the article
        #This method return a power in dBm. This power is the best power in interference condition
        #This method use the practically formula which will be used in empirical games 
        #This formula is based on the received power dBm, which must be only noise and interference
        
        #convert received_power in W
        received_power_watts = math.pow(10.00, float(received_power_dbm)/10.00) * 0.001
        best_response = (1.00/float(self.player.cost)) - (received_power_watts)/float(self.player.direct_gain) 
        
        #I want to return a dBm power
        try:
            return 10.00 * math.log10(best_response/0.001) 
        except:
            print "Player %d: negative best response" %(self.player.player_number)
            return None
    
     
    '''
    #not implemented
    def costAdaptiveChange_Fang(self, received_power_dbm, useful_received_power_dbm):
        #must measure sinr first
        received_power = math.pow(10.00, float(received_power_dbm)/10.00) * 0.001
        useful_received_power = math.pow(10.00, float(useful_received_power_dbm)/10.000) * 0.001
        sinr = (useful_received_power)/(received_power-useful_received_power)
        print "Player %d  new cost adaptive changed: %.6f" %(self.player.player_number, 10/sinr)
    
    def costAdaptiveChange_Huang(self, received_power_dbm):
        received_power = math.pow(10.00, float(received_power_dbm)/10.00) * 0.001
        new_cost = (self.player.priority / (received_power))
        print "Player %d  new cost adaptive changed: %.6f" %(self.player.player_number, new_cost)
        self.player.setCost(new_cost)
        
    def enableAdaptiveCost(self):
        self.adaptive_cost = True
        
    def disableAdaptiveCost(self):
        self.adaptive_cost = False
    '''    
        
    def sharePowerToTheNeighbor(self, power_dBm):
        #Player i will call this method to share his new power to the neighbor
        #This is used in theoretically game
        self.neighborPowerAllocation.changeNeighborPowerAtribute(power_dBm)
        
    def changeNeighborPowerAtribute(self, new_power_dBm):
        #this method only changes self.neighbor_current_transmitting_power
        self.neighbor_previous_transmitted_power = self.neighbor_current_transmitting_power 
        self.neighbor_current_transmitting_power = new_power_dBm    
       
    def alertNeighborAboutAChangeOfPower(self):
        #Player i will call this method to alert the neighbor player that he made a change of power.
        self.neighborPowerAllocation.neighborPowerEvent = True
        
    def changeCurrentPower(self, new_power_dbm):
        #change power on current object. Use this method to unbalance the system by generating an event.
        
        #save new power
        self.previous_transmitted_power = self.current_transmitting_power
        self.current_transmitting_power = new_power_dbm
        
        print "Player %d intentionally changed  his power: previous power = %.6f   current power = %.6f" %(self.player.player_number ,self.previous_transmitted_power, self.current_transmitting_power)
        
        #before we generate, let's make sure the other players are not transmitting now
        #wait for the neighbor to finish his transmission
        while self.neighborPowerAllocation.playerApp.isSendingAPacket():
            print "Player %d : waiting for the neighbor to finish his transmission" %self.player.player_number
            time.sleep(1)

        #transmit for a few seconds. 
        if self.game_type != 1:
            #if it's a theoretical game (simulation) it's no needed to transmit anything
            self.playerApp.sendPacket(8)
            #announce the other player that I made a change
            #but first, wait 1-2 seconds to be sure that the neighbor player catch the interference (there might be other delays in the testbed)
            time.sleep(1)
         
        #announce neighbor about a change
        self.sharePowerToTheNeighbor(self.current_transmitting_power)
        self.alertNeighborAboutAChangeOfPower()   
        
        #add an iteration to the results_list (We want to save all experiment results in a file). results_list has the following structure: [new power calculated_truncated, new_power_calculated_non_truncated, received power, anticipated useful received power, player cost] 
        try:
            self.results_list[0] = ([self.current_transmitting_power, self.current_transmitting_power, "None", "None", self.player.cost])
        except:
            pass 
            
        return
    
    def checkEquilibrium(self,equal_condition = False):
        #check difference between last best responses
        #Depends on the implementation, if you want to compare equilibrium considering truncated values, than equal_condition= True, otherwise set it to False
        #list :[most recent, less recent, less recent, ..]
        print "Player %d check equilibrium :" %(self.player.player_number)
        list = self.queue_list.getList()
        length = self.queue_list.len
        print list
        
        if len(list) != length :return False
        
        if equal_condition == False:
            for i in range(0, len(list)):
                if math.fabs(math.fabs(float(list[0])) - math.fabs(float(list[i])) ) > float(self.threshold_power):
                    return False
             
            #if I've got here it means that the Nash equilibrium condition is reached   
            return True 
        else:
            #in this case, all best responses must be equal
            for i in range(0, len(list)-1):
                if float(list[i]) != float(list[i+1]):
                    return False
                
            return True
    
    def limitCurrentTransmittingPower(self):
        if self.current_transmitting_power > 0 :
            print "Player %d limited his own  power to 0 dBm from %.3f" %(self.player.player_number, self.current_transmitting_power)
            self.current_transmitting_power = 0
        if self.current_transmitting_power < -55:
            print "Player %d limited his own  power to -55 dBm from %.3f" %(self.player.player_number, self.current_transmitting_power)
            self.current_transmitting_power = -55
    
    def printIterationsToFile(self, results_list, other_observations = None):
        #first make folders
        try:
            os.mkdir("./iterations")
        except:
            pass
        
        try:
            if self.player.player_number == 1:
                os.mkdir("./iterations/c1_%d-c2_%d" %(self.player.cost, self.neighborPowerAllocation.player.cost))
            elif self.player.player_number == 2:
                os.mkdir("./iterations/c1_%d-c2_%d" %(self.neighborPowerAllocation.player.cost, self.player.cost))
        except:
            pass
        
        if self.player.player_number == 1:    
            path =  "./iterations/c1_%d-c2_%d/player_%d_with_tx_%d_and_rx_%d.dat" %(self.player.cost, self.neighborPowerAllocation.player.cost,self.player.player_number, self.player.tx_node.node_id, self.player.rx_node.node_id)
        else:
            path =  "./iterations/c1_%d-c2_%d/player_%d_with_tx_%d_and_rx_%d.dat" %(self.neighborPowerAllocation.player.cost,self.player.cost,self.player.player_number, self.player.tx_node.node_id, self.player.rx_node.node_id)
        
        #see if the path exits and if not create if for the first time
        if (not os.path.exists(path) or not os.path.isfile(path)):
            #create the file
            f = open(path, "w")
            f.write("In this file you will find experiments results about the convergence of the player %d with tx_%d and rx_%d\n" %(self.player.player_number, self.player.tx_node.node_id, self.player.rx_node.node_id))
            f.close()
        
        f = open(path, "a")
        
        if other_observations == None:
            other_observations = "None"
        
        if self.adaptive_cost:
            f.write("Experiment made at: %s. Configuration: cost = %s    threshold = %.3f . Type of the game: %d . Direct gain: %.3f dB   Cross gain: %.3f dB  Observations:%s\n" %(str(datetime.datetime.now()),str(self.player.cost)+ " adaptive", self.threshold_power, self.game_type, 10.00*math.log10(self.player.direct_gain), 10.00 * math.log10(self.player.cross_gain), other_observations))
        else:
            f.write("Experiment made at: %s. Configuration: cost = %s    threshold = %.3f . Type of the game: %d . Direct gain: %.3f dB   Cross gain: %.3f dB  Observations:%s\n" %(str(datetime.datetime.now()), str(self.player.cost) + " fixed", self.threshold_power, self.game_type, 10.00*math.log10(self.player.direct_gain), 10.00 * math.log10(self.player.cross_gain), other_observations))
        
        for i in range(0, len(results_list)):
            f.write("Iteration: %d     New_Power: %.12f ( %.6f )  Measured_Power: %s  Anticipated_useful_received_power: %s    Instant cost: %.3f\n" %(i, results_list[i][0], results_list[i][1],str(results_list[i][2]), str(results_list[i][3]), results_list[i][4] ) )
            
        f.write("\n")
        f.close()
        
    def printStrategyTable(self, nash_value_player1, nash_value_player2, iterations=-1):
        #prints to a file, only the Nash equilibrium value
        path = "./iterations/strategyTable.dat" 
        
        #see if the path exits and if not create it for the first time
        if (not os.path.exists(path) or not os.path.isfile(path)):
            #create the file
            f = open(path, "w")
            f.write("In this file you will find Nash Equilibrium values\n")
            f.close()
        
        f = open(path, "a")
        
        if self.player.player_number == 1:
            f.write("c1= %d   c2= %d   Nash value player 1= %.9f dBm    Nash value player 2= %.9f dBm  Iterations= %d  h11= %.3f dB h21= %.3f dB  h22= %.3f dB  h12= %.3f dB  Player1Noise=%.3fE-13  Player2Noise=%.3fE-13  Date= %s\n" % (self.player.cost, self.neighborPowerAllocation.player.cost, nash_value_player1, nash_value_player2, iterations, 10.00 * math.log10(self.player.direct_gain), 10.00*math.log10(self.player.cross_gain), 10.00*math.log10(self.neighborPowerAllocation.player.direct_gain), 10.00*math.log10(self.neighborPowerAllocation.player.cross_gain), self.player.noise_power*1e13, self.neighborPowerAllocation.player.noise_power*1e13,datetime.datetime.now() )  )
        f.close()
        
    def getTheNearestPower(self, power):
        #from the available power list choose the nearest from the power
        
        min_diferrence = float("inf")
        nearest_power = None
        #Small discussion: self.available_generating_powers it's ascending sorted
        #The update takes only when you find an available power more appropriate to given power. If the there are 2 available power which gives the same distance from the given power, the greater value will be chosen. Example: available power list [0 , -2, -4, ..] and we have a given power= -1, the result will be 0 
        for i in range(0, len(self.available_generating_powers)):
            if (math.fabs(power-self.available_generating_powers[i]) < min_diferrence):
                min_diferrence = math.fabs(power-self.available_generating_powers[i])
                nearest_power = self.available_generating_powers[i]
                
        return nearest_power
    
    def equilibriumDectected(self):
        #when other players detect the equilibrium
        self.equilibriumDetected = True
    
    def gameType1(self):
        #number of iterations until player reach the Nash equilibrium
        iterations = 0
        #Use this because I want to see how long it takes to reach the Nash equilibrium
        process_start_time = time.time()
      
        #initialize results_list because I want to save all experiment results 
        self.results_list = [[self.getTheNearestPower(self.current_transmitting_power), self.current_transmitting_power, "None", "None", self.player.cost]]
        
        print "Player %d: game type 1 started" %self.player.player_number
        while True:
            #infinite loop
            #see if neighbor changed it's power
            if (self.neighbor_previous_transmitted_power != self.neighbor_current_transmitting_power):
                #neighbor power change event triggered
                #reset the event by equaling the old power with the current power 
                self.neighbor_previous_transmitted_power = self.neighbor_current_transmitting_power
                
                print "Player %d detected a change of power and it's recalculating its own transmission power" %self.player.player_number
                
                #there has been a change of power on the neighbor player, so I have to recalculate my own power
                #in this game type we use the theoretically formula
                self.previous_transmitted_power = self.current_transmitting_power
                self.current_transmitting_power = self.getBestResponseTheoreticallyForm()
                #save best response
                self.best_response_untouched = self.current_transmitting_power
                #truncate the value
                #self.current_transmitting_power = self.getTheNearestPower(self.current_transmitting_power)
                
                #append data in results list: [new power calculated, new_power_untouched, received power, anticipated useful received power] 
                self.results_list.append([self.current_transmitting_power, self.best_response_untouched, "None", "None", self.player.cost])
                iterations+= 1
                
                #now see if the new calculated power is different from the old one. If no, that means Nash equilibrium
                if self.previous_transmitted_power != self.current_transmitting_power :
                    print "Player %d changed his own power: previous power = %.6f dBm     current power = %.6f dBm" %(self.player.player_number, self.previous_transmitted_power, self.current_transmitting_power)
                    #announce the other player about my change
                    self.sharePowerToTheNeighbor(self.current_transmitting_power)
                else:
                    #best response is the same from the previous iteration
                    print "Player %d : new power is not different from the old one, that means Equilibrium. Number of iterations:%d  previous power=%.3f  current power=%.3f\n" %(self.player.player_number,iterations, self.previous_transmitted_power, self.current_transmitting_power)
                
                    #finish the game by stopping the threads
                    self.equilibriumDectected()
                    self.neighborPowerAllocation.equilibriumDectected()
    
            else:
                if self.equilibriumDetected:
                    print "Player %d Equilibrium. No events had been detected. Number of iterations:%d. Time passed: %.6f" %(self.player.player_number, iterations, (time.time() - process_start_time)) 
                    print "Player %d power allocated: %.3f" %(self.player.player_number, self.current_transmitting_power)
                    
                    #write experiment results in a file
                    self.printIterationsToFile(self.results_list)
                   
                    #if this is player 1, then print the strategy table( is enough that only one player to do that)
                    if self.player.player_number == 1:
                        self.printStrategyTable(self.current_transmitting_power, self.neighborPowerAllocation.current_transmitting_power, iterations=iterations)
                    break
                 
            time.sleep(0.01)  
         
    def gameType2(self):
        #number of iterations until player reach the Nash equilibrium
        iterations = 0
        #USe this because I want to see how long it takes to reach the Nash equilibrium
        process_start_time = time.time()
        
        print "Player %d Game type 2 started" %self.player.player_number
        
        #want to save the experiment results. results_list_ [new power calculated, received power, anticipated useful received power] 
        self.results_list = [[self.getTheNearestPower(self.current_transmitting_power), self.current_transmitting_power, "None", "None", self.player.cost]]
        
        self.queue_list = MyQueue(5)
        
        while True:
            #see if there is any power change alert from the neighbor
            if self.neighborPowerEvent :
                #that means neighbor changed its own power
                #reset the event because is being treated
                self.neighborPowerEvent = False
                
                print "Player %d detected a change of power and it's recalculating its own transmission power. Iteration %d" %(self.player.player_number, iterations)
                
                #anticipate transmitted_power. Initialize transmited_power with  -100000 dBm, equivalent with almost 0 in linear scale
                transmited_power_dbm_before_measurement = -100000   
                if self.playerApp.isSendingAPacket():
                    #yes, I am sending a packet right now, I have to consider that because I want to know what is interference and noise and what is not
                    transmited_power_dbm_before_measurement = self.playerApp.getTransmittingPower()
                
                #there hass been a change of power on the neighbor player, so I have to recalculate my own power
                #measure received power. received_power has the following structure: [[frequency], [power_dbm]]
                received_power = self.player.rx_node.senseStartQuick()
                
                #see if there is any power transmitting right now again. First initialize transmited_power_dbm with a very low power: -10000 dBm it's very small
                transmited_power_dbm_after_measurement = -100000
                if self.playerApp.isSendingAPacket():
                    #yes, I am sending a packet right now, I have to consider that because want to know when is interference and noise and when is not
                    transmited_power_dbm_after_measurement = self.playerApp.getTransmittingPower()
                
                #see if the useful transmitted power before and after measurements are equal, if not I can't be sure that when I did the measure, I was generating signal or no, that way I won't be able to determine the interference level
                if transmited_power_dbm_after_measurement != transmited_power_dbm_before_measurement:
                    print "Player %d bad anticipation of useful received power, continue this iteration and measure again" %(self.player.player_number)
                    #set event to true because it wasn't complete treated 
                    self.neighborPowerEvent = True
                    #measure again
                    continue
                
                if (transmited_power_dbm_after_measurement + 10.00 * math.log10(self.player.direct_gain)) > received_power[1][0]:
                    #the anticipated useful received power can't be higher than the received power
                    print "Anticipated received power > received power : %.6f > %.6f" %(transmited_power_dbm_after_measurement + 10.00 * math.log10(self.player.direct_gain), received_power[1][0])
                    self.neighborPowerEvent = True
                    continue
                    
                #just print some info
                if float(transmited_power_dbm_after_measurement) < -1000:
                    print "Player %d received power: [%.3f dBm] and he is not transmitting anything at this moment" %(self.player.player_number, received_power[1][0])
                else :
                    print "Player %d received power: [%.3f dBm] and he is transmitting with %.3f dBm. Anticipated useful received power: %.3f" %(self.player.player_number, received_power[1][0], transmited_power_dbm_after_measurement,  transmited_power_dbm_after_measurement + 10.00 * math.log10(self.player.direct_gain))
                    
                #now we have anything we need to calculate new power
                self.previous_transmitted_power = self.current_transmitting_power
                self.current_transmitting_power = self.getBestResponsePracticallyForm1(transmited_power_dbm_after_measurement, float(received_power[1][0]))
                
                #Sometimes formula returns a negative power (in linear!), which can't be possible.
                if self.current_transmitting_power is None:
                    self.neighborPowerEvent = True
                    #anyway, I want to keep previous transmitted power
                    self.current_transmitting_power = self.previous_transmitted_power
                    continue
                
                #copy best response
                self.best_response_untouched = self.current_transmitting_power
                self.current_transmitting_power = self.getTheNearestPower(self.current_transmitting_power)
                
                #make some list with iterations and calculated powers
                self.results_list.append([self.current_transmitting_power, self.best_response_untouched, received_power[1][0], transmited_power_dbm_after_measurement + 10.00 * math.log10(self.player.direct_gain), self.player.cost])
                self.queue_list.append(self.best_response_untouched)
                #we want to count how many iterations the algorithm used to reach the Nash equilibrium
                iterations+= 1
                
                #see if the difference between new power and old power exceeds the threshold_power
                if not self.checkEquilibrium(equal_condition=False):
                    #Nash equilibrium hasn't reached yet
                    print "Player %d has not reached the Nash Equilibrium yet" %(self.player.player_number)
                    
                    #generate at new power. This is needed because this way the neighbor player can see the change I made
                    #send a packet for 12 seconds
                    self.playerApp.sendPacket(8)
                    #to be sure the neighbor will catch my generated signal, a wait for 1 second (this way I consider the programming time)
                    time.sleep(1)
                    #announce the other player about my change
                    self.alertNeighborAboutAChangeOfPower()
                else:
                    #that means equilibrium
                    print "Player %d : Equilibrium has been reached" %(self.player.player_number)
                    
                    #finish the game by stopping the threads
                    self.equilibriumDectected()
                    self.neighborPowerAllocation.equilibriumDectected()
                
            else:
                if self.equilibriumDetected:
                    print "Player %d Equilibrium. No events had been detected. Number of iterations:%d. Time passed: %.6f" %(self.player.player_number, iterations, (time.time() - process_start_time) - 45) 
                    print "Player %d power allocated: %.3f" %(self.player.player_number, self.current_transmitting_power)
                    
                    #write experiment results in a file
                    self.printIterationsToFile(self.results_list)
                   
                    #if this is player 1, then print the strategy table( is enough that only one player to do that)
                    if self.player.player_number == 1:
                        self.printStrategyTable(self.current_transmitting_power, self.neighborPowerAllocation.current_transmitting_power, iterations=iterations)
                    break
            time.sleep(0.03)
                    
    def gameType3(self):  
        #number of iterations until player reached the Nash equilibrium
        iterations = 0
        #USe this because I want to see how long it takes to reach the Nash equilibrium
        process_start_time = time.time()
        
        print "Player %d Game type 3 started" %self.player.player_number
        
        #want to save the experiment results. results_list_ [[new power calculated truncated, new_power_calculated, received power, anticipated useful received power], [same thing],[same thing].. ] 
        self.results_list = [[self.getTheNearestPower(self.current_transmitting_power), self.current_transmitting_power, "None", "None", self.player.cost]]
        #a queue_list which will help us to know if the equilibrium has been reached
        self.queue_list = MyQueue(5)
        
        while True:
            #infinite loop
            #see if there is any power change alert from the neighbor
            if self.neighborPowerEvent :
                #that means neighbor changed its own power, so I have to update my power
                #reset the event because is being treated
                self.neighborPowerEvent = False
                
                print "Player %d detected a change of power and it's recalculating its own transmission power. Iteration %d" %(self.player.player_number, iterations)
                
                #check if I am transmitting something right now
                if( self.playerApp.isSendingAPacket()):
                    #I can't measure in this case, I want to measure only interference and noise
                    while self.playerApp.isSendingAPacket():
                        print "Player %d : bad news, I'm transmitting packets right now, wait to stop!" %self.player.player_number
                        time.sleep(1)
                    
                    #Ask the neighbor to recalculate power and regenerate a signal
                    self.alertNeighborAboutAChangeOfPower()
                    continue
                
                #measure received power. received_power has the following structure: [[frequency], [power_dbm]]
                received_power = self.player.rx_node.senseStartQuick()
                print "Player %d received noise and interference power: %.3f dBm" %(self.player.player_number, received_power[1][0])
                
                #now we have anything we need to calculate new power
                self.previous_transmitted_power = self.current_transmitting_power
                #the best response returned is in dBm
                self.current_transmitting_power = self.getBestResponsePracticallyForm2(received_power[1][0])
                
                #sometimes formula returns a negative power in linear, that can't be possible in practice, so if that happens, continue this iteration
                if self.current_transmitting_power is None:
                    print "Player %d negative power" %self.player.player_number
                    self.current_transmitting_power = self.previous_transmitted_power
                    self.neighborPowerEvent = True
                    continue
                
                #the best response give us a real power, in practice we can't generate a power at any resolution ( The formula doesn't take into account this thing)
                #On VESNA platform there are a few power values that can be generated
                print "Player %d best response: %.6f. Choosing the right value for VESNA..." %(self.player.player_number, self.current_transmitting_power) 
                #I want to keep the best response given by the formula
                self.best_response_untouched = self.current_transmitting_power
                #truncate the power
                self.current_transmitting_power = self.getTheNearestPower(self.current_transmitting_power)
            
                #make some list with iterations and calculated powers
                self.results_list.append([self.current_transmitting_power, self.best_response_untouched, received_power[1][0], "None", self.player.cost])
                self.queue_list.append(self.best_response_untouched)
                #we want to count how many iterations the algorithm used to reach the Nash equilibrium
                iterations+= 1
                
                #see if we have reached the equilibrium
                if not self.checkEquilibrium(equal_condition=False):
                    #the equilibrium has not been reached yet 
                    print "Player %d has not reached the Nash Equilibrium yet" %(self.player.player_number)
                    
                    #wait for the neighbor to finish his transmission
                    while self.neighborPowerAllocation.playerApp.isSendingAPacket():
                        print "Player %d : waiting for the neighbor to finish his transmission" %self.player.player_number
                        time.sleep(1)
                    
                    #generate at new power. This is needed because this way the neighbor player can see the change I made
                    #send a packet for a few seconds
                    self.playerApp.sendPacket(6)
                    #to be sure the neighbor will catch my generated signal,  wait for 1 second (this way I consider others delay that can appear within the testbed)
                    time.sleep(1)
                    #announce the other player about my change
                    self.alertNeighborAboutAChangeOfPower()
                else:
                    #that means equilibrium
                    print "Player %d : Equilibrium has been reached" %(self.player.player_number)
                    
                    #check if neighbor has reached equilibrium too
                    if(not self.neighborPowerAllocation.checkEquilibrium(equal_condition=False)):
                        print "Player %d : My neighbor has not reached the Nash equilibrium yet, send a packet again" %self.player.player_number
                        
                        #wait for the neighbor to finish his transmission
                        while self.neighborPowerAllocation.playerApp.isSendingAPacket():
                            print "Player %d : waiting for the neighbor to finish his transmission" %self.player.player_number
                            time.sleep(1)
                        
                        #send packet
                        self.playerApp.sendPacket(6)
                        time.sleep(1)
                        self.alertNeighborAboutAChangeOfPower()
                        continue
                    
                    #finish this game
                    self.neighborPowerAllocation.equilibriumDectected()
                    self.equilibriumDectected()
                    
            else:
                if self.equilibriumDetected:
                    print "Player %d Equilibrium. No events had been detected. Number of iterations:%d. Time passed: %.6f \n" %(self.player.player_number, iterations, (time.time() - process_start_time) - 45) 
                    print "Player %d power allocated: %.3f" %(self.player.player_number, self.current_transmitting_power)
                    
                    #write experiment results in a file
                    self.printIterationsToFile(self.results_list, "Using threshold with a 5 size queue, predicted gains")
                    if self.player.player_number == 1:
                        self.printStrategyTable(self.best_response_untouched, self.neighborPowerAllocation.best_response_untouched, iterations)
                    
		    while True:
			    time.sleep(1)

            time.sleep(0.05)
            
    def run(self):
        if self.game_type == 1:
            self.gameType1()
        elif self.game_type == 2:
            self.gameType2()
        elif self.game_type == 3:
            self.gameType3()
