""" This module contains a set of auxiliary functions for the testing
    of the grmpy package
"""

# standard library
import random
import string
import numpy as np

# project library
from tools.user.processing import _add_auxiliary

# Module-wide variables
MAX_AGENTS = 1000
MAX_MAXITER = 0
MAX_NUM_COVARS_OUT = 5
MAX_NUM_COVARS_COST = 5

''' Main function '''


def random_init(seed=None):
    """ This function simulated a random initialization file.

        This function already imposes that I have at least one covariate in X
        and Z, and also an intercept is defined.
        
    """

    # Set random seed
    if seed is not None:
        np.random.seed(seed )

    init_dict = dict()

    # Basics
    init_dict['BASICS'] = dict()

    init_dict['BASICS']['agents'] = np.random.random_integers(1, MAX_AGENTS)

    init_dict['BASICS']['file'] = id_generator()

    # Correlation of unobservables
    init_dict['RHO'] = dict()

    for group in ['treated', 'untreated']:
        init_dict['RHO'][group] = np.random.uniform(-0.5, 0.5)

    # Estimation details
    init_dict['ESTIMATION'] = dict()
    init_dict['ESTIMATION']['optimizer'] = np.random.choice(['bfgs', 'nm'])
    init_dict['ESTIMATION']['start'] = np.random.choice(['random', 'init'])
    init_dict['ESTIMATION']['maxiter'] = np.random.random_integers(0,
                                                                  MAX_MAXITER)
    init_dict['ESTIMATION']['version'] = np.random.choice(['slow', 'fast'])

    # Model
    num_coeffs_out = np.random.random_integers(1, MAX_NUM_COVARS_OUT)
    num_coeffs_cost = np.random.random_integers(1, MAX_NUM_COVARS_COST)

    for key_ in ['TREATED', 'UNTREATED', 'COST']:
        init_dict[key_] = dict()
        init_dict[key_]['var'] = np.random.uniform(0.1, 0.5)

        if key_ not in ['COST']:
            init_dict[key_]['int'] = np.random.uniform(-0.5, 0.5)

        num_coeffs = num_coeffs_out

        if key_ == 'COST':
            num_coeffs = num_coeffs_cost

        init_dict[key_]['coeff'] = []
        for i in range(num_coeffs):
            init_dict[key_]['coeff'] += [np.random.uniform(-0.5, 0.5)]

    # Add auxiliary information
    init_dict = _add_auxiliary(init_dict)

    # Finishing
    return init_dict

''' Auxiliary functions '''

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):

    return ''.join(random.choice(chars) for _ in range(size)) + '.txt'



