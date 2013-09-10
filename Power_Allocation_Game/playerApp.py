from node import Node

import threading
import time
import math
import random

class PlayerApp(threading.Thread):
    #This class represents the application part. Here we generate the signal, whenever we want.
    #This class must have a Player object and a PowerAllocation object in order to work
        
    #transmitting_start_time [s].I use this to know when was the moment of the last signal generation. It is important that when I generate a new signal the previous  generated signal to be finished
    start_gen_time = 0
    
    #transmitting duration [s]. For how much time will a generator transmit signal. This can be changed during the program
    transmitting_duration = 6
    
    #frequency we are using in experiments [Hz]
    frequency = 2420e6
    
    #current transmitting power [dBm]. This power will be updated before we send any packet ( generate signal)
    current_transmitting_power = 0.00
    
    def __init__(self, playerObject, frequency = 2420e6):
        print "Player app version 2"
        threading.Thread.__init__(self)
        
        #save player object. From this object I have the nodes which I am working with
        self.player = playerObject
        
        #save frequency
        self.frequency = frequency
        
    def printPlayerAppInfo(self):
        print "PlayerApp associated to player %d" %(self.powerAllocation.player.player_number)    
        
    def setPowerAllocationOjbect(self, powerAllocation):
        #An object of power Allocation. This way, this object can communicate with the user powerAllocation object.
        #From this powerAllocation Object, this playerApp will take the allowed transmission power
        self.powerAllocation = powerAllocation      
         
    def getTransmittingPower(self):
        #returns current transmitting power
        return self.current_transmitting_power
         
    def sleepUntilSignalGenerationStops(self):
        #sleep until the previous transmission stops
        #print "Player %d: Time passed from the last start generation: %f" %(self.player.player_number ,time.time() - self.start_gen_time)
        if ( (time.time() - self.start_gen_time) < self.transmitting_duration):
            #that means we have to wait
            print "Player %d: Sleep for %f until signal generation stops" %(self.player.player_number ,math.ceil(self.transmitting_duration - (time.time() - self.start_gen_time)))
            time.sleep(math.ceil(self.transmitting_duration - (time.time() - self.start_gen_time)))
        return
    
    def isSendingAPacket(self):
        #returns true if it is an ongoing transmission
        if (time.time() - self.start_gen_time) < (self.transmitting_duration+1):
            return True
        else:
            return False 
    
    def sendPacket(self, transmitting_duration):
        #before we send a new packet, we must wait for the previous transmission to be finished
        self.sleepUntilSignalGenerationStops()
        
        #now generate signal. Get the transmitting power from the power allocation object
        self.current_transmitting_power = self.powerAllocation.getTransmittingPower()
        
        retry_number = 0
        while True:
            try:
                #change transmitting duration
                self.transmitting_duration = transmitting_duration
                
                self.player.tx_node.setGeneratorConfiguration(self.frequency, self.current_transmitting_power)
                self.player.tx_node.generatorStart(time.time(), self.transmitting_duration)
                
                #set the time of last signal generated
                self.start_gen_time = time.time()
                print "\nPlayer %d is transmitting with %.6f dBm for %.3f seconds \n" %(self.player.player_number, self.current_transmitting_power, self.transmitting_duration)
                break
            except :
                retry_number += 1
                if retry_number>=10 :
                    print "Player %d cannot transmit at the  specified configuration. Number of attempts: %d" %(self.player.player_number, retry_number)
                    break
                print "Player %d failed to transmit at the  specified configuration. Retry %d" %(self.player.player_number, retry_number)
                continue
        return 
    def run(self):
        while True:
            #wait until previous transmission is over
            if self.isSendingAPacket():
                time.sleep(1)
                continue
            else:
                time.sleep(random.randrange(0, 15, 1))
                self.sendPacket(transmitting_duration=random.randrange(5,10,1))
            