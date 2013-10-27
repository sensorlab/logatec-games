from player import Player
from gainCalculations import GainCalculations
from livePlot import gameLivePlot
import numpy
import iterations
import math
import time


def checkConvergence(h11, h12, h21, h22):
    #h11 and h22 direct gains, linear values
    #h12 and h21 cross gains : hcross = hji
    #check if hji/hii > 1/M where j!=i
    if ( (h21 / h11 ) >= (1/2.00) ):
        print "System is not convergent: h21/h11 = %.3f" %(h21/h11)
        return False
    
    if ( (h12/h22) >= (1/2.00)):
        print "System is not convergent: h12/22 = %.3f" %(h12/h22)
        return False
        
    print "System is convergent: h21/h11 = %.3f    and       h12/22 = %.3f\n" %(h21/h11, h12/h22)
    return True
    

def main():
    
        #define two players, chose gameType as the following: 1-implementation 1 (theoretical) ; 2 - implementation 2(practically form 1);  3 - implementation 3(practically form 2) - recommended
        player1 = Player(10001, 25, 2, 1000.00, 1, game_Type=3)
        player2 = Player(10001, 16, 17, 1000.00, 2, game_Type=3)
        
        #update gains
        #player1.measureGains()
        #player2.measureGains()
        #player1.setDirectGain(GainCalculations.getAverageGain(player1.coordinator_id, player1.tx_node.node_id, player1.rx_node.node_id, year=2013, month=8, day=23))
        #player1.setCrossGain(GainCalculations.getAverageGain(player1.coordinator_id, player2.tx_node.node_id, player1.rx_node.node_id, year=2013, month=8, day=23))
        
        #player2.setDirectGain(GainCalculations.getAverageGain(player2.coordinator_id, player2.tx_node.node_id, player2.rx_node.node_id, year=2013, month=8, day=23))
        #player2.setCrossGain(GainCalculations.getAverageGain(player2.coordinator_id, player1.tx_node.node_id, player2.rx_node.node_id, year=2013, month=8, day=23))
        player1.setDirectdBGain(-77)
        player1.setCrossdBGain(-85)
        
        player2.setDirectdBGain(-78)
        player2.setCrossdBGain(-83)
        
        #if you want to see some info about players
        player1.printPlayerInfo()
        player2.printPlayerInfo()
        
        #check convergence. See if the topology suits the game conditions
        if not checkConvergence(player1.direct_gain, player2.cross_gain, player1.cross_gain, player2.direct_gain):
            return
        
        #set links between players. (They have to communicate one with each other)
        player1.setNeighborPlayer(player2)
        player2.setNeighborPlayer(player1)
        
        livePlot = gameLivePlot(player1, player2)
    
        #start live plotting
        livePlot.startPloting()
    
        #start Power Allocation threads
        player1.startGame()
        player2.startGame()
        
        
        
        time.sleep(3)
        #trigger an event by changing the power of one player
        player1.unbalance()
        
        #wait for the threads to finish
        while player1.powerAllocation.isAlive() or player2.powerAllocation.isAlive() or livePlot.is_alive():
            time.sleep(3)     
       
        
        #if you want to plot the results     
        iterations.plotIterations(player1.player_number, player1.tx_node.node_id, player1.rx_node.node_id, player2.player_number, player2.tx_node.node_id, player2.rx_node.node_id, int(player1.cost), int(player2.cost), TruncatedValues=False, saveImage=True)
        
        
        choice = raw_input("Do you want to start PlayerApp threads(sends packets continuously) - yes/no:")
        if choice.lower() == "yes":
            player1.playerApp.start()
            player2.playerApp.start()
        
        
main()