# Data manipulation
import matplotlib.pyplot as plt
import pandas as pd

# Python imports
import os


def plot_script(model, F0=.5):
    """
    Created 4 plots in figs folder
    Used model as input

    Plots:
    - fmin per timestep with commit places
    - number of changes per commit
    - max(insertions, deletions) in lines per commit
    - repository size per commit
    """
    # Create folder for the figures
    os.makedirs('figs', exist_ok=True)

    # Create dataframe
    data = create_dataframe(model)
    data['shift'] = data['code_size'].shift(periods=1, fill_value=0)
    data['size_change'] = data['code_size'] - data['shift']
    print(data.head(5))
    # Find commits
    commits = find_commits(data, F0)

    # Create plots
    plot_fitness(data, commits, colorcoded=False) # fmin.png
    plot_commitsize(data, commits) # commit_change.png
    plot_commitsize_biggest(data, commits) # commit_size.png
    plot_rep_size(data, commits) # rep_size.png


def plot_fitness(data, commits, colorcoded=False):
    """
    Plot the lowest fitness per time step with the places of the commits
    if colorcoded=True the dots in the scatterplot represent their action
    """

    # Plot green commit lines
    plt.axvline(commits[0], alpha=.1, linestyle='-', c='green', label='commit')
    for commit in commits[1:]:
        plt.axvline(commit, alpha=.1, linestyle='-', c='green')

    # Color the dots with their action
    if colorcoded:
        plt.scatter(data[data['action'] == 'update_method']['step'], data[data['action'] == 'update_method']['fmin'],
                    s=3, label='fmin, update', c='blue')
        plt.scatter(data[data['action'] == 'call_method']['step'], data[data['action'] == 'call_method']['fmin'],
                    s=3, label='fmin, call', c='orange')
        plt.scatter(data[data['action'] == 'remove_method']['step'], data[data['action'] == 'remove_method']['fmin'],
                    s=3, label='fmin, remove', c='yellow')
        plt.scatter(data[data['action'] == 'create_method']['step'], data[data['action'] == 'create_method']['fmin'],
                    s=3, label='fmin, create', c='red')
    # All dots the same color
    else:
        plt.scatter(data['step'],data['fmin'], s=3, label='fmin')

    plt.title('Lowest fitness of the methods in the repository per time step')
    plt.xlabel('Time')
    plt.ylabel('Lowest fitness (fmin)')
    plt.legend(numpoints=1)
    plt.savefig('figs/fmin.png')
    plt.clf()


def plot_commitsize(data, commits):
    """
    Number of changes per commit, barplot
    """

    prev_commit = 0
    for i in range(len(commits)):
        # Calculate the number of changes in this commit
        num_changes = data['changes'].iloc[prev_commit:commits[i]].abs().sum()
        plt.bar(i, num_changes, color='blue')

        prev_commit = commits[i]

    plt.title('Number of changes per commit')
    plt.xlabel('Time')
    plt.ylabel('Number of changes')
    plt.savefig('figs/commit_change.png')
    plt.clf()


def plot_commitsize_biggest(data, commits):
    """
    max(insertions, deletions) per commit
    """

    prev_commit = 0
    first_plot = [True, True]
    for i in range(len(commits)):
        pos_changes, neg_changes = get_pos_neg_changes(data.iloc[prev_commit:commits[i]])

        if pos_changes > abs(neg_changes):
            plt.bar(i, pos_changes, color='blue', label="insert" if first_plot[0] else "")
            first_plot[0] = False
        else:
            plt.bar(i, abs(neg_changes), color='red', label="delete" if first_plot[1] else "")
            first_plot[1] = False

        prev_commit = commits[i]

    plt.title('Maximum of insertions or deletions per commit')
    plt.xlabel('Time')
    plt.ylabel('Size of inserttions/deletions')
    plt.legend(numpoints=1)
    plt.savefig('figs/commit_size_biggest.png')
    plt.clf()


def plot_rep_size(data, commits):
    """
    Plot the repository size per commit
    """

    plt.plot(range(len(commits)), [data['code_size'].iloc[commit] for commit in commits])
    plt.title('Repository size per commit')
    plt.xlabel('Commit')
    plt.ylabel('Size')
    plt.savefig('figs/rep_size.png')
    plt.clf()


def get_pos_neg_changes(data):
    """
    Return the positive and negative changes in this commit data
    """
    pos_changes = data[data['size_change'] > 0]['size_change'].sum()
    neg_changes = data[data['size_change'] < 0]['size_change'].sum()

    return pos_changes, neg_changes


def find_commits(data, f0, at_final=False):
    """
    Returns a list with the timesteps where the fmin >= f0
    If at_final is True, the final timestep is counted as a commit
    """
    #     commits = [data['step'].iloc[i] for i in range(len(data)) if data['fmin'].iloc[i] >= f0]
    commits = list(data[data['fmin'] >= f0]['step'])

    if at_final and commits[-1] != data['step'].iloc[-1]:
        commits += [data['step'].iloc[-1]]

    return commits


def create_dataframe(model):
    """
    Create a dataframe from the model output
    Returns the dataframe
    """
    # Create dataframe
    nums, fmean, fstd, fmin, fmax = zip(*model.list_fit_stats)
    data = pd.DataFrame(
        {'step': range(len(model.list_fmin)), 'fmin': model.list_fmin, 'action': model.list_action,
         'fnum':nums, 'fmean':fmean, 'fstd':fstd, 'fmin':fmin, 'fmax':fmax,
         'code_size': model.total_code_size, 'changes':model.changes}
    )

    return data