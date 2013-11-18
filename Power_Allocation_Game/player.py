from node import Node
from playerApp import PlayerApp
from powerAllocation import  PowerAllocation
from gainCalculations import GainCalculations
import kalmanImplementation
import time
import math
import random

class Player:
    #this class defines a player. A player also has a PlayerApp object and a PowerAllocationObject
    
    #player power cost [1/w]
    cost = 0
    
    #channel gains. Must be dimension less
    direct_gain = 0.00
    cross_gain = 0.00
    
    #noise power [W]. This must be measured
    noise_power = 6.49721018016e-13
    
    #player number. This is how we can identify a player
    player_number = None
    
    #playerApp
    playerApp = None
    
    #powerAllocation
    powerAllocation = None
    
    #Neighbor player object
    neighbor_player = None
    
    def __init__(self, coordinator_id, tx_node_id, rx_node_id, cost, player_number, game_Type = 0):
        print "Player version 2" 
        
        #save coordinator_id
        self.coordinator_id = coordinator_id
        
        #save cost
        self.cost = cost
        
        #save player_number
        self.player_number = player_number
        
        #define 2 nodes. We consider that a player has only 1 user, which means 1 tx and one rx. With these nodes a player can send and receive data to/from the nodes
        self.tx_node = Node(coordinator_id, tx_node_id)
        self.rx_node = Node(coordinator_id, rx_node_id)
        
        #define playerApp for this player
        self.playerApp = PlayerApp(self)
        
        #define powerAllocation for this player
        self.powerAllocation = PowerAllocation(self, self.playerApp, gameType=game_Type)
        
        #set link from playerApp to powerAllocation
        self.playerApp.setPowerAllocationOjbect(self.powerAllocation)
        
    def setNeighborPlayer(self, Player):
        self.neighbor_player = Player
        self.powerAllocation.setNeighborPowerAllocationObject(Player.powerAllocation)    
        
    def measureGains(self):
        #takes instant channel gains, it does not apply any filter or anything else
        #measure direct gain
        self.direct_gain = GainCalculations.calculateInstantGain(self.coordinator_id, self.tx_node.node_id, self.rx_node.node_id, measuring_freq=2420e6, saveresults=False, transmitting_duration=4)
        #measure cross gain
        self.cross_gain = GainCalculations.calculateInstantGain(self.coordinator_id, self.neighbor_player.tx_node.node_id, self.rx_node.node_id, measuring_freq=2420e6, saveresults=False, transmitting_duration=6)
        
    def startGame(self):
        self.powerAllocation.start()    
        
    def unbalance(self, new_power_dBm = random.randrange(-55, 0, 1)):
        self.powerAllocation.changeCurrentPower(new_power_dBm)
    
    def printPlayerInfo(self):
        #just print some info about the player
	print "\x1b[1m"
	print "*" * 79
	print "Player %d info:" % (self.player_number,)
        print "tx=%d  rx=%d  direct gain=%.6fE-8 (%.3f dB)   cross gain=%.12fE-8 (%.3f dB)  cost = %.3f   noise power = %.6fE-12" %(self.tx_node.node_id, self.rx_node.node_id, self.direct_gain * 1e8, 10.00*math.log10(self.direct_gain),self.cross_gain * 1e8, 10.00*math.log10(self.cross_gain), self.cost, self.noise_power * 1e12)
	print "*" * 79
	print "\x1b[0m"
        self.powerAllocation.printPowerAllocationInfo()
        self.playerApp.printPlayerAppInfo()
        
    def setCost(self, cost):
        old_cost = self.cost
        self.cost = cost
        print "Player %d changed its cost: %.3f. Old cost: %.3f" %(self.player_number, self.cost, old_cost)
        
    def setPriority(self, priority):
        self.priority = priority 
        
    def setDirectGain(self, direct_gain):
        self.direct_gain = direct_gain
    
    def setCrossGain(self, cross_gain):
        self.cross_gain = cross_gain
    
    def setDirectdBGain(self, direct_gain_dB):
        self.direct_gain = math.pow(10.00, direct_gain_dB/10.00)
        
    def setCrossdBGain(self, cross_gain_dB):
        self.cross_gain = math.pow(10.00, cross_gain_dB/10.00)
        
    def setNoisePower(self, noise_power_w):
        self.noise_power = noise_power_w
        
    def setNoisedBmPower(self, noise_power_dBm):
        self.noise_power = math.pow(10.00, noise_power_dBm/10.00)*0.001
    
        
        
    
