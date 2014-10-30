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

# Authors: Andrei Toma
# 		Ciprian Anton
#

from matplotlib import pyplot as plot
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import dates
import os
import time
import matplotlib
import numpy
import math
import kalmanImplementation
import random

class Plot:
    #has several static method for plotting
         
    @staticmethod    
    def plotXYLists(x, y, title, xlabel, ylabel, ion = False): 
        #plots X and Y lists
        if ion==True:
            plot.ion()
        else:
            plot.ioff()
            
        plot.clf()
        plot.grid()
        plot.xlabel(xlabel)
        plot.ylabel(ylabel)
        
        plot.title(title)
        
        plot.plot(x, y)
        
        if ion==True:
            plot.draw()
        else:
            plot.show()
    
    @staticmethod    
    def plotList(y, title, xlabel, ylabel,ion): 
        #plots y lists

        if ion:
            plot.ion()
        else:
            plot.ioff()
        plot.clf()
        plot.grid()
        plot.xlabel(xlabel)
        plot.ylabel(ylabel)
        plot.title(title)
        
        plot.plot(y)
    
        if ion:
            plot.draw()
        else:
            plot.show()   
        
    @staticmethod
    def plotMultipleLines(x, y,labels, xlabel, ylabel,title, ion):
        #in this case, x: [[x_1],[x_2],[x_3]...] and y = [[y_1], [y_2],[y_3] ]
       
        if ion:
            plot.ion()
        else:
            plot.ioff()
        
        plot.clf()
        plot.grid()
        plot.title(title)
        plot.xlabel(xlabel)
        plot.ylabel(ylabel)
             
        for i in range(0, len(x)):
            plot.plot(x[i], y[i], "-" ,label= labels[i])
        
        plot.legend(loc = 'upper center')
         
        if ion:
            plot.draw()
        else:
            plot.show()   
                
    @staticmethod
    def plot2Subplots(y1, y2, labels1, labels2, xlabel, ylabel, title1, title2, c1, c2, ion, Truncated = False, SaveImg = True):        
        #in this case y1 and y2 = [[y_1], [y_2],[y_3] ].
        #example y1 = [[1,2,3],[0,1,2,4,5], ..]
        #use this for plotting iterations
        if ion:
            plot.ion()
        else:
            plot.ioff()
        plot.clf()
       
        #I want to make 2 sub plots. ax1 represents the first, ax2 represents the second
        ax1 = plot.subplot(211)
        ax2 = plot.subplot(212, sharex=ax1)
        
        ax1.grid()
        ax2.grid()
        
        #just a list with a few markers
        markers_list = ['-o', '-v', '-p', '-D', '-*']
        
        #plot first sub plot (y1)
        for i in range(0, len(y1)):
            ax1.plot(y1[i], random.choice(markers_list) ,label= labels1[i], linewidth = 1.5)
        
        
        #determine maximum length in y1, only last value matters
        max_length = -float("inf")
        max_y = -float("inf")
        min_y = float("inf")
        for i in y1:
            if len(i)>max_length:
                max_length = len(i)
            if i[-1] > max_y :
                max_y = i[-1]
            if i[-1] < min_y:
                min_y = i[-1]

        ax1.axis([0, max_length, min_y-3, max_y+3])
        ax1.legend(loc = "upper right",bbox_to_anchor=(1.1, 1.1))
        
        ax1.set_ylabel(ylabel)
        ax1.set_title(title1)
        
        #--------------------------------------------------
        #now do the same thing for y2 
        for i in range(0, len(y2)):
            ax2.plot(y2[i], random.choice(markers_list), label= labels2[i], linewidth = 1.5)
        
        #determine maximum length in y2, only last value matterss
        max_length = -float("inf")
        max_y = -float("inf")
        min_y = float("inf")
        for i in y2:
            if len(i)>max_length:
                max_length = len(i)
            if i[-1] > max_y :
                max_y = i[-1]
            if i[-1] < min_y:
                min_y = i[-1]
        
        ax2.axis([0, max_length, min_y-3, max_y+3])
        ax2.legend(loc = "upper right", bbox_to_anchor=(1.1, 1.1))
        ax2.set_xlabel(xlabel)
        ax2.set_ylabel(ylabel)
        ax2.set_title(title2)
       
        #maximize the window
        mng = plot.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        
        if SaveImg:
            fig = plot.gcf()
            fig.set_size_inches( (19, 11) )
            if Truncated:
                plot.savefig("./iterations/c1_%d-c2_%d/c1_%d-c2_%d-truncated.jpg" %(c1,c2,c1,c2), dpi=200)
            else:
                plot.savefig("./iterations/c1_%d-c2_%d/c1_%d-c2_%d-nontruncated.jpg" %(c1,c2,c1,c2), dpi=200)
                plot.savefig("./iterations/c1_%d-c2_%d-nontruncated.jpg" %(c1,c2), dpi=200)
            return  
        
        if ion:
            plot.draw()
        else:
            plot.show()  
            
    @staticmethod
    def plotGains(date_list, y_list, xlabel, ylabel, title, ion=False):
        #y_list in dB. date_list is a list of dates at which the measurements were made
        if ion:
            plot.ion()
        else:
            plot.ioff()
            
        plot.clf()
        plot.grid()
        
        plot.title(title)
        plot.xlabel(xlabel)
        plot.ylabel(ylabel)
        
        #determine minimum and maximum values of y list. Do this now because I will need it several times. 
        min_y_list = min(y_list)
        max_y_list = max(y_list)
        
        #change rc param
        plot.rcParams.update({'font.size': 22})
        
        #set yticks
        distance = math.fabs(math.fabs(max_y_list)-math.fabs(min_y_list))/16
        #round the distance to the nearest integer
        distance = round(distance) - .5
        distance = int(distance) + (distance>0)
        if distance <1:
            distance = 1
        
        plot.yticks(numpy.arange(min_y_list, max_y_list, distance))
        
        #plot values
        plot.plot(y_list , '-',color = "black", label = "Measured gain", linewidth = 1.3)
        plot.axis([0, len(y_list), min_y_list - 2, max_y_list +2])
        
        #plot average line
        k =0.00
        sum = 0.00
        for i in y_list:
            #do average in linear scale
            sum+= math.pow(10.00, float(i)/10.00)
            k+=1
        linear_average_gain = sum/k
        plot.axhline(10.00 * math.log10(linear_average_gain), color = 'r', linewidth = 2.2, label = "Average gain %.3f dB" %(10.00*math.log10(linear_average_gain)))
        
        #We want to shade the night measurements with a color, and the day measurements with other color
        #make 2 lists, which represents the intervals for day and night. day intervals : [ [a,b, day], [c,d, day] ,[e,f, day] ]
        day_intervals = []
        night_intervals = []
        
        #determine the night and day intervals
        for i in range(0, len(date_list)-1):
            #for day. We want to determine index interval y_list for which date_list has a day hours
            if (date_list[i].hour ==12 or date_list[i].hour == 13) and i==0 :
                first_index = i
            elif (date_list[i].hour == 12 or date_list[i].hour == 13) and (date_list[i-1].hour != 12 and date_list[i-1].hour != 13):
                first_index = i
                
            if (date_list[i].hour == 12 or date_list[i].hour == 13) and (date_list[i+1].hour != 12 and date_list[i+1].hour != 13):
                last_index = i
                day_intervals.append([first_index, last_index, date_list[i].day])
                
            if (date_list[i].hour == 12 or date_list[i].hour == 13) and (date_list[i+1].hour == 12 or date_list[i+1].hour == 13) and (i+1) == len(date_list)-1:
                last_index =i+1
                day_intervals.append([first_index, last_index, date_list[i].day])
            
            #same thing for night
            if (date_list[i].hour ==21 or date_list[i].hour == 22) and i==0 :
                first_index = i
            elif (date_list[i].hour == 21 or date_list[i].hour == 22) and (date_list[i-1].hour != 21 and date_list[i-1].hour != 22):
                first_index = i

            if (date_list[i].hour == 21 or date_list[i].hour == 22) and (date_list[i+1].hour != 21 and date_list[i+1].hour != 22):
                last_index = i
                night_intervals.append([first_index, last_index, date_list[i].day])
                
            if (date_list[i].hour == 21 or date_list[i].hour == 22) and (date_list[i+1].hour == 21 or date_list[i+1].hour == 22) and (i+1) == (len(date_list)-1):
                last_index =i+1
                night_intervals.append([first_index, last_index, date_list[i].day])
        
        #plot vertical span 
        for i in range(0, len(day_intervals)):
            plot.axvspan(day_intervals[i][0], day_intervals[i][1], color = "white", alpha = 0.1)
            
        for i in range(0, len(night_intervals)):
            plot.axvspan(night_intervals[i][0], night_intervals[i][1], color = "gray", alpha = 0.2)

        #plot arrows from maximum to minimum value of gains
        arrow_length = math.fabs(math.fabs(max_y_list) - math.fabs(min_y_list))
        plot.arrow(len(y_list)/2, min_y_list, 0, arrow_length, head_width = 0.02 * len(y_list), length_includes_head = True, color = "blue",head_length = arrow_length*0.05, linewidth = 2)
        plot.arrow(len(y_list)/2, max_y_list, 0, -arrow_length, head_width = 0.02 * len(y_list), length_includes_head = True, color = "blue", head_length = arrow_length*0.05, linewidth = 2)
        plot.text(len(y_list)/2 +0.5, min_y_list + 0.1*arrow_length, "%.3f dB" %arrow_length, fontsize = 22, weight = 600)
        
        #plot maximum and minimum lines
        plot.axhline(max_y_list, color = 'black', linestyle = "--")
        plot.text(0.4 * len(y_list), max_y_list +0.5 , "%.3f dB" % max_y_list, color = "red", weight = 600, fontsize = 22)
        plot.axhline(min_y_list, color = 'black', linestyle = '--')
        plot.text(0.4 * len(y_list), min_y_list - 1, "%.3f dB" % min_y_list, color = "red", weight = 600, fontsize = 22)
        
        #I want to plot the predicted gain value using the KalmanFilter. For this I need linear values
        y_list_linear = []
        for i in range(0, len(y_list)):
            #dB -> linear
            y_list_linear.append(math.pow(10.00, float(y_list[i])/10.00))
         
    
        #plot predicted gain using  Kalman filter
        y_list_predictedVer2 = kalmanImplementation.getPredictedValuesVer2(y_list_linear)
        for i in range(0, len(y_list_predictedVer2)):
            y_list_predictedVer2[i] = 10.00 * math.log10(y_list_predictedVer2[i])
        
        #now plot y_list_predictedVer2
        plot.plot(y_list_predictedVer2, '-', color = "yellow", label = "Predicted gain", linewidth = 2.2)
        
        #plot deviations? standard deviation or % from maximum deviation?
        #get standard deviation
        standard_deviation = kalmanImplementation.getStandardDeviation(y_list_linear)    
        plot.axhspan(10.00*math.log10(linear_average_gain-standard_deviation),10.00*math.log10(linear_average_gain+standard_deviation), facecolor='black', alpha=0.20)  
        
        #plot arrow
        arrow_length = 10.00*math.log10(linear_average_gain+standard_deviation) - 10.00*math.log10(linear_average_gain-standard_deviation)
        plot.arrow(len(y_list)/2 - 0.3*len(y_list)/2, 10.00*math.log10(linear_average_gain-standard_deviation), 0, arrow_length, head_width =  0.6*arrow_length, length_includes_head = True, color = "green",head_length = arrow_length*0.09, linewidth = 3)
        plot.arrow(len(y_list)/2 - 0.3*len(y_list)/2, 10.00*math.log10(linear_average_gain+standard_deviation), 0, -arrow_length, head_width =  0.6*arrow_length, length_includes_head = True, color = "green",head_length = arrow_length*0.09, linewidth = 3)
        plot.text(len(y_list)/2 - 0.3*len(y_list)/2, 10.00*math.log10(linear_average_gain+standard_deviation)+0.5, "%.3f dB" %arrow_length, color = "green", weight=600, fontsize = 22)
        
        #plot a text with number of measurements
        plot.text(2, min(y_list)-1, "Number of\nmeasurements:\n%d" %len(y_list), color = "black", weight = 700, fontsize = 22)
        
        leg = plot.legend(loc = 'upper right', bbox_to_anchor=(1.05, 1.05), fontsize = 22)
        leg.get_frame().set_alpha(0.7)
        
        #maximize the window
        mng = plot.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        
         
        fig = plot.gcf()
        fig.set_size_inches( (19, 11) )
        try:
            os.mkdir("./gain plots")
        except:
            pass
        plot.savefig("./gain plots/%s.jpg" %(title), dpi=250)
        #return
        if ion:
            plot.draw()
        else:
            plot.show()
        