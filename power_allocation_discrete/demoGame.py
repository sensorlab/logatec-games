"""
Demo for the Dynamic (cost adaptive) power allocation game.

A dynamic power allocation game is played between 4 players. Mapping between players and JSI VESNA nodes:
- player 1: transmitter node - JSI Vesna node 51, receiver node  - JSI Vesna node 52
- player 2: tx - node 56, rx - node 59
- player 3: tx - node 54, rx - node 58
- player 4: tx - node 57, rx - node 53
"""
import gameNode
from powerGame import PowerGame


def main():
    # define coordinator id
    coord_id = gameNode.JSI
    # consider plotting the results
    plot_results = True
    # measuring channel gains takes very long time, for speed-up you can run the game on some
    # old measurements, if consider_dummy_data=False then channel gains are measured
    consider_dummy_data = True
    # list of node ids used for this game, demo requires 4 players!!
    nodes_used = [51, 52, 56, 59, 54, 58, 57, 53]
    # player costs
    #costs = [0.2, 0.2, 0.2, 0.2]
    costs = [0.3, 0.3, 0.3, 0.3]
    # frequency used
    freq = 2422e6

    plr_thresh = 40
    # game_type = 5
    game_type = 6
    nr_game_iterations = 50
    measuring_period = 10
    nr_runs = 1

    # dummy data used when channel gains are not measured
    dummyDirectGains = {0: 0.0009268290613003395, 1: 3.77518487745779e-06, 2: 0.00010864181762973266,
                        3: 0.0008317625408339001}
    dummyCrossGains = {0: {1: 8.629189815526171e-06, 2: 1.9860138212515864e-05, 3: 0.00010814277139495838},
                       1: {0: 1.1528149943349e-06, 2: 1.588459852554849e-05, 3: 4.785576487266305e-06},
                       2: {0: 2.7921211726230703e-06, 1: 8.184583907864356e-05, 3: 2.6459159576826786e-06},
                       3: {0: 0.00017417959086096514, 1: 1.896643259824681e-05, 2: 0.0003206259020644263}}
    dummyTxPowers = {0: -8, 1: -8}

    powerGame = PowerGame(coord_id, nodes_used, costs, freq, game_type, plr_thresh, plot_results)
    powerGame.initPlayers()
    if game_type == 6:
        powerGame.set_total_game_iterations(nr_game_iterations)
        powerGame.set_measuring_period(measuring_period)
    if consider_dummy_data:
        powerGame.setGameDummyData(dummyDirectGains, dummyCrossGains, None)
    else:
        powerGame.measureGains()
    powerGame.playGame(nr_runs)


if __name__ == '__main__':
    main()