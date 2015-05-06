""" This module contains all functions related to the estimation of the
    generalized Roy model.
"""

# standard library
import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize

# project library
from tools.user.processing import process

''' Main function '''


def estimate(init_dict):
    """ Estimate the generalized Roy model.
    """

    # Antibugging
    assert (isinstance(init_dict, dict))

    # Load dataset
    Y, D, X, Z = _load_data()

    # Create auxiliary objects
    start = init_dict['ESTIMATION']['start']
    maxiter = init_dict['ESTIMATION']['maxiter']

    optimizer = init_dict['ESTIMATION']['optimizer']

    # Initialize different starting values
    x0 = _get_start(start, init_dict)

    # Call alternative optimizers
    opts = dict()

    opts['maxiter'] = maxiter

    # Select optimizer
    if optimizer == 'nm':

        optimizer = 'Nelder-Mead'

    elif optimizer == 'bfgs':

        optimizer = 'BFGS'

    rslt = minimize(_max_interface, x0, args=(Y, D, X, Z),
                    method=optimizer, options=opts)

    # Tranformation to internal parameters
    num_covars_out = init_dict['AUX']['num_covars_out']

    parameters = _distribute_parameters(rslt['x'], num_covars_out)

    # Finishing
    return parameters


''' Auxiliary functions '''


def _distribute_parameters(x, num_covars_out):
    """ Distribute the parameters.
    """
    # Antibugging
    assert (isinstance(x, np.ndarray))
    assert (isinstance(num_covars_out, int))
    assert (num_covars_out > 0)

    # Initialize containers
    rslt = dict()

    rslt['TREATED'] = dict()
    rslt['UNTREATED'] = dict()
    rslt['COST'] = dict()
    rslt['RHO'] = dict()

    # Distribute parameters
    rslt['TREATED']['all'] = x[:num_covars_out]
    rslt['UNTREATED']['all'] = x[num_covars_out:(2 * num_covars_out)]

    rslt['COST']['all'] = x[(2 * num_covars_out):(-4)]

    rslt['TREATED']['var'] = np.exp(x[(-4)])
    rslt['UNTREATED']['var'] = np.exp(x[(-3)])

    rslt['RHO']['treated'] = -1.0 + 2.0 / (1.0 + float(np.exp(-x[-2])))
    rslt['RHO']['untreated'] = -1.0 + 2.0 / (1.0 + float(np.exp(-x[-1])))

    # Finishing.
    return rslt


def _negative_log_likelihood(args, Y, D, X, Z):
    """ Negative Log-likelihood function of the Generalized Roy Model.
    """
    # Distribute parametrization
    Y1_coeffs = np.array(args['TREATED']['all'])
    Y0_coeffs = np.array(args['UNTREATED']['all'])

    C_coeffs = np.array(args['COST']['all'])

    U1_var = args['TREATED']['var']
    U0_var = args['UNTREATED']['var']

    U1V_rho = args['RHO']['treated']
    U0V_rho = args['RHO']['untreated']

    # Auxiliary objects.
    num_agents = Y.shape[0]
    choice_coeffs = np.concatenate((Y1_coeffs - Y0_coeffs, - C_coeffs))

    # Likelihood construction.
    likl = 0.00

    for i in range(num_agents):

        G = np.concatenate((X[i, :], Z[i, :]))
        idx = np.dot(choice_coeffs, G)

        if D[i] == 1.00:

            coeffs = Y1_coeffs
            rho = U1V_rho
            sd = np.sqrt(U1_var)

        else:

            coeffs = Y0_coeffs
            rho = U0V_rho
            sd = np.sqrt(U0_var)

        arg_one = (Y[i] - np.dot(coeffs, X[i, :])) / sd
        arg_two = (idx - rho * arg_one) / np.sqrt(1.0 - rho ** 2)

        cdf_evals = norm.cdf(arg_two)
        pdf_evals = norm.pdf(arg_one)

        if D[i] == 1.0:

            contrib = (1.0 / float(sd)) * pdf_evals * cdf_evals

        else:

            contrib = (1.0 / float(sd)) * pdf_evals * (1.0 - cdf_evals)

        contrib = np.clip(contrib, 1e-20, None)

        likl += -np.log(contrib)

    likl *= (1.0 / float(num_agents))

    # Quality checks.
    assert (isinstance(likl, float))
    assert (np.isfinite(likl))

    # Finishing.
    return likl


def _load_data():
    """ Load dataset.
    """
    init_dict = process()

    # Auxiliary objects
    num_covars_out = init_dict['AUX']['num_covars_out']
    num_covars_cost = init_dict['AUX']['num_covars_cost']

    # Read dataset
    data = np.genfromtxt(init_dict['BASICS']['file'])

    # Distribute data
    Y, D = data[:, 0], data[:, 1]

    X, Z = data[:, 2:(num_covars_out + 2)], data[:, -num_covars_cost:]

    # Finishing
    return Y, D, X, Z


def _max_interface(x, Y, D, X, Z):
    """ Interface to the SciPy maximization routines.
    """
    # Auxiliary objects.
    num_covars_out = X.shape[1]

    # Collect maximization arguments.
    rslt = _distribute_parameters(x, num_covars_out)

    # Calculate likelihood.
    likl = _negative_log_likelihood(rslt, Y, D, X, Z)

    # Finishing.
    return likl


def _get_start(which, init_dict):
    """ Get different kind of starting values.
    """
    # Antibugging.
    assert (which in ['random', 'init'])

    # Distribute auxiliary objects
    num_paras = init_dict['AUX']['num_paras']

    # Select relevant values.
    if which == 'random':
        x0 = np.random.uniform(size=num_paras)

        # Variances
        x0[(-4)] = max(x0[(-4)], 0.01)
        x0[(-3)] = max(x0[(-3)], 0.01)

        # Correlations
        x0[(-2)] -= - 0.5
        x0[(-1)] -= - 0.5

    elif which == 'init':
        x0 = init_dict['AUX']['start_values'][:]
    else:
        raise AssertionError

    # Transform to real line
    x0 = _transform_start(x0)

    # Quality assurance.
    assert (np.all(np.isfinite(x0)))

    # Finishing.
    return x0


def _transform_start(x):
    """ Transform starting values to cover the whole real line.
    """

    # Coefficients
    x[:(-4)] = x[:(-4)]

    # Variances
    x[(-4)] = np.log(x[(-4)])
    x[(-3)] = np.log(x[(-3)])

    # Correlations
    x[(-2)] = -np.log(-1.0 + 2.0/(x[(-2) + 1]))
    x[(-1)] = -np.log(-1.0 + 2.0/(x[(-1) + 1]))

    # Finishing
    return x
