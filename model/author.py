from mesa import Agent
import numpy as np
import re

class Author(Agent):
    """
    The author agent class for repository agent based model simulation using commits.

    This class inherits the Agent class from the mesa library.
    The agents commit to certain files based on some probability or rules each iteration

    Args:
        name (int): ID of the agent
        model (:obj: model): The top-level ABM
        agent_type (int): Type of agent

    TODO:
        - Make actual author class based on logical rules
        - Add removal of lines
    """
    def __init__(self, unique_id, model, agent_type):
        # params
        self.unique_id = unique_id
        self.model = model
        self.agent_type = agent_type

        # initialisations
        self.commits = 0
        self.committed_lines = 0

    def step(self):
        """
        Author step function that is called each iteration
        Determines how the agent should act during this iteration
        """

        repo_files = list(self.model.repository.keys())

        ### Random demonstration implementation ###

        if self.agent_type == 0:

            # 10% chance to create new file (uniform distr)
            # or create file if none created yet
            if np.random.random() >= 0.9 or len(repo_files) == 0:
                self.create_file()
            
            repo_files = list(self.model.repository.keys())

            # 50% chance to add lines to a file (uniform distr)
            if np.random.random() >= 0.5:
                # Choose random file
                file_name = repo_files[np.random.randint(0, len(repo_files))]
                # Commit N lines to the file
                lines = self.get_n_lines()
                self.model.repository[file_name] += lines
                self.add_lines(lines)

    def initialise_first_file(self):
        """
        Create the first file in a repository
        """
        n_lines = self.get_n_lines()
        self.model.repository['file_1'] = n_lines
        self.add_lines(n_lines)

    def create_file(self):
        """
        Create a new file in the repository and commit N lines to it
        """
        repo_files = list(self.model.repository.keys())
        print(self.model.repository)
        if len(repo_files) > 0:
            new_file = re.search('(.*_)', repo_files[-1]).group(1)
            new_num = int(re.search('\_([0-9]+)', repo_files[-1]).group(1)) + 1
            new_file += str(new_num)
            print(new_file)
            n_lines = self.get_n_lines()
            self.model.repository[new_file] = n_lines
            self.add_lines(n_lines)
        else:
            self.initialise_first_file()

    def add_lines(self, n_lines):
        """
        Increment internal storage of committed lines and add to model log
        """
        self.commits += 1
        self.committed_lines += n_lines
        self.model.commit_delta_log.append(n_lines)

    def get_n_lines(self):
        """
        Commit a certain amount of lines to a file
        Type 0 = uniformly distributed between 1 and 1000
        """
        if self.agent_type == 0:
            return np.random.randint(1, 1000)