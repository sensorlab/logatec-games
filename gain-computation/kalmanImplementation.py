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
# 		   Ciprian Anton
#

import math
from pykalman import KalmanFilter

def getStandardDeviation(list):
    #based on the list, returns the standard deviation
    #list must have linear values
    
    #determine the average value
    average = math.fsum(list)/len(list)
    
    #compute the difference of each data point from the mean(average), and square the result of each
    diference_list = []
    for i in range(0, len(list)):
        diference_list.append(math.pow(float(list[i])-average, 2))
    
    return math.sqrt(math.fsum(diference_list)/ len(diference_list) )

'''
#temporary
def getPredictedValue(measurements):
    #returns predicted value based on KalmanFilter
    #Apply  this method only for Gains
    
    standard_deviation = math.pow(getStandardDeviation(measurements), 1)
    standard_deviation = math.pow(0.1, 1)
    
    estimated_values = [0.00]
    error_cov =1.00
    
    for i in range(0, len(measurements)):
        #time update (prediction)
        prior_estimate = estimated_values[-1]
        prior_error_cov = error_cov
        
        #measurement update
        Kalman_gain = (prior_error_cov)/(prior_error_cov + standard_deviation)
        estimated_values.append( (prior_estimate + Kalman_gain * (measurements[i] - prior_estimate) ) )
        error_cov = (1- Kalman_gain)*prior_error_cov

    return estimated_values[1:len(estimated_values)]
'''

def getPredictedValuesVer2(measurements, standard_deviation = None):
    #this method use PyKalman module
    #Apply this method only for Gains.
    
    if standard_deviation == None:
        #if standard deviation is not specified, then get it only from measurements list
        standard_deviation = getStandardDeviation(measurements)
        
    #adapt the transition_covariance. Temporary 
    if standard_deviation < 1e-9:
        transition_covariance = 1e-21
    else:
        transition_covariance = 5e-17
    
    kf = KalmanFilter(transition_matrices = [1], observation_matrices = [1], transition_covariance = transition_covariance, observation_covariance = math.pow(standard_deviation, 2))
    tmp= kf.filter(measurements)[0].tolist()
    for i in range(0, len(tmp)):
        tmp[i] = tmp[i][0]
    
    return tmp


