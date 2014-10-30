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
from player import Player
from gainCalculations import GainCalculations


    
def plotIterationsAsAFunctionOfCost(c1=None, c2=None):
    path1 = "/home/ciprian/Documents/Backup/NashEquilibriums/Player 1 NE/strategyTable.dat"
    path2 = "/home/ciprian/Documents/Backup/NashEquilibriums/Player 2 NE/strategyTable.dat"
    
    path1 = "./iterations/strategyTable.dat"
    path2 = "./iterations/strategyTable.dat"
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
    
    plot.title("Iterations (Cost)")
    plot.xlabel("Cost  (Ci)")
    plot.ylabel("Iterations")
    
    #change rc param
    plot.rcParams.update({'font.size': 22})
    
    #make lists for player 1 NE, that means c2 is fixed and c1 is varied
    if c2!=None:
        #open the file for reading
        f = open(path1, "r")
        
        #read first line, it's just a header
        f.readline()
        
        #c2 is fixed, c1 is varied (values from the file)
        iterations_player1 = []
        c1_list = []
        
        while True:
            line = f.readline()
            if not line:
                break
        
            line_list = line.split()
            
            #see if c2 from the file correspond with c2 from the parameter
            if(float(line_list[3]) == float(c2)):
                iterations_player1.append(float(line_list[17]))
                c1_list.append(float(line_list[1]))
        
        #close the file
        f.close()
        
        '''
        #sort the lists
        ok=False
        while not ok:
            ok = True
            for i in range(0, len(c1_list)-1):
                if c1_list[i]>c1_list[i+1]:
                    ok=False
                    temp = c1_list[i]
                    c1_list[i] = c1_list[i+1]
                    c1_list[i+1] = temp
                    
                    temp = ne_player1[i]
                    ne_player1[i] = ne_player1[i+1]
                    ne_player1[i+1] = temp
        
        '''  
        
        #now plot results
        #plot.plot(c1_list, ne_player1, "-", color ="gray", alpha = 0.5)
        plot.plot(c1_list, iterations_player1, "*r", label = "c2=%d" %c2)
        
        plot.axis([min(c1_list)-100, max(c1_list)+100, min(iterations_player1)-3, max(iterations_player1)+3])
        
    #make lists for player 2 NE, that means c1 is fixed and c2 is varied
    if c1!=None:
        #c1 is fixed, c2 is varied (values from the file)
        #that means Nash equilibrium for player 2
        
        #open the file for reading
        f = open(path2, "r")
        
        #read the first line
        f.readline()
        
        iterations_player2 = []
        c2_list = []
        
        #read the entire file
        while True:
            line = f.readline()
            if not line:
                break
        
            line_list = line.split()
            #look in the file where c1 from the file=c1
            if(float(line_list[1]) == float(c1)):
                iterations_player2.append(float(line_list[17]))
                c2_list.append(float(line_list[3]))
        
        #close the file
        f.close()
        
        '''
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
        '''
        #now plot results
           
        #plot.plot(c2_list, ne_player2, "-", color ="gray", alpha = 0.5)
        plot.plot(c2_list, iterations_player2, "o", label = "c1=%d" %c1)
        plot.axis([min(c2_list)-100, max(c2_list)+100, min(iterations_player2)-1, max(iterations_player2)+1])
        
    plot.legend(loc = 'upper right', fontsize = 22)
        
    plot.show()        
    f.close()
    return    
    
plotIterationsAsAFunctionOfCost(c1 = 1000)