"""
Created on Oct 16, 2014

@author: Mihai Suciu
"""

from matplotlib import pyplot as plot

import time


class GameLivePlot():
    """
    Used to plot player strategies during the game.
    """
    title = 'plot'
    nr_players = 0
    # dictionary holding players best response
    gains = dict()

    markers = ['o', 'v', 's', 'D']
    colors = ['red', 'green', 'blue', 'magenta']

    def __init__(self, plot_title):
        """
        :param plot_title:
        :return:
        """
        self.title = plot_title

        # start an interactive plot
        plot.ion()
        # create a figure
        self.fig1 = plot.figure(self.title)

    def init_plot(self, nr_players):
        """
        init plot params
        :param nr_players:
        :return:
        """
        self.nr_players = nr_players
        for x in range(0, self.nr_players):
            self.gains[x] = list()

    def plot_tx_powers(self, pl_tx_powers):
        """
        initialize empty plot
        :param pl_tx_powers: list containing players initial tx power
        :return:
        """
        for x in range(0, self.nr_players):
            self.gains[x].append(pl_tx_powers[x])
        plot.clf()
        plot.grid()
        plot.xlabel('game iterations')
        plot.ylabel('player strategies [dBm]')
        for i in range(0, self.nr_players):
            plot.plot(range(0,len(self.gains[i])), self.gains[i], color=self.colors[i], marker=self.markers[i], label="Player %d" % (i+1))
        plot.legend(loc=0, bbox_to_anchor=(1.1, 1.1))
        plot.axis([0, 70, -90, 0])
        plot.draw()
        time.sleep(2)


    def test_plot(self):
        """
        test plot
        :return:
        """
        plot.clf()
        plot.grid()
        plot.xlabel('game iterations')
        plot.ylabel('player strategies')
        plot.axis([0, 5, 0, 3])
        plot.plot([1, 2, 3], [3, 2, 3], color='red', marker=self.markers[0], label='Player1')
        plot.legend(loc=0, bbox_to_anchor=(1.1, 1.1))
        plot.draw()
        time.sleep(2)