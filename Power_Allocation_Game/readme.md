## Introduction
This package provides Python *.py files for conductiong a simple power allocation game between two players (four nodes) located in a VESNA-based wireless sensor network that uses ALH protocol in order to communicate. (link to LOG-a-TEC portal can be found [here](http://www.log-a-tec.eu/) - you need a username and password in order to have access to the testbed).

Before using this package, please install VESNA ALH Tools and Python bindings for VESNA spectrum sensor application. In order to do this, please follow the steps described here:

* 1) **Installation of VESNA ALH Tools**
(see its own README file for installation instructions - _Tomaz Solc_ )
* https://github.com/avian2/vesna-alh-tools
* 2) **Installation of Python bindings for VESNA spectrum application** 
(see its own README file for installation instructions - _Tomaz Solc_ )
* https://github.com/sensorlab/vesna-spectrum-sensor

**This package contains the following Python classes:**
* **Node** - used for setting the nodes as transmitters or receivers
* **Player** - contains information about the player, such as: channel gains, costs, player number (ID), noise power.
* **PlayerApp** - used as an application for sending packets (generating signal).
* **PowerAllocation** - used for determining the power that need to be allocated for each player. It contains three types of implementation (gameType) mentioned in Wiki "Power Allocation Game in a Real Scenario. The case of PAPU in LOG a TEC".
* **gainCalculations** - used for performing channel gain measurements.
* **Noise** - used for measuring the noise power.
* **Plot** - used for plotting the results.
* **bestResponseAnalysis** - used for analysing the behaviour of the best response as a function of different parameters.
* **Kalmanimplementation** - used for implementing the Kalman Filter
* **MyQueue** - use as a queue of channel gains and best responses.
* **Iterations** - used for plotting algorithm's interations.
* **PlotNashEquilibriums** - used for plotting player strategies.

------------------------------------------------------------------

* **gainMeasurementExample** - used as an example on how to perform channel gain measurements.
* **gameExample** - used as an example on how to run the game.




In the power allocation game, each player has two layers:

            +-----------------------------------------------------------------------------+ 
            |   +---------------------------+                  +----------------------+   |    
            |   |        Application        |<-------Pi------->|   Power Allocation   |   | Player i
            |   +---------------------------+                  +----------------------+   |
            +-----------------------------------------------------------------------------+          
                            |                                           |       |
                            Pi                                          |       |
                            |                                           |       |
                +---------------------------+                           |       |
                |     Radio Environment     |                           Pi      Pj
                +---------------------------+                           |       |
                            |                                           |       |
                            Pj                                          |       |
                            |                                           |       |
            +-----------------------------------------------------------------------------+ 
            |   +---------------------------+                  +----------------------+   |    
            |   |        Application        |<-------Pi------->|   Power Allocation   |   | Player j
            |   +---------------------------+                  +----------------------+   |
            +-----------------------------------------------------------------------------+  
                                    Fig.1 System layers in a cooperative game
                                    
             +-----------------------------------------------------------------------------+ 
             |   +---------------------------+                  +----------------------+   |    
             |   |        Application        |<-------Pi------->|   Power Allocation   |   | Player i
             |   +---------------------------+                  +----------------------+   |
             +-----------------------------------------------------------------------------+         
                        |                                                  
                        Pi                                      
                        |                                           
            +---------------------------+                       
            |     Radio Environment     |               
            +---------------------------+           
                        |                           
                        Pj                              
                        |                                   
             +-----------------------------------------------------------------------------+ 
             |   +---------------------------+                  +----------------------+   |    
             |   |        Application        |<-------Pi------->|   Power Allocation   |   | Player j
             |   +---------------------------+                  +----------------------+   |
             +-----------------------------------------------------------------------------+  
                                Fig.2 System layers in the PAPU implementation
                                
            where:
                Application layer – representing the player who wants to use the radio environment.
                Power Allocation layer – used to determine the best power allocation that the Application layer can use.

Objects:

                            +---------------------------+
                   +------->|         PLAYER i          |<-------+
                   |        +---------------------------+        | -each Player has an object
                   |                                             | of PlayerApp and PowerAllocation
                   |                                             | -each PlayerApp has an object
                   |                                             | of Player and PowerAllocation
                   |                                             | -each PowerAllocation has an
                   |                                             |  object of Player and PlayerApp
                   |   +-----------+       +-----------------+   |    
                   +-->| PlayerApp |<----->| PowerAllocation |<--+
                       +-----------+       +-----------------+
                                                    |
                                                    |
                                        +--------------------------+
                                        | Communication with other | -each PowerAllocation layer
                                        | player's PowerAllocation |  communicates with others
                                        |         layer            |  PowerAllocation layer
                                        +--------------------------+
                                        
The game problem definition, game theory based solution, PAPU algorithm, experimental set-up and the types of implementing this game can be found in the Wiki, page "Power Allocation Game in a Real Scenario. The case of PAPU in LOG a TEC".
