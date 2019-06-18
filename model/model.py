# External imports
import numpy as np
import pandas as pd
# mesa
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

# Model class imports
from author import Author

class commit_simulation(Model):
    """
    The main model class for repository agent based model simulation using commits.

    This class inherits the model class from the mesa library.
    It creates agents who commit based on certain probabilities.
    The agents share a resource, the repository, and all have access to the same information

    Args:
        n_authors (int): Amount of agents to use in the model
        iterations (int): Total amount of iterations to simulate
        agent_type (int): Indicates how/when the agent decides to create commit

    TODO:
        - Determine all required parameters
        - Determine correct schedule
        - Determine time line (natural or commit based)
    """
    def __init__(self, n_authors, iterations, agent_type):
        # params
        self.n_authors = n_authors
        self.iterations = iterations
        self.agent_type = agent_type

        # initialisations
        self.agents = []
        self.repository = {}
        self.commit_delta_log = []

        # Random activation
        self.schedule = RandomActivation(self)
        self.datacollector = DataCollector(
            agent_reporters={"Commits": "commits",
                             "Committed lines": "committed_lines"})
        self.running = True

        # initialisations functions
        self.init_agents()
        self.step_n = 0

        # Collect first time
        self.datacollector.collect(self)

    def init_agents(self):
        """
        Initialise the agents based on amount of agents and their types
        """
        for i in range(self.n_authors):
            agent = Author(i, self, self.agent_type)
            self.agents.append(agent)
            self.schedule.add(agent)
    
    def step(self):
        """
        Mesa step function, collects data and advances the scheduler
        """
        self.datacollector.collect(self)
        self.schedule.step()
        self.step_n += 1

    def run_model(self):
        """
        Run function that completely runs the model
        """
        for _ in range(self.iterations):
            self.step()