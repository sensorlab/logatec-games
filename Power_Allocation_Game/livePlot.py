#this file contains code for plotting the game power in live mode
import threading
import time
import numpy
from matplotlib import pyplot as plot

class gameLivePlot (threading.Thread):
    
    #need two players
    player1 = None
    player2 = None

    #players best response
    player1_bi = []
    player2_bi = []

    def __init__(self, player1, player2):
        threading.Thread.__init__(self)
        self.player1 = player1
        self.player2 = player2

        
    def startPloting(self):
        self.start();
               
    def getNearestDecimal(self, value):
        for i in range(value+1, 200):
            if int( (int(i)/10)*10) == int(i):
                return i
           
    def getPlayer1Bi(self):
        #check if there is a difference between local best response (player1_bi) and power allocation best response
        tmp_bi = []
        for i in range(0, len(self.player1.powerAllocation.results_list)):
            #append only untouched best response
            tmp_bi.append(float(self.player1.powerAllocation.results_list[i][1]))
        
        return tmp_bi
    
    def getPlayer2Bi(self):
        #check if there is a difference between local best response (player2_bi) and power allocation best response
        tmp_bi = []
        for i in range(0, len(self.player2.powerAllocation.results_list)):
            #append only untouched best response
            tmp_bi.append(float(self.player2.powerAllocation.results_list[i][1]))
        
        return tmp_bi
          
    
        
    def run(self):
        #interactive plot
        plot.ion()
        #create a figure
        fig1 = plot.figure("Best response evolution")
        
        while True:
            #says if there was a change in data (new best response)
            update_plot = False
            
            #get bi from power allocation thread
            tmp_bi = self.getPlayer1Bi()
            
            #check if there is a difference between local best response and power allocation best response
            if (self.player1_bi != tmp_bi):
                #there was a change
                self.player1_bi = tmp_bi
                update_plot = True
                
            #get data from player 2
            tmp_bi = self.getPlayer2Bi()
            if (self.player2_bi != tmp_bi):
                #there was a change
                self.player2_bi = tmp_bi
                update_plot = True
                
            if update_plot:
                #replot data
                plot.clf()
                #create axis
                ax1 = fig1.add_subplot(211)
                
                ax1.grid()
                ax1.set_title("Best response evolution")
                ax1.set_xlabel("Iterations")
                ax1.set_ylabel("Power [dBm]")
                
                ax1.plot(self.player1_bi, color = 'red', marker = 'o', label="Player 1")
                ax1.plot(self.player2_bi, color = 'green', marker = 'o', label = "Player 2")
                
                reference_bi = self.player1_bi[-1]
                if self.player2_bi[-1] < reference_bi:
                    reference_bi = self.player2_bi[-1]
                
                
                if(len(self.player1_bi) > len(self.player2_bi)):
                    ax1.axis([0, self.getNearestDecimal(len(self.player1_bi)), reference_bi -6, 1 ])
                else:
                    ax1.axis([0, self.getNearestDecimal(len(self.player2_bi)), reference_bi -6, 1 ])
                    
                ax1.legend(loc = "upper right", bbox_to_anchor=(1.1, 1.1))
                
                ax2 = fig1.add_subplot(212)
                ax2.grid()
                ax2.set_xlabel("Player 1 - Power [dBm]")
                ax2.set_ylabel("Player 2 - Power [dBm]")
                
                min_length = len(self.player1_bi)
                if len(self.player2_bi) < min_length:
                    min_length = len(self.player2_bi)
                
                try:
                    ax2.plot(self.player1_bi[0:min_length], self.player2_bi[0:min_length], 'o', color="gray", alpha=0.7, label="Previous power set")
                    ax2.plot([self.player1_bi[-1]], [self.player2_bi[-1]], 'or', label="Current power set")
                except:
                    pass
                
                ax2.axis([self.player1_bi[-1]-3, self.player1_bi[-1] +3, self.player2_bi[-1]-3, self.player2_bi[-1]+3])
                ax2.legend(loc = "upper right", bbox_to_anchor=(1.1, 1.1))
                plot.draw()
                
            if( not self.player1.powerAllocation.is_alive() and not self.player2.powerAllocation.is_alive()):
                #wait 10 seconds before closing the plot
                time.sleep(10)
                plot.close()
                break
        
            time.sleep(0.5)            
