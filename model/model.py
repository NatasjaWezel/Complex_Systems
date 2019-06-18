### External imports
# Standard imports
import numpy as np
import pandas as pd
from os import path

# Specific imports
from plyj.model import MethodDeclaration, VariableDeclaration
from plyj.parser import Parser
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
        - Implement all unimplemented functions
        - Determine metric for pick_unfit_method
    """
    def __init__(self, iterations, fitness_method, probabilities):
        # params
        self.iterations = iterations
        self.fitness_method = fitness_method
        self.probabilities = probabilities

        # initialisations
        self.running = True
        self.step_n = 0
        self.possible_actions = [self.create_method, self.call_method, self.update_method, self.remove_method]
        self.changes = []
        self.fitness = []

        # AST modifications
        self.AST = AST()

        # Create basic AST from .java file and parse to a directed reference graph
        self.reference_graph = DiGraph()
        self.classes = []
        self.get_tree()

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

    def get_fitness(self):
        """
        Gets fitness based on fitness method

        fitness_method == 0: returns random number between 0 and 1 (uniform distribution)
        """
        if self.fitness_method == 0:
            return np.random.random()

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
            delta_change = action()

        self.store_fitness()

        return delta_change

    def store_fitness(self):
        """
        Append fitness of all elements in self.fitness
        """
        pass

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
        """
        if np.random.random() <= self.probabilities['create_class']:
            return 0
            # selected_class = self.create_class()
        else:
            n_methods = self.get_method_amounts()
            probabilities = list(np.array(n_methods)/np.sum(n_methods))
            selected_class = self.sample(self.classes, probabilities)
        method = self.AST.create_method(selected_class)
        fitness = self.get_fitness()
        self.reference_graph.add_node(method.name, {'method': method, 'class': selected_class, 'fitness': fitness, 'lines': 0})

        # Add statement(s) based on probability to new method here? It is created empty

    def call_method(self):
        """
        Sample two random functions from the reference graph and use them to determine a caller and callee
        Use AST class to create a reference:
            AST.create_reference(
                caller method, callee method, callee class
            )       returns: the new reference (does not have to be used)
        Set a new fitness for the caller method
        Then add a new edge from the caller to the callee in the reference graph

        A method does not call itself

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
    
        in_degrees = [1 if s == 0 else s for s in in_degrees]
        caller_method_probabilities = list(np.array(sizes)/np.sum(sizes))
        callee_method_probabilities = list(np.array(in_degrees)/np.sum(in_degrees))
        caller_info = self.sample(methods, caller_method_probabilities)
        callee_info = self.sample(methods, callee_method_probabilities)
        if caller_info['method'].name == callee_info['method'].name:
            if len(methods) > 1:
                self.call_method()
            return
        self.AST.create_reference(
            caller_info['method'], callee_info['method'], callee_info['class']
        )
        caller_info['fitness'] = self.get_fitness()
        self.reference_graph.add_edge(caller_info['method'].name, callee_info['method'].name)
        return 1

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
        """
        method = self.pick_unfit_method()
        if np.random.random() <= 0.5:
            self.AST.add_statement(method)
            self.reference_graph.nodes(data=method)[0][1]['lines'] += 1
        else:
            stmt = self.pick_statement(method)
            if stmt:
                self.AST.delete_statement(method, stmt)
                self.reference_graph.nodes(data=method)[0][1]['lines'] -= 1 if self.reference_graph.nodes(data=method)[0][1]['lines'] > 0 else 0
        self.reference_graph.nodes(data=method)[0][1]['fitness'] = self.get_fitness()
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

    def remove_method(self, method=None):
        """
        Deletes a method and deletes the method call from its callers.
        If a caller becomes empty after deleting the method, delete the caller as well and the deletion propagates

        References graph can be used to determine the references and they can be deleted using the AST class:
            AST.delete_reference(caller node, method, class node)
        After deleting all callers, the method can be deleted using:
            AST.delete_method(class node, method)
        Remove the method node from the reference graph

        Args:
            method: The method to be deleted. If None, choose one using pick_unfit_method
        Returns:
            The number of changes made
        """
        pass

    def create_class(self):
        """
        Create class using AST:
            AST.create_class()      returns: Newly created class

        Returns:
            Created class
        """
        pass

    def pick_unfit_method(self):
        """
        Picks a method based on its (low) fitness

        Currently selects the method with lowest fitness

        Returns:
            method

        TODO:
            Redesign fitness metric to base sampling on
        """
        method_fitness = ('empty', 2)
        nodes_dict = dict(self.reference_graph.nodes(data=True))
        for method_node in self.reference_graph.__iter__():
            node_data = nodes_dict[method_node]
            fitness = node_data['fitness']
            if fitness < method_fitness[1]:
                method_fitness = (node_data, fitness)
        return method_fitness[0]['method']

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
            self.probabilities['delete_method']
        ]