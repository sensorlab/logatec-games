import math
import numpy
import datetime
import os
import time
import kalmanImplementation

from matplotlib import pyplot as plot
from player import Player
from gainCalculations import GainCalculations

def getBi(cost, Prx_W, hii_db):
    #best response = 1/c - (I+N)/hii
    best_response = (1.00/float(cost)) - (Prx_W/math.pow(10.00, hii_db/10.00))
    #return best response in dBm
    try:
        return 10.00*math.log10(best_response/0.001)
    except:
        return None

def getMin(list):
    #returns the  minimum value from the list
    min = float("inf")
    for i in list:
        if i<min:
            min=i
        
    return min

def getMax(list):
    #returns the maximum value from the list
    max = -float("inf")
    for i in list:
        if i>max:
            max=i
        
    return max

def bestResponseAsAFunctionOfDirectGain():
    #formula to test:  Bi = (1/c) - (Prx/hii), where c is constant, Prx= ct
    #define a player
    player = Player(10001, 25, 2, 1000.00, 1)
    #player = Player(10001, 16, 17, 1000.00, 2)
    
    #get min and max channel gains measured until 23 august
    tmp = GainCalculations.getMinMaxGain(player.coordinator_id, player.tx_node.node_id, player.rx_node.node_id, year=2013, month=8, day=23)
    #tmp = [min linear gain, maximum linear gain]
    min_hii = 10.00*math.log10(tmp[0])
    max_hii = 10.00*math.log10(tmp[1])
    
    #define a hii array
    hii = numpy.arange(min_hii, max_hii, 0.05)
    
    #find max Prx_dBm in which Bi > -55 dBm
    Prx_dBm = -100
    
    while True:
        tmp_bi = getBi(player.cost, math.pow(10.00, Prx_dBm/10.00)*0.001, min_hii)
        if tmp_bi is None or tmp_bi<-55:
            #return to the previous Prx_dBm
            Prx_dBm-=0.0001
            break
        Prx_dBm+=0.0001
    
    average_gain = GainCalculations.getAverageGain(player.coordinator_id, player.tx_node.node_id, player.rx_node.node_id, year=2013, month=8, day=23)
    standard_deviation = GainCalculations.getStandardDeviation(player.coordinator_id, player.tx_node.node_id, player.rx_node.node_id, year=2013, month=8, day=23)
    
    #now plot results 
    plot.ioff()
    plot.clf()
    plot.grid()
    
    plot.title("B%d=f(h%d%d, I+N)" %(player.player_number, player.player_number, player.player_number))
    plot.xlabel("h%d%d [dB]" %(player.player_number, player.player_number))
    plot.ylabel("B%d [dBm]" %(player.player_number))

    #change rc param
    plot.rcParams.update({'font.size': 20})

    #I just want to add a text to legend
    plot.plot([0], [0], alpha = 0, label = "c%d=%d" %(player.player_number, player.cost))
    
    #now plot bi 
    Prx_crt = Prx_dBm
    Prx_step = 3
    Prx_inf = Prx_crt - 10
    max_bi = -float("inf")
    min_bi = float("inf")
    
    markers = [".", "*", "+", "h", "x", "_"]
    marker_index = 0
    while Prx_crt >= Prx_inf:   
        Bi = []
        for i in hii:
            best_response = getBi(player.cost, math.pow(10.00, Prx_crt/10.00)*0.001, i)
            Bi.append(best_response)
            if best_response > max_bi: max_bi = best_response
            if best_response < min_bi: min_bi = best_response
        plot.plot(hii, Bi, linewidth = 2.5, label = "Prx %.2f dBm" %(Prx_crt), marker = markers[marker_index], markersize = 5)
        if marker_index<len(markers):
            marker_index+=1
        else:
            marker_index = 0
        Prx_crt-=Prx_step
    
    #set axis limits
    plot.axis([min(hii)-0.5, max(hii)+0.5, min_bi-2, max_bi+2])
       
    #set ticks
    plot.xticks(numpy.arange(min(hii),max(hii), 2))
    plot.yticks(numpy.arange(min_bi, max_bi, 2)) 
        
    #plot a vertical line with the average gain
    plot.vlines(10.00*math.log10(average_gain), plot.axis()[2], plot.axis()[3], "red", label = "Mean gain=%.2f dB" %(10.00*math.log10(average_gain)), linestyle = "--", linewidth = 2)
    
    #plot vertical lines with the +- standard deviation
    max_std_hii = 10.00*math.log10(average_gain+standard_deviation)
    min_std_hii = 10.00*math.log10(average_gain-standard_deviation)
    #plot.vlines(min_std_hii, plot.axis()[2], plot.axis()[3], "black", linestyle = "--", linewidth = 1)
    #plot.vlines(max_std_hii, plot.axis()[2], plot.axis()[3], "black", linestyle = "--", linewidth = 1)
    
    #plot some spans for +- standard deviation
    plot.axvspan(min_std_hii, max_std_hii, facecolor = "gray", alpha = 0.2)
    #Plot horizontal arrows
    
    #plot arrows for +- standard deviation
    arrow_length = math.fabs(max_std_hii - min_std_hii)

    plot.arrow(min_std_hii, min_bi + 1, arrow_length, 0, head_width = 0.02*(math.fabs(max(hii)-min(hii))), length_includes_head = True, color = "green",head_length = 0.02*(math.fabs(max(hii)-min(hii))), linewidth = 1.0)
    plot.arrow(max_std_hii, min_bi + 1, -arrow_length, 0, head_width = 0.02*(math.fabs(max(hii)-min(hii))), length_includes_head = True, color = "green",head_length = 0.02*(math.fabs(max(hii)-min(hii))), linewidth = 1.0)
    plot.text(min_std_hii+arrow_length/3, min_bi +1.1, "%.3f dB" %arrow_length, fontsize = 18, color = "green")
    
    
    #plot horizontal lines for best response variation
    #plot.hlines(getBi(player.cost, math.pow(10.00, Prx_dBm/10.00)*0.001, max_std_hii), min(hii), max(hii), color = "black", linestyle = "--", linewidth = 1)
    #plot.hlines(getBi(player.cost, math.pow(10.00, Prx_dBm/10.00)*0.001, min_std_hii), min(hii), max(hii), color = "black", linestyle = "--", linewidth = 1)
    #plot.axhspan(getBi(player.cost, math.pow(10.00, Prx_dBm/10.00)*0.001, min_std_hii), getBi(player.cost, math.pow(10.00, Prx_dBm/10.00)*0.001, max_std_hii), facecolor = "blue", alpha = 0.1)
    
    #plot arrows for best response variation
    #max_std_Bi = getBi(player.cost, math.pow(10.00, Prx_dBm/10.00)*0.001, max_std_hii)
    #min_std_Bi = getBi(player.cost, math.pow(10.00, Prx_dBm/10.00)*0.001, min_std_hii)
    #arrow_length = math.fabs(max_std_Bi - min_std_Bi)
    #plot.arrow(min(hii) +0.5, max_std_Bi, 0, -arrow_length, head_width = 0.01*(math.fabs(max(hii)-min(hii))), length_includes_head = True, color = "blue", head_length = 0.01*(math.fabs(max(hii)-min(hii))), linewidth = 1.3)
    #plot.arrow(min(hii) +0.5, min_std_Bi, 0, +arrow_length, head_width = 0.01*(math.fabs(max(hii)-min(hii))), length_includes_head = True, color = "blue", head_length = 0.01*(math.fabs(max(hii)-min(hii))), linewidth = 1.3)
    #plot.text(min(hii) +0.5, max_std_Bi, "%.3f dBm" %arrow_length, fontsize = 18, weight = 500, color = "blue")
    

    leg = plot.legend(loc = "center right", fontsize = 18, bbox_to_anchor=(1, 0.5))
    leg.get_frame().set_alpha(0.6)

    #maximize the window
    mng = plot.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())
    
    fig = plot.gcf()
    fig.set_size_inches( (19, 11) )
    #plot.savefig("/home/ciprian/Pictures/best response/%s%d.jpg" %("bi_f(hii)_player", player.player_number), dpi=250)

    plot.show() 

def bestResponseAsAFunctionOfRx():
    player = Player(10001, 25, 2, 1000.00, 1)
    
    #get gain measurements until 23 august
    player.setDirectGain(GainCalculations.getAverageGain(player.coordinator_id, player.tx_node.node_id, player.rx_node.node_id, year=2013, month=8, day=23))
    
    #find max Prx_dBm in which Bi > -55 dBm
    Prx_dBm = -100
    
    while True:
        tmp_bi = getBi(player.cost, math.pow(10.00, Prx_dBm/10.00)*0.001, 10.00*math.log10(player.direct_gain))
        if tmp_bi is None or tmp_bi<-55:
            Prx_dBm-=0.001
            break
        Prx_dBm+=0.0001
    
    #now plot results 
    plot.ioff()
    plot.clf()
    plot.grid()
    
    plot.title("B%d=f(I+N)"  %(player.player_number))
    plot.xlabel("I+N [dBm]")
    plot.ylabel("B%d [dBm]" %(player.player_number))
    
    Prx_crt = Prx_dBm
    Prx_inf = Prx_dBm-20
    Prx_step = 0.001
    
    Bi = []
    Prx = []
    while Prx_crt>=Prx_inf:  
        best_response = getBi(player.cost, math.pow(10.00, Prx_crt/10.00)*0.001, 10.00*math.log10(player.direct_gain))
        Bi.append(best_response)
        Prx.append(Prx_crt)
        
        Prx_crt-=Prx_step    
        
    
    plot.plot(Prx, Bi, label = "h%d%d=%.1f dBm" %(player.player_number,player.player_number,10.00*math.log10(player.direct_gain)), linewidth = 2) 
    plot.axis([min(Prx)-1, max(Prx)+1, min(Bi)-1, max(Bi)+1])
    
    leg = plot.legend(loc = 'upper right', fontsize = 18)
    leg.get_frame().set_alpha(0.6)
    
    plot.show()
    
def bestResponseAsAfunctionOfCostAndPrx():
    #plot best response variation as function of I+N and cost
    player = Player(10001, 25, 2, 1000.00, player_number=1, game_Type=0)
    #give the node id which cause interference to player
    tx2_node_id = 16
    
    #I want to determine the maximum level of interference 
    #average direct gain
    hii = GainCalculations.getAverageGain(player.coordinator_id, player.tx_node.node_id, player.rx_node.node_id, year=2013, month=8, day=23)
    #maximum cross gain
    hji = GainCalculations.getMinMaxGain(10001, tx2_node_id, player.rx_node.node_id, year=2013, month=8, day=24)
    #get average noise
    noise = GainCalculations.getAverageNoise(player.coordinator_id, player.tx_node.node_id, player.rx_node.node_id, year=2013, month=8, day=23)
    
    max_interference_and_noise = 0.001*hji[1] + noise
    max_interference_and_noise = 10.00*math.log10(max_interference_and_noise/0.001)
    
    interference_and_noise = numpy.arange(max_interference_and_noise, max_interference_and_noise-10, -2)
    cost = numpy.arange(100, 10000, 0.1)
    
    #now plot results 
    plot.ioff()
    plot.clf()
    plot.grid()
    
    plot.title("B%d (c%d, I+N)" %(player.player_number, player.player_number))
    plot.xlabel("c%d" %(player.player_number))
    plot.ylabel("B%d [dBm]" %(player.player_number))
    
    for i in interference_and_noise:
        tmp_list = []
        tmp_cost = []
        for c in cost:
            tmp_bi = getBi(c, math.pow(10.00, i/10.00)*0.001, 10.00*math.log10(hii))
            if tmp_bi!=None:
                tmp_list.append(tmp_bi)
                tmp_cost.append(c)
                
        plot.plot(tmp_cost, tmp_list, label = "I+N=%.1f dBm" %i)
    
    plot.plot([],[],label = "h%d%d = %.3f dB" %(player.player_number, player.player_number, 10.00*math.log10(hii))) 
       
    plot.axhspan(-55, 0, alpha = 0.1)
        
    plot.legend(bbox_to_anchor=(1.05, 1.05))
    plot.show()

#bestResponseAsAfunctionOfCostAndPrx()
#bestResponseAsAFunctionOfDirectGain()
#bestResponseAsAFunctionOfRx()   