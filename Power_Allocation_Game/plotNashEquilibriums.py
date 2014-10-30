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


import math
import numpy
import datetime
import os

from plot import  Plot
from matplotlib import pyplot as plot
from gainCalculations import GainCalculations

def plotNashEquilibriumAsAfunctionOfCost(c1=None, c2=None):
    #If you want to plot NE(c1) then , give c2 parameter, else,if you want to plot NE(c2) give c1 parameter
    
    #set paths where you have experimental results
    path1 = "/home/ciprian/Documents/Backup/NashEquilibriums/Player 1 NE/strategyTable.dat"
    path2 = "/home/ciprian/Documents/Backup/NashEquilibriums/Player 2 NE/strategyTable.dat"
    
     
    #see if the file exits
    if not os.path.exists(path1):
        print "%s doesn't exits" %path1
    elif not os.path.exists(path2): 
        print "%s doesn't exits" %path2
        return
    
    #check parameters
    if c1==None and c2 == None:
        print "None of the costs are set."
        return
    
    plot.ioff()
    plot.clf()
    plot.grid()
    
    plot.title("Strategies for players")
    plot.xlabel("Cost  (Ci)")
    plot.ylabel("Player strategy [dBm]")
    
    #change rc param
    plot.rcParams.update({'font.size': 22})
    
    ne_player1 = []
    ne_player2 = []
    
    #make lists for player 1 NE, that means c2 is fixed and c1 is varied
    if c2!=None:
        #open the file for reading
        f = open(path1, "r")
        
        #read first line, it's just a header
        f.readline()
        
        #c2 is fixed, c1 is varied (values from the file)
        ne_player1 = []
        c1_list = []
        
        while True:
            line = f.readline()
            if not line:
                break
            
            #example of line: c1= 1000   c2= 1000   Nash value player 1= -0.240737352 dBm    Nash value player 2= -1.266989792 dBm  Iterations= 9  h11= -74.884 dB h21= -88.312 dB  h22= -68.886 dB  h12= -74.700 dB  Player1Noise=6.497E-13  Player2Noise=6.497E-13  Date= 2013-09-09 10:41:58.540216
            line_list = line.split()
            
            #see if c2 from the file correspond with c2 from the parameter
            if(float(line_list[3]) == float(c2)):
                ne_player1.append(float(line_list[8]))
                c1_list.append(float(line_list[1]))
        
        #close the file
        f.close()
       
        if (len(ne_player1) !=0): 
            #sort the lists after costs. (Needed only for plot)
            ok=False
            while not ok:
                ok = True
                for i in range(0, len(c1_list)-1):
                    if c1_list[i]>c1_list[i+1]:
                        ok=False
                        #change costs
                        temp = c1_list[i]
                        c1_list[i] = c1_list[i+1]
                        c1_list[i+1] = temp
                        
                        #change powers corresponding with costs
                        temp = ne_player1[i]
                        ne_player1[i] = ne_player1[i+1]
                        ne_player1[i+1] = temp
              
            #now plot results
            plot.plot(c1_list, ne_player1, "-", color ="gray", alpha = 0.5)
            plot.plot(c1_list, ne_player1, "*r", label = "Player 1 strategy, c2=%d" %c2)
            
            plot.axis([min(c1_list)-100, max(c1_list)+100, min(ne_player1)-1, max(ne_player1)+1])
        else:
            print "The cost c2=%s couldn't be found in %s" %(c2, path1)
    
    #make lists for player 2 NE, that means c1 is fixed and c2 is varied
    if c1!=None:
        #c1 is fixed, c2 is varied (values from the file)
        #that means Nash equilibrium for player 2
        
        #open the file for reading
        f = open(path2, "r")
        
        #read the first line
        f.readline()
        
        ne_player2 = []
        c2_list = []
        
        #read the entire file
        while True:
            line = f.readline()
            if not line:
                break
            #example of line:c1= 1000   c2= 1000   Nash value player 1= -0.240737352 dBm    Nash value player 2= -1.266989792 dBm  Iterations= 9  h11= -74.884 dB h21= -88.312 dB  h22= -68.886 dB  h12= -74.700 dB  Player1Noise=6.497E-13  Player2Noise=6.497E-13  Date= 2013-09-09 10:41:58.540216
        
            line_list = line.split()
            #look in the file where c1 from the file=c1
            if(float(line_list[1]) == float(c1)):
                ne_player2.append(float(line_list[14]))
                c2_list.append(float(line_list[3]))
        
        #close the file
        f.close()
        
        if len(ne_player2):
            #sort the lists
            ok=False
            while not ok:
                ok = True
                for i in range(0, len(c2_list)-1):
                    if c2_list[i]>c2_list[i+1]:
                        ok=False
                        temp = c2_list[i]
                        c2_list[i] = c2_list[i+1]
                        c2_list[i+1] = temp
                        
                        temp = ne_player2[i]
                        ne_player2[i] = ne_player2[i+1]
                        ne_player2[i+1] = temp
            
            #now plot results   
            plot.plot(c2_list, ne_player2, "-", color ="gray", alpha = 0.5)
            plot.plot(c2_list, ne_player2, "o", label = "Player 2 strategy, c1=%d" %c1)
            plot.axis([min(c2_list)-100, max(c2_list)+100, min(ne_player2)-1, max(ne_player2)+1])
        else:
            print "The cost c1=%s couldn't be found in %s" %(c1, path2)
    if len(ne_player1)==0 and len(ne_player2)==0:
        return 
            
    plot.legend(loc = 'upper right', fontsize = 22)
        
    plot.show()        
    
def plotNashEquilibrums(): 
    path = "/home/ciprian/Documents/Backup/NashEquilibriums/c1=c2/23 Aug/strategyTable.dat"
    path_theoretical = "/home/ciprian/Documents/Backup/NashEquilibriums/c1=c2/Theoretical/strategyTable.dat"
    #path = "./iterations/strategyTable.dat"
    if not os.path.exists(path):
        print "%s doesn't exits" %path
        return 
    
    plot_theoretical_nash = True
    if not os.path.exists(path_theoretical):
        print "%s doesn't exits" %path_theoretical
        plot_theoretical_nash = False
    
    #open file with empirical experiments for reading
    f = open(path, "r")
    
    f.readline()
    #Define: nash_equilibrium = [ [c1,c2, ne1, ne2, ne1, ne2, ..], [c1, c2, ne1, ne2, ne1, ne2 ..]  ]
    nash_equilibriums = []

    max_ne1 = -float("inf")
    max_ne2 = -float("inf")
    min_ne1 = float("inf")
    min_ne2 = float("inf")

    #read strategy table file
    while True:
        line = f.readline()
        if not line:
            break
        
        line_list = line.split()
        try:
            c1 = float(line_list[1])
            c2 = float(line_list[3])
            
            if float(line_list[8])> max_ne1:
                max_ne1 = float(line_list[8])
            if float(line_list[8])< min_ne1:
                min_ne1 = float(line_list[8])
                
            if float(line_list[14])> max_ne2:
                max_ne2 = float(line_list[14])
            if float(line_list[14])< min_ne2:
                min_ne2 = float(line_list[14])  
            
            combination_found = False
            for i in range(0,len(nash_equilibriums)):
                if nash_equilibriums[i][0] == c1 and nash_equilibriums[i][1] == c2:
                    nash_equilibriums[i].append(float(line_list[8]))
                    nash_equilibriums[i].append(float(line_list[14]))
                    combination_found = True
 
            if not combination_found:
                nash_equilibriums.append([c1, c2, float(line_list[8]), float(line_list[14])])
                
        except:
            continue
    f.close()   
   
    if plot_theoretical_nash:
        #also, I want to plot the theoretically strategy. To the same thing
        f = open(path_theoretical, "r")
        f.readline()
        #nash_equilibrium = [ [c1,c2, ne1, ne2, ne1, ne2, ..], [c1, c2, ne1, ne2, ne1, ne2 ..]  ]
        nash_equilibriums_theoretical = []
        
        #read strategy table file
        while True:
            line = f.readline()
            if not line:
                break
            line_list = line.split()
            try:
                c1 = float(line_list[1])
                c2 = float(line_list[3])
                 
                combination_found = False
                for i in range(0,len(nash_equilibriums_theoretical)):
                    if nash_equilibriums_theoretical[i][0] == c1 and nash_equilibriums_theoretical[i][1] == c2:
                        nash_equilibriums_theoretical[i].append(float(line_list[8]))
                        nash_equilibriums_theoretical[i].append(float(line_list[14]))
                        combination_found = True
     
                if not combination_found:
                    nash_equilibriums_theoretical.append([c1, c2, float(line_list[8]), float(line_list[14])])
                    
            except:
                continue
        f.close()   
   
    #now plot results
    plot.ioff()
        
    plot.clf()
    plot.grid()
    
    plot.title("Nash Equilibria")
    plot.xlabel("Player 1 strategy [dBm]")
    plot.ylabel("Player 2 strategy [dBm]")
    
    #change rc param
    plot.rcParams.update({'font.size': 18})
    
    #plot empirical nash equilibria
    for i in range(0, len(nash_equilibriums)):
        tmp_x_list = []
        tmp_y_list = []
        for j in range(2, len(nash_equilibriums[i]), 2):
            tmp_x_list.append(nash_equilibriums[i][j])
            tmp_y_list.append(nash_equilibriums[i][j+1])
        plot.plot(tmp_x_list, tmp_y_list, "o", label = "c1=%d  c2=%d" %(nash_equilibriums[i][0], nash_equilibriums[i][1]))
    
    if plot_theoretical_nash: 
        for i in range(0, len(nash_equilibriums_theoretical)):
            tmp_x_list = []
            tmp_y_list = []
            for j in range(2, len(nash_equilibriums_theoretical[i]), 2):
                tmp_x_list.append(nash_equilibriums_theoretical[i][j])
                tmp_y_list.append(nash_equilibriums_theoretical[i][j+1])
            plot.plot(tmp_x_list, tmp_y_list, "o", color ="red", label = "c1=%d  c2=%d Simulation" %(nash_equilibriums_theoretical[i][0], nash_equilibriums_theoretical[i][1]))
          
    plot.axis([min_ne1-1, max_ne1+1, min_ne2-1, max_ne2+1])
    
    leg = plot.legend(loc = 'upper right', bbox_to_anchor=(1.05, 1.05), fontsize = 12)
    leg.get_frame().set_alpha(0.9)
        
    plot.show()
    
plotNashEquilibrums()
#plotNashEquilibriumAsAfunctionOfCost(c1=1000, c2 = 1000)
