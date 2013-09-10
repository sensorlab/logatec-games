from plot import Plot

import os
import time
  
def plotIterations(player_number1, tx_node_id1, rx_node_id1, player_number2, tx_node_id2, rx_node_id2, c1=0, c2=0, TruncatedValues=True, saveImage = True):
    #This method will read the files which contains information about an experiment identified from c1 and c2, and then plot the results using Plot class
    path1 ="./iterations/c1_%d-c2_%d/player_%d_with_tx_%d_and_rx_%d.dat" %(c1, c2, player_number1, tx_node_id1, rx_node_id1)
    path2 ="./iterations/c1_%d-c2_%d/player_%d_with_tx_%d_and_rx_%d.dat" %(c1, c2,player_number2, tx_node_id2, rx_node_id2)
    
    if (not os.path.exists(path1) or not os.path.isfile(path1)):
        print "No data available for plotting iterations"
        return
    
    if (not os.path.exists(path2) or not os.path.isfile(path2)):
        print "No data available for plotting iterations"
        return
    
    f1 = open(path1, "r")
    f2 = open(path2, "r")
    
    #read first file
    iterations_list1 =[]
    labels1 = []
    #read first line, it's a  header
    f1.readline()
    while True:
        line = f1.readline()
        
        if not line:
            break
        
        #detect line which represent the starting of a new experiment
        if line[0:10] == "Experiment":
            iterations_list1.append([])
            line_list = line.split()
            if line_list[9]=="adaptive":
                labels1.append("cost=%s  gain=%s dB" %(line_list[9], line_list[22] ) )
            else:
                labels1.append("cost=%s  gain=%s dB" %(line_list[8], line_list[22] ) )
            continue
        
        line_list = line.split()
        try:
            if TruncatedValues:
                iterations_list1[-1].append(float(line_list[3]))
            else:
                iterations_list1[-1].append(float(line_list[5]))
        except:
            continue
    f1.close()
    
    #read second file
    iterations_list2 =[]
    labels2 = []
    #read first line, it's a  header
    f2.readline()
    while True:
        line = f2.readline()
        
        if not line:
            break
        
        if line[0:10] == "Experiment":
            iterations_list2.append([])
            line_list = line.split()
            if line_list[9] == "adaptive":
                labels2.append("cost=%s  gain=%s dB" %( line_list[9], line_list[22]) )
            else:
                labels2.append("cost=%s  gain=%s dB" %( line_list[8], line_list[22]) )
            continue
        
        line_list = line.split()
        try:
            if TruncatedValues:
                iterations_list2[-1].append(float(line_list[3]))
            else:
                iterations_list2[-1].append(float(line_list[5]))
        except:
            continue
    f2.close()
    
    if TruncatedValues:
        Plot.plot2Subplots(iterations_list1, iterations_list2, labels1, labels2, "Iterations", "Power [dBm]", "Best response evolution for player %d. Truncated values" %player_number1, "Best response evolution for player %d. Truncated values" %player_number2,c1, c2,ion=False,Truncated=TruncatedValues,SaveImg = saveImage )
    else:
        Plot.plot2Subplots(iterations_list1, iterations_list2, labels1, labels2, "Iterations", "Power [dBm]", "Best response evolution for player %d. Real values" %player_number1, "Best response evolution for player %d. Real values" %player_number2,c1, c2,ion=False,Truncated=TruncatedValues,SaveImg = saveImage )

