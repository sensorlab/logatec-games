from vesna import alh
from vesna.alh.spectrumsensor import SpectrumSensor, SpectrumSensorProgram, SweepConfig
from vesna.alh.signalgenerator import SignalGenerator, SignalGeneratorProgram, TxConfig

import time
import os
import logging

class Node:
    #This class has methods for configuring the VESNA nodes, for generating a signal, for spectrum sensing
    #This class uses VESNA modules.
    
    tx_config = None
    sweep_config = None
    
    def __init__(self, coordinator_id, node_id):
        #get a coordinator object
        self.coordinator = alh.ALHWeb("https://crn.log-a-tec.eu/communicator", coordinator_id)
        
        #get a node object
        self.node = alh.ALHProxy(self.coordinator, node_id)
        
        #save the coordinator_id and node_id
        self.coordinator_id = coordinator_id
        self.node_id = node_id
        
        logging.basicConfig(level=logging.INFO)
        
    def NodeTest(self):
        #just try to communicate with the coordinator and with the node to see if they are working
        print self.coordinator.get("hello")
        print self.node.get("sensor/mcuTemp") 
        
    def getSenseConfig(self):
        #just get a configuration list so you can see it
        SpectrumSensor(self.node).get_config_list()
        
    def getGeneratorConfig(self):
        #just get a configuration list so you can see it
        SignalGenerator(self.node).get_config_list()
        
        
    def setSenseConfiguration(self, start_freq_hz, end_freq_hz, step_freq_hz):
        #sets the sensing configuration for sensing node. It measure the power in the band of [ start_freq_hz   end_freq_hz].
        #The sweep step is step_freq_hz 
        self.sweep_config = SpectrumSensor(self.node).get_config_list().get_sweep_config(start_freq_hz, end_freq_hz, step_freq_hz)  
        
        if self.sweep_config is None:
            raise Exception("Something went wrong with the sweep_config. Sweep_config is None")
        
    def setSenseConfigurationChannel(self, start_ch, stop_ch, step_ch):
        #sets the sensing configuration for sensing node. It measures the power from start_ch to stop_ch
        #The sweep step is step_ch
        self.sweep_config = SweepConfig(SpectrumSensor(self.node).get_config_list().get_config(0,0) , start_ch, stop_ch, step_ch )
        
        if self.sweep_config is None:
            raise Exception("Something went wrong with the sweep_config. Sweep_config is None")
              
    def setSenseConfigurationFullSweep(self):
        #sets the sensing configuration for node . The difference is that this method will sense the entire band that device supports
        self.sweep_config = SpectrumSensor(self.node).get_config_list().get_config(0,0).get_full_sweep_config()
        
        if self.sweep_config is None:
            raise Exception("Something went wrong with the sweep_config. Sweep_config is None")
        
    def senseStart(self, time_start, time_duration , slot_id):
        #start spectrum sensing on node with the given configuration (self.sweep_config it is what matter)
        #may perform a few frequency sweeps, depends on the time duration 
        
        #this can generate exception if sweep_config is None
        if self.sweep_config is None:
            print "Cannot start sensing, configuration is missing"
            return None
       
        #get a program object.
        program = SpectrumSensorProgram(self.sweep_config, time_start, time_duration , slot_id )
        
        #get sensor object, with this we'll program the node
        sensor =  SpectrumSensor(self.node)
    
        #program the sensor
        sensor.program(program)
        
        #waiting for the sensor to finish the job
        while not sensor.is_complete(program):
            print "waiting..."
            time.sleep(1)
            
            if time.time() > (program.time_start + program.time_duration + 60):
                raise Exception("Something went wrong with the sensing")
        
        print "Experiment is finished. retrieving data."
        result = sensor.retrieve(program)
        
        #try to make a folder
        try:
            os.mkdir("./data")
        except OSError:
            pass
        
        try:
            os.mkdir("./data/coor_%d" %self.coordinator_id)
        except OSError:
            pass
        
        #write results in a file
        result.write("./data/coor_%d/node_%s.dat" %(self.coordinator_id ,self.node_id))
  
    def senseStartQuick(self):
        #returns a list : [[frequencies] , [power_dbm]]
        #starts spectrum sensing on node with the given configuration (self.sweep_config it is what matter)
        #The difference is that this method will do a quick step. Use this if time is critical
        #Bandwidth you can measure in this case is limited 
        #This will perform a single frequency step with the sweep method defined in the SpectrumSensor class
        
        #this can generate exception if sweep_config is None
        if self.sweep_config is None:
            print "Cannot start sensing, configuration is missing"
            return None
        
        sweep =  SpectrumSensor(self.node).sweep(self.sweep_config)
        
        #get the frequency list
        f_hz = self.sweep_config.get_hz_list()
        
        data_received = []
        data_received.append(f_hz)
        data_received.append(sweep.data)
        return data_received
       
        
    def setGeneratorConfiguration(self, f_hz, power_dbm):
        #sets configuration for the signal generation. 
        #In this case, the parameters are f_hz and power_dbm, the choosen configuration rely on this parameters. 
          
        #get a tx_config object
        self.tx_config = SignalGenerator(self.node).get_config_list().get_tx_config(f_hz, power_dbm)
        
        if self.tx_config is None:
            raise Exception("something went wrong with configuration, tx_config is None")
        
    def setGeneratorConfigurationChannel(self, f_ch, power_dbm):
        #sets configuration for the signal generation. 
        #In this case, the parameters are f_ch and power_dbm
         
        #get a tx_config object
        self.tx_config = TxConfig(SignalGenerator(self.node).get_config_list().get_config(0, 0), f_ch, power_dbm)
        
        if self.tx_config is None:
            raise Exception("Something went wrong with configuration")
        
    def generatorStart(self, time_start, time_duration):
        #starts signal generation with the given configuration (tx_config is what matter)
        
        #this can generate exceptions if self.tx_config is None
        if self.tx_config is None:
            print "Cannot start signal generating, configuration is missing"
            return None
      
        #get a program object
        program = SignalGeneratorProgram(self.tx_config, time_start, time_duration)
        SignalGenerator(self.node).program(program)