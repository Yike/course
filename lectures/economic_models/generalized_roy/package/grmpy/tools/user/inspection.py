""" This module contains all functions related to the inspection of the
    results from an estimation run.
"""

# standard library
import numpy as np

# project library
from tools.economics.simulation import simulate

''' Main function '''


def inspect(rslt, init_dict):
    """ This function simulates a sample from the estimates of the model
        and reports the average effects of treatment in a file.
    """
    # Antibugging
    assert (isinstance(rslt, dict))
    assert (isinstance(init_dict, dict))

    # Update parameters
    modified_init = init_dict

    for key_ in rslt.keys():

        for subkey in rslt[key_].keys():

            modified_init[key_][subkey] = rslt[key_][subkey]

    # Modified dataset
    modified_init['BASICS']['file'] = 'simulated.txt'

    # Simulate from estimation results
    Y1, Y0, D = simulate(modified_init, True)

    # Calculate the average treatment effects
    B = Y1 - Y0

    effects = []
    effects += [np.mean(B)]
    effects += [np.mean(B[D == 1])]
    effects += [np.mean(B[D == 0])]

    # Print selected results to file
    fmt = '     {0:<5}{1:10.2f}\n\n'

    with open('results.txt', 'w') as file_:

        file_.write('\n softEcon: Generalized Roy Model')
        file_.write('\n -------------------------------\n')

        file_.write('\n Average Treatment Effects\n\n')

        for i, label in enumerate(['ATE', 'TT', 'TUT']):

            str_ = fmt.format(label, effects[i])

            file_.write(str_)
