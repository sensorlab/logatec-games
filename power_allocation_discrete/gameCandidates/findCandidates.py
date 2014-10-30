# Copyright (C) 2014 SensorLab, Jozef Stefan Institute
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

# Authors: Mihai Suciu
#

'''
Created on Mar 13, 2014

@version: 1.4
@author: mihai
'''
from games.myVersionOfPowerGame import gameNode
from games.myVersionOfPowerGame.gameCandidates.candidates import CandidateNodes

def main():
    """Find candidate nodes for the PAPU games, check the convergence condition"""
    
    coordinatorId = gameNode.JSI
    nodesJSI = [51, 52, 53, 54, 56, 57, 58, 59]
    
    findSol = CandidateNodes(coordinatorId, nodesJSI)
    # findSol.findNodes(3, 5, 6)
    
    #permutation = [51, 52, 56, 59, 57, 53, 54, 58]
    #permutation = [51, 52, 54, 58]
    permutation = [51, 52, 56, 59]
    findSol.testSpecificPermutation(2, permutation)
    

if __name__ == '__main__':
    main()
