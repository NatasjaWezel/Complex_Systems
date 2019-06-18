# Data manipulation
import matplotlib.pyplot as plt
import pandas as pd

# Python imports
import time


# Custom imports
from model import commit_simulation

def run_repo_model():
    """
    This function instantiates a model and can be used to gather results
    """
    n_authors = 5
    iterations = 100

    model = commit_simulation(n_authors, iterations, 0)
    print('Running model...')
    start_time = time.time()
    model.run_model()
    print('Model run completed..!\nTook {} seconds.'.format(time.time() - start_time))
    gather_results(model)


def gather_results(model):
    """
    Gathers and analyses model results
    """
    print('Analysing model...\n\n')
    data = model.datacollector.get_agent_vars_dataframe()
    print(data)
    print(model.commit_delta_log)
    print(model.repository)

if __name__ == "__main__":
    run_repo_model()