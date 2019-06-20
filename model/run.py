# Data manipulation
import matplotlib.pyplot as plt
import pandas as pd

# Python imports
import time
import sys
import os

# Custom imports
from model import code_dev_simulation
from java_printer import JavaPrinter
import csv
import datetime

DEFAULT_SIMULATIONS = 100
DEFAULT_ITERATIONS = 10**5 # 100,000 steps is around 15 mins
# fitness method = 0 -> uniform distribution
FITNESS_METHOD = 0
EXP_CONDITION = 'no_rec' # reproduce (recursion/multiple calls possible), 'no_rec' ...
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

    Argument 1 (int): Amount of iterations to run model
    Argument 2 (bool): Whether to generate the java files created during the simulation
    Argument 3 (int): Amount of simulations of the model to run
    """

    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ITERATIONS
    simulations = int(sys.argv[3]) if len(sys.argv) > 1 else DEFAULT_SIMULATIONS
    assert (EXP_CONDITION in ['reproduce', 'no_rec'])

    # Create the output file
    filename = create_outputfile()

    for sim in range(simulations):
        print('Simulation {} of {}'.format(sim+1, simulations))

        model = code_dev_simulation(iterations, FITNESS_METHOD, PROBABILITIES, EXP_CONDITION)

        print('Model instantiated...\n')

        print('Running model...')

        start_time = time.time()
        model.run_model()

        print('Model run completed..!\nTook {} seconds.\n'.format(time.time() - start_time))

        gen = bool(sys.argv[2]) if len(sys.argv) > 2 else False
        gather_results(model, gen)
        filename = append_outputfile(model, sim, filename)

def gather_results(model, generate_files):
    """
    Gathers and analyses model results

    Args:
        - model (Code_dev_simulation): Model to analyse the results of
        - generate_files (bool): Indicates whether to generate the created java files

    TODO:
        - Test implementation of java file generation
    """
    if (generate_files):
        if os.path.exists('output'):
            for root, _, files in os.walk('output'):
                for name in files:
                    os.remove(os.path.join(root, name))
        os.makedirs('output/src', exist_ok=True)
        for class_info in model.classes:
            java_printer = JavaPrinter()
            class_info.accept(java_printer)
            with open(os.path.join('output/src', class_info.name + '.java'), 'w') as java_file:
                java_file.write(java_printer.result)

def create_outputfile():
    """
    Creates an output file with the header, returns filename
    Columns are 'sim', 'step', 'fmin', 'action', 'fnum', 'fmean', 'fstd', 'fmin', 'fmax'

    return filename
    """

    # Create folder
    os.makedirs('results', exist_ok=True)
    # Create file
    filename = 'results/result_' + str(EXP_CONDITION) + '_' + str(FITNESS_METHOD) + '_' + str(datetime.datetime.now().strftime("%d_%H_%M_%S")) + '.csv'
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        # Header
        writer.writerow(['sim', 'step', 'fmin', 'action', 'fnum', 'fmean', 'fstd', 'fmin', 'fmax'])

    return filename

def append_outputfile(model, sim, filename):
    """
    Appends results from a simulation to the output file with one row per simulation step
    Creates new file if there is a memory error

    Columns are 'sim', 'step', 'fmin', 'action', 'fnum', 'fmean', 'fstd', 'fmin', 'fmax'

    Returns filename
    """
    try:
        # Open file
        with open(filename, mode='a', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            # Write rows
            for row in range(len(model.list_fmin)):
                writer.writerow([sim, row, model.list_fmin[row], model.list_action[row]] + model.list_fit_stats[row])

    # Create new file if there is a memoryerror and add entire simulation results
    except MemoryError:
        filename = create_outputfile()
        # Open file
        with open(filename, mode='a', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            # Write rows
            for row in range(len(model.list_fmin)):
                writer.writerow([sim, row, model.list_fmin[row], model.list_action[row]] + model.list_fit_stats[row])

    return filename

if __name__ == "__main__":
    run_repo_model()
