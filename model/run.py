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

DEFAULT_ITERATIONS = 10000
# fitness method = 0 -> uniform distribution
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

    Argument 1 (int): Amount of iterations to run model
    Argument 2 (bool): Whether to generate the java files created during the simulation
    """

    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ITERATIONS
    model = code_dev_simulation(iterations, FITNESS_METHOD, PROBABILITIES)

    print('Model instantiated...\n')

    print('Running model...')

    start_time = time.time()
    model.run_model()

    print('Model run completed..!\nTook {} seconds.\n'.format(time.time() - start_time))

    gen = bool(sys.argv[2]) if len(sys.argv) > 2 else False
    gather_results(model, gen)
    create_outputfile(model)

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

def create_outputfile(model):
    """
    Writes an output file with one row per simulation step
    Columns are 'step', 'fmin', 'action'

    """

    # Create folder
    os.makedirs('results', exist_ok=True)
    # Create file
    with open('results/result_' + str(FITNESS_METHOD) + '_' + str(datetime.datetime.now().strftime("%d_%H_%M_%S")) + '.csv',
              mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        # Header
        writer.writerow(['step', 'fmin', 'action'])

        # Write rows
        for row in range(len(model.list_fmin)):
            writer.writerow([row, model.list_fmin[row], model.list_action[row]])


if __name__ == "__main__":
    run_repo_model()
