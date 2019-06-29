import pandas as pd
import numpy as np
import pickle
import os

def get_statistics(data, f0):
    """
    Returns a dict with lists of statistical values per simulation

    """
    statistics = {
        'f0': f0,
        'fmax_means': [],
        'fmin_means': [],
        'f_commit_means': [],
        'f_commit_mins': [],
        'f_commit_maxs': [],
        'num_commits': [],

        'steps': [],
        'lines_sum': [],
        'lines_pos': [],
        'lines_neg': [],
        'lines_big': [],
        'changes_sum': [],
        'changes_pos': [],
        'changes_neg': [],
        'changes_big': [],

        'action_props': []
    }

    for sim in data['sim'].unique():
        data_sim = data[data['sim'] == sim]
        data_commits = data_sim[data_sim['fmin'] >= f0]
        commits = list(data_commits['step'])

        # mean fmin and fmax
        statistics['fmin_means'].append(data_sim['fmin'].mean())
        statistics['fmax_means'].append(data_sim['fmax'].mean())

        # mean, min, max f for a commit
        statistics['f_commit_means'].append(data_commits['fmean'].mean())
        statistics['f_commit_mins'].append(data_commits['fmin'].mean())
        statistics['f_commit_maxs'].append(data_commits['fmax'].mean())
        statistics['num_commits'].append(len(commits))

        # Mean size of steps/lines/changes per commit
        changes_dict, changes_names = get_changes(data_sim, commits)
        for name in changes_names:
            statistics[name].append(changes_dict[name])

        # Proportions last action
        statistics['action_props'].append(get_action_proportions(data_sim, commits))
        if sim % 1 == 0:
            print('running sim {} of {}'.format(sim, len(data['sim'].unique())))

    return statistics


def dicts_per_exp(datas):
    dicts = []
    for data in datas:
        dicts.append(get_statistics(data, .5))
        print('a dict is done')
    return dicts


def find_commits(data, f0, at_final=False):
    """
    Returns a list with the timesteps where the fmin >= f0 and at the final timestep
    """
    #     commits = [data['step'].iloc[i] for i in range(len(data)) if data['fmin'].iloc[i] >= f0]
    commits = list(data[data['fmin'] >= f0]['step'])

    if at_final and commits[-1] != data['step'].iloc[-1]:
        commits += [data['step'].iloc[-1]]

    return commits


def get_pos_neg_lines(data):
    """
    Get absolute positive, negative and total changes in lines in this data
    """

    neg_changes = data[data['size_change'] < 0]['size_change'].abs().sum()
    pos_changes = data[data['size_change'] > 0]['size_change'].abs().sum()
    file_change = pos_changes - neg_changes

    return file_change, pos_changes, neg_changes


def get_pos_neg_changes(data):
    """
    Get absolute positive, negative and total changes in this data
    """
    pos_changes = data[(data['action'] != 'remove_method') & (data['changes'] >= 0)]['changes'].abs().sum()
    neg_changes = data[(data['action'] == 'remove_method') | (data['changes'] < 0)]['changes'].abs().sum()
    file_change = pos_changes - neg_changes

    return file_change, pos_changes, neg_changes


def get_changes(data, commits):
    """
    Returns list with mean size of steps/lines/changes per commit
    """
    stats_names = ['steps', 'lines_sum', 'lines_pos', 'lines_neg', 'lines_big', 'changes_sum', 'changes_pos',
                   'changes_neg', 'changes_big']
    stats = {name: [] for name in stats_names}

    # Add column with size changes
    data['shift'] = data['code_size'].shift(periods=1, fill_value=0)
    data['size_change'] = data['code_size'] - data['shift']

    # Iterate over commits
    prev_ind = 0
    for commit in commits:
        data_commit = data.iloc[prev_ind:commit]

        stats['steps'].append(commit - prev_ind)

        # Get number of changes lines, added and deleted lines
        file_change, change_pos, change_neg = get_pos_neg_lines(data_commit)
        stats['lines_sum'].append(file_change)
        stats['lines_pos'].append(change_pos)
        stats['lines_neg'].append(change_neg)
        stats['lines_big'].append(max(change_pos, change_neg))

        # Get the total, positive and negative changes
        file_change, change_pos, change_neg = get_pos_neg_changes(data_commit)
        stats['changes_sum'].append(file_change)
        stats['changes_pos'].append(change_pos)
        stats['changes_neg'].append(change_neg)
        stats['changes_big'].append(max(change_pos, change_neg))

        prev_ind = commit

    return {name: np.array(stats[name]).mean() for name in stats_names}, stats_names


#     return [np.array(stats[name]).mean() for name in stats_names], stats_names


def get_action_proportions(data, commits):
    """
    Returns a list with the proportion of actions in the commits
    update, call, remove, create"""
    # Initialize dict
    action_names = ['update_method', 'call_method',
                    'remove_method', 'create_method']
    actions = {name: 0 for name in action_names}

    # Count the actions
    for commit in commits:
        actions[data['action'].iloc[commit]] += 1

    # Return the list of action proportions
    return [actions[name] / len(commits) for name in action_names]


if __name__ == "__main__":
    """
    Writes a pickle file with the statistics of the exp. condition
    """
    # Change filename to the file you want to analyse
    filename = "result_msr_MSR_fit0_its100000_addprob1_time26_20_13_22.csv"

    f0 = .5

    os.makedirs('commit_sizes', exist_ok=True)

    data = pd.read_csv(filename)
    data = data[data['sim']<60]
    data['action'][data['action']=='delete_method'] = 'remove_method'
    dictionary = get_statistics(data, f0)

    # Pickle dict
    pickle.dump(dictionary, open('pickles/' +filename[:-4] + ".p", "wb" ))



