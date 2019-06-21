### External imports
# Standard imports
import numpy as np
import pandas as pd
from scipy.stats import norm
from os import path

# Specific imports
from plyj.model import MethodDeclaration, VariableDeclaration, MethodInvocation, ExpressionStatement
from plyj.parser import Parser

import networkx as nx
from networkx import DiGraph

# Model class imports
from AST import AST


class code_dev_simulation():
    """
    The main model class for simulating a software development process.

    A directed graph is created to keep track of code references, while the java source code
    is stored internally in an AST

    Args:
        iterations (int): Total amount of iterations to simulate
        fitness_method (int): The method indication to define the fitness metric
        probabilities (dict<string, int>): Maps probability to a certain function

    TODO:
        - Determine metric for pick_unfit_method
        - Determine better fitness metric, maybe based on amount of lines in a method
    """
    def __init__(self, iterations, fitness_method, probabilities, exp_condition):
        # params
        self.iterations = iterations
        self.fitness_method = fitness_method
        self.probabilities = probabilities
        self.exp_condition = exp_condition

        # initialisations
        self.running = True
        self.step_n = 0
        self.possible_actions = [self.create_method, self.call_method, self.update_method, self.remove_method, self.batch_change]
        self.changes = []
        self.fitness = []

        # AST modifications
        self.AST = AST()

        # Create basic AST from .java file and parse to a directed reference graph
        self.reference_graph = DiGraph()
        self.classes = []
        self.get_tree()

        # Analysis lists
        self.list_fmin = []
        self.list_action = []
        self.list_fitnesses = []
        self.list_fit_stats = []
        self.total_code_size = []

    def get_tree(self):
        """
        Parse a .java file and get its declarations, then initialise the references
        """
        with open(path.join(path.dirname(__file__), './', 'app.java')) as j_file:
            parser = Parser()
            tree = parser.parse_file(j_file)
            initial_classes = tree.type_declarations

        self.initialise_references(initial_classes)

    def initialise_references(self, initial_classes):
        """
        Initialise the reference graph by adding methods in the initial java file as nodes
        They are initialised with a method name, their class, and a fitness value
        The classes are added to a list

        Args:
            initial_classes (list): The initial classes to instantiate the reference graph with
        """
        for java_class in initial_classes:
            self.classes.append(java_class)
            for java_element in java_class.body:
                if isinstance(java_element, MethodDeclaration):
                    self.reference_graph.add_node(java_element.name, {'method': java_element, 'class': java_class, 'fitness': self.get_fitness(), 'lines': 0})

    def batch_change(self):
        self.remove_method()
        for i in range(np.random.randint(0, high=10)):
            self.update_method()
        return 1

    def get_default_fitness(self):
        """
        Initialise a fitness for a to be created node based on the total amount of methods
        """
        return 1 / max(len(self.reference_graph.nodes()), 1)

    def get_fitness(self, node=None):
        """
        Gets fitness based on fitness method

        fitness_method == 0: returns random number between 0 and 1 (uniform distribution)
        fitness_method == 1: returns probabilities based on page ranking and amount of method calls
        """
        if self.fitness_method == 0:
            return np.random.random()
        elif self.fitness_method == 1:
            if node == None:
                return self.get_default_fitness()
            pr = nx.pagerank(self.reference_graph, alpha=0.9, max_iter=500)
            self.set_new_fitenesses(pr)
            nodes_dict = dict(self.reference_graph.nodes(data=True))
            return nodes_dict[node]['fitness']

    def set_new_fitenesses(self, pr):
        nodes_dict = dict(self.reference_graph.nodes(data=True))
        line_weights = {}
        for node in nodes_dict:
            line_weights[node] = max(nodes_dict[node]['lines'], 1)

        line_sum = max(sum(line_weights.values()), 1)

        for node in line_weights:
            line_weights[node] /= line_sum

        stdev = 0.4
        for node in pr.keys():
            node_data = nodes_dict[node]
            stdev_ = np.interp(line_weights[node], (min(line_weights.values()), max(line_weights.values())), (-stdev, stdev))
            node_data['fitness'] = min(max(pr[node] + np.random.uniform(low=-stdev_, high=stdev_), 0), 1)
            # dont delete pls (pr[node] + line_weights[node]) / 2


    def run_model(self):
        """
        Run function that completely runs the model
        """
        for _ in range(self.iterations):
            self.changes.append(self.step())
            self.step_n += 1

    def step(self):
        """
        Step function for every iteration

        Uses probabilities dictionary to determine which function to use
        """
        action = self.sample(self.possible_actions, self.get_probabilities())
        delta_change = 0

        while delta_change == 0:
            action = self.sample(self.possible_actions, self.get_probabilities())
            delta_change = action()

        self.save_states(action)

        return delta_change

    def save_states(self, action):
        """
        Saves the state of the model every step

        Args:
            action (function): The function that is called this step
        """
        self.list_fmin.append(self.get_fmin())
        self.list_action.append(action.__name__)
        fitnesses = self.get_fitnesses()
        self.list_fit_stats.append(self.fitness_stats(fitnesses))
        self.total_code_size.append(self.get_total_code_size())

    def create_method(self):
        """
        Creates a method

        Uses probabilities['create_class] to determine whether to create the method in a new class
        A class is selected, then created using the method in the AST class:
            AST.create_method(class)        returns: the new method
        Its class is added to the classes list.
        The method is finally added to the reference graph with its class and fitness as properties

        Returns:
            The number of changes made

        TODO:
            - Should a statement automatically be created when a method is created?
              Consistent empty method creation does not make much sense
            - But it also doesn't really matter what's in the method right?
        """
        if np.random.random() <= self.probabilities['create_class']:
            selected_class = self.create_class()
            changes = 2
        else:
            n_methods = self.get_method_amounts()
            probabilities = list(np.array(n_methods)/np.sum(n_methods))
            selected_class = self.sample(self.classes, probabilities)
            changes = 1
        method = self.AST.create_method(selected_class)
        fitness = self.get_fitness()
        self.reference_graph.add_node(method.name, {'method': method, 'class': selected_class, 'fitness': fitness, 'lines': 0})

        # Add statement(s) based on probability to new method here? It is created empty

        # Method created and class created/modified
        return changes

    def call_method(self):
        """
        Sample two random functions from the reference graph and use them to determine a caller and callee
        Use AST class to create a reference:
            AST.create_reference(
                caller method, callee method, callee class
            )       returns: the new reference (does not have to be used)
        Set a new fitness for the caller method
        Then add a new edge from the caller to the callee in the reference graph

        A method does not call itself, and does not call another method twice

        Returns:
            The number of changes made
        """
        methods = []
        sizes = []
        in_degrees = []
        for node, in_degree in self.reference_graph.in_degree_iter():
            in_degrees.append(in_degree)
            data = self.reference_graph.node[node]
            methods.append(data)
            sizes.append(len(data['method'].body))

        sizes = [1 if s == 0 else s+1 for s in sizes]
        in_degrees = [1 if s == 0 else s+1 for s in in_degrees]
        caller_method_probabilities = list(np.array(sizes)/np.sum(sizes))
        callee_method_probabilities = list(np.array(in_degrees)/np.sum(in_degrees))
        caller_info = self.sample(methods, caller_method_probabilities)
        callee_info = self.sample(methods, callee_method_probabilities)

        if self.exp_condition != 'reproduce':
            callee_info = self.find_callee(caller_info, callee_info, methods, callee_method_probabilities, sizes,
                                           in_degrees)
        if callee_info is None:
            return 0

        self.AST.create_reference(
            caller_info['method'], callee_info['method'], callee_info['class']
        )

        caller_info['fitness'] = self.get_fitness(caller_info['method'].name)
        caller_info['lines'] += 1
        self.reference_graph.add_edge(caller_info['method'].name, callee_info['method'].name)
        return 1

    def call_exists(self, callee_method, caller_method):
        """
        Checks whether a call to callee is already being made in the caller

        Returns: (bool) True if a call is already being made
        """
        callee_class = callee_method['class']
        callee_method = callee_method['method']
        caller_method = caller_method['method']
        for stmt in caller_method.body:
            if isinstance(stmt, ExpressionStatement) and\
                        isinstance(stmt.expression, MethodInvocation) and\
                        stmt.expression.name == callee_method.name and\
                        stmt.expression.target.value == callee_class.name:
                return True
        return False

    def find_callee(self, caller_info, callee_info, methods, callee_method_probabilities, sizes, in_degrees):
        """
        Find a method to call that is not equal to the caller and has not been called by the caller already

        Args:
            caller_info: caller function node
            callee_info: callee function node
            methods (list): list of all the available methods to call
            callee_method_probabilities (list<float>): Probabilities for every function to be called
            sizes (list<int>): List of all sizes of methods
            in_degrees (list<int>): List of all the references a method has

        Returns:
            Callee method or None if no methods available
        """
        while caller_info['method'].name == callee_info['method'].name or self.call_exists(callee_info,caller_info):

            callee_info = self.sample(methods, callee_method_probabilities)
            callee_method_probabilities.pop(methods.index(callee_info))
            sizes.pop(methods.index(callee_info))
            in_degrees.pop(methods.index(callee_info))
            callee_method_probabilities = list(np.array(in_degrees)/np.sum(in_degrees))
            methods.remove(callee_info)
            if len(methods) == 0:
                return None
        return callee_info

    def update_method(self):
        """
        Pick an unfit method using pick_unfit_method()
        Then either use add or delete statement from the AST class:
            AST.add_statement(method)       returns: void
            AST.delete_statement(method)    returns: void

        Currently 50% chance to either add or delete statement

        Finally assign a new fitness to the method

        Returns:
            The number of changes made

        TODO:
            - Design conditions to add or delete statements
            - Think the chance to add a statement should be higher, since repos
            - grow?
        """
        node = self.pick_unfit_method()
        method = node['method']
        if np.random.random() <= 1:
            self.AST.add_statement(method)
            self.reference_graph.node[node['method'].name]['lines'] += 1
        else:
            stmt = self.pick_statement(method)
            if stmt:
                self.AST.delete_statement(method, stmt)
                self.reference_graph.node[node['method'].name]['lines'] -= 1 if self.reference_graph.node[node['method'].name]['lines'] > 0 else 0
        self.reference_graph.node[node['method'].name]['fitness'] = self.get_fitness(node['method'].name)
        return 1

    def pick_statement(self, method):
        """
        Pick a statement and return it

        Currently a random statement (variable declaration) is picked in the method uniformly

        Args:
            method: Method to pick a statement from

        Returns:
            Statement or None if method no statements
        """
        declarations = []
        for java_element in method.body:
                if isinstance(java_element, VariableDeclaration):
                    declarations.append(java_element)
        if len(declarations) > 0:
            return np.random.choice(declarations)
        else:
            return None

    def remove_method(self, node=None):
        """
        Deletes a method and deletes the method call from its callers.
        If a caller becomes empty after deleting the method, delete the caller as well and the deletion propagates

        References graph can be used to determine the references and they can be deleted using the AST class:
            AST.delete_reference(caller node, method, class node)
        After deleting all callers, the method can be deleted using:
            AST.delete_method(class node, method)
        Remove the method node from the reference graph

        Args:
            node: The method node to be deleted. If None, choose one using pick_unfit_method
        Returns:
            The number of changes made
        """
        change_size = 0
        if len(self.reference_graph.nodes()) == 1:
            return 0
        if node is None:
            node = self.pick_unfit_method('norm')

        method_info = node
        method = node['method'].name
        class_node = node['class']

        void_callers = []
        for caller in self.reference_graph.predecessors_iter(method):
            if caller != method:
                # Get the caller and delete the reference
                caller_info = self.reference_graph.node[caller]
                caller_node = caller_info['method']
                self.AST.delete_reference(caller_node, method_info['method'], class_node)
                # If the caller has become empty, add it to the queue to delete later
                if len(caller_node.body) == 0:
                    void_callers.append(caller)
                else:
                    # Otherwise change its fitness
                    caller_info['fitness'] = self.get_fitness(caller_info['method'].name)
                    caller_info['lines'] -= 1
                    change_size += 1
        # Delete the method after deleting all the invocation statements
        self.AST.delete_method(class_node, method_info['method'])
        self.reference_graph.remove_node(method)
        if len(class_node.body) == 0:
            self.classes.remove(class_node)
        change_size += 1

        # Then recursively do the same for all the methods that have become empty in the process
        for caller in void_callers:
            change_size += self.remove_method(self.get_node_data(caller))
        return change_size

    def create_class(self):
        """
        Create class using AST:
            AST.create_class()      returns: Newly created class

        Returns:
            Created class
        """
        class_node = self.AST.create_class()
        self.classes.append(class_node)
        return class_node

    def pick_unfit_method(self, dist='exp'):
        """
        Picks a method based on its (low) fitness

        Currently selects the method with lowest fitness

        Returns:
            method

        TODO:
            Redesign fitness metric to base sampling on
        """
        lamda = 1
        nodes_dict = dict(self.reference_graph.nodes(data=True))
        sorted_array = [a[1] for a in sorted(nodes_dict.items(), key=lambda x: x[1]['fitness'])]
        
        if dist == 'exp':
            x = np.linspace(0, 5, len(sorted_array))
            dist = lamda * np.exp(-lamda * x)
        else:
            x = np.linspace(norm.ppf(0.01), norm.ppf(0.99), len(sorted_array))
            dist = norm.pdf(x)

        dist /= sum(dist)

        return np.random.choice(sorted_array, p=dist)

    def get_fmin(self):
        """
        copy of pick_unfit_method
        Currently selects the method with lowest fitness

        returns fmin
        """
        method_fitness = ('empty', 2)
        nodes_dict = dict(self.reference_graph.nodes(data=True))
        for method_node in self.reference_graph.__iter__():
            node_data = nodes_dict[method_node]
            fitness = node_data['fitness']
            if fitness < method_fitness[1]:
                method_fitness = (node_data, fitness)
        return method_fitness[1]

    def get_node_data(self, node):
        """
        Return node data from the reference graph

        Args:
            node (string): The name of the node to return the data of

        Returns:
            Data of the node defined in the reference graph
        """
        nodes_dict = dict(self.reference_graph.nodes(data=True))
        return nodes_dict[node]

    def sample(self, elements, probalities):
        """
        Sample a list of elements using a list of probalities (same order)

        Args:
            elements (list<any>): List of elements to sample
            probalities (list<float>): List of floats that specify the weight for each element in elements

        Returns:
            Sampled element from elements
        """
        return np.random.choice(elements, p=probalities)

    def get_method_amounts(self):
        """
        Get the amount of methods in all classes

        Returns (list<int>) List of amount of methods in same order as self.classes
        """
        class_n_methods = []
        for java_class in self.classes:
            n_methods = 0
            for java_element in java_class.body:
                if isinstance(java_element, MethodDeclaration):
                    n_methods += 1
            class_n_methods.append(n_methods)
        return class_n_methods

    def get_probabilities(self):
        """
        Get a list of the four method probabilities in order:
        Create, call, update, and delete respectively

        Returns:
            List<float> probabilities of four method manipulation functions
        """
        return [
            self.probabilities['create_method'],
            self.probabilities['call_method'],
            self.probabilities['update_method'],
            self.probabilities['delete_method'],
            self.probabilities['batch_change']
        ]

    def get_fitnesses(self):
        """
        copy of pick_unfit_method
        Currently selects the method with lowest fitness

        Returns:
            list of fitnesses

        """
        nodes_dict = dict(self.reference_graph.nodes(data=True))
        return [nodes_dict[method_node]['fitness'] for method_node in self.reference_graph.__iter__()]

    def fitness_stats(self, fitnesses):
        """
        Gets list of fitnesses of the methods as input
        Returns a list of mean, std, min, max values
        """
        fitnesses = np.array(fitnesses)
        return [len(fitnesses), fitnesses.mean(), fitnesses.std(), fitnesses.min(), fitnesses.max()]

    def get_total_code_size(self):
        """
        Save the total code base size (total amount of method lines) by summing the lines of each method
        """
        nodes_dict = dict(self.reference_graph.nodes(data=True))
        return sum([nodes_dict[method_node]['lines'] for method_node in self.reference_graph.__iter__()])