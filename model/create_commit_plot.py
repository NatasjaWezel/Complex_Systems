import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def convert(filename):
    data = pd.read_csv(filename)
    commits = get_lines_for_data(data, .5)
    df = pd.DataFrame(commits[0][3], columns=["colummn"])
    os.makedirs('./output/csv', exist_ok=True)
    df.to_csv('./output/csv/commits.csv', index=False)

def get_pos_neg_lines(data):
    """
    Get absolute positive, negative and total changes in lines in this data
    """

    neg_changes = data[data['size_change'] < 0]['size_change'].abs().sum()
    pos_changes = data[data['size_change'] > 0]['size_change'].abs().sum()
    file_change = pos_changes - neg_changes

    return file_change, pos_changes, neg_changes


def lines_per_commit(data_sim, commits):
    """
    data_sim is the data for one simulation, commits is a list of indices at the commits
    Returns the netto changes, the positive changes, negative changes and the max(insert, delete) changes as lists
    """
    file_changes, change_poss, change_negs, change_maxs = [], [], [], []
    prev_ind = 0

    # Iterate over the commits
    for commit in commits:
        # Create separate dataframe for this commit
        data_commit = data_sim.iloc[prev_ind:commit]
        # Get the changes in lines for this commit
        file_change, change_pos, change_neg = get_pos_neg_lines(data_commit)
        change_max = max(change_pos, change_neg)

        # Save these changes to separate lists
        file_changes.append(file_change)
        change_poss.append(change_pos)
        change_negs.append(change_neg)
        change_maxs.append(change_max)

        # Change previous index to new commit index
        prev_ind = commit

    # Return the list of changes per commit
    return file_changes, change_poss, change_negs, change_maxs



def get_lines_for_data(data, f0):
    """
    TODO: do stuff with the results from the lines_per_commit"""

    # Add column with size changes
    data['shift'] = data['code_size'].shift(periods=1, fill_value=0)
    data['size_change'] = data['code_size']-data['shift']

    commit_sizes_runs = []
    for sim in data['sim'].unique():
        # Data for one sim
        data_sim = data[data['sim']== sim]
        # Commits
        data_commits = data_sim[data_sim['fmin'] >= f0]
        commits = list(data_commits['step'])

        # Lists of changes per commit
        file_changes, change_poss, change_negs, change_maxs = lines_per_commit(data_sim, commits)
        commit_sizes_runs.append([file_changes, change_poss, change_negs, change_maxs])

    return commit_sizes_runs