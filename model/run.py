# Data manipulation
import matplotlib.pyplot as plt
import pandas as pd

# Python imports
import time
import sys
import os

# Custom imports
from model import code_dev_simulation

DEFAULT_ITERATIONS = 1000
FITNESS_METHOD = 0
PROBABILITIES = {
    'create_method': 0.1,
    'call_method': 0.4,
    'update_method': 0.45,
    'delete_method': 0.05,
    'create_class': 0.1
}

def run_repo_model():
    """
    This function instantiates a model and can be used to gather results

    Argument 1: Amount of iterations to run model
    """
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ITERATIONS
    model = code_dev_simulation(iterations, FITNESS_METHOD, PROBABILITIES)
    print('Model instantiated...\n')

    print('Running model...')
    start_time = time.time()
    model.run_model()
    print('Model run completed..!\nTook {} seconds.\n'.format(time.time() - start_time))

    gather_results(model)

def gather_results(model):
    """
    Gathers and analyses model results
    """
    pass

if __name__ == "__main__":
    run_repo_model()