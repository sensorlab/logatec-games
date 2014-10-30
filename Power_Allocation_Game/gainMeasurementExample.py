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


#Here are a few simple examples of how you can use the GainCalculation class

from gainCalculations import GainCalculations
import math

def performGainMeasurement():
    #You can do a gain measurement at any time you want. You can save the results in a file if you want to check them later
    #You have to specify the coordinator_id , transmitter's node id, receiver's node id
    #Optional you can specify at which frequency to measure(2420Mhz default) , to or not to save the results, and how long should the generator transmit a signal (recommended to be at least 5 seconds, default value=10)
    gain = GainCalculations.calculateInstantGain(10001, 25, 2, measuring_freq=2422e6, saveresults=False, transmitting_duration=5)
    #returned gain is in linear scale. 
    print gain
    print "%.3f dB" %(10.00*math.log10(gain))
    
def plotSavedGains():
    #If you made several gain measurements, you can plot them
    #You can apply a filter and take into account only gains before the date mentioned. If no date is mentioned, then all saved measurements will be plotted
    GainCalculations.plotGains(10001, 25, 2)
    
def getAFewParameters():
    #From the measured gain, you can get a few results
    #If you just want to get a list with measured gains:
    print GainCalculations.getFileResults(10001, 25, 2)
    #You will find informations about: calculated gain, received RSSI, Noise power, transmitted power, date
    
    #if you just want the average gain:
    print GainCalculations.getAverageGain(10001, 25, 2)
    print "%.3f dB" %(10.00*math.log10(GainCalculations.getAverageGain(10001, 25, 2))) 
    
    #if you just want to find info about the noise power
    GainCalculations.getAverageNoise(10001, 25, 2)
    GainCalculations.getMinMaxNoise(10001, 25, 2)
    
    #there are others useful methods in GainCalculation class, I will not mention all of them here, you can find all of them just by looking in GainCalculation class

#uncomment the method you want to call
#getAFewParameters() 
#plotSavedGains()   
performGainMeasurement()