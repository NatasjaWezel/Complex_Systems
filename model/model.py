### External imports
# Standard imports
import numpy as np
import pandas as pd
from os import path

# Specific imports
from plyj.model import MethodDeclaration
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

        # initialisations functions
        self.step_n = 0

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
                    # Add node and give it a fitness
                    self.reference_graph.add_node(java_element.name, {'method': java_element, 'class': java_class, 'fitness': self.get_fitness()})

    def get_fitness(self):
        """
        Gets fitness based on fitness method

        fitness_method == 0: returns random number between 0 and 1 (uniform distribution)
        """
        if self.fitness_method == 0:
            return np.random.random()

    def step(self):
        """
        Step function for every iteration

        Uses probabilities dictionary to determine which function to use
        """

        # Generate random number to determine which function to use
        probability = np.random.random()
        function_picker = 0

        for method in self.probabilities:
            # Get chance that belongs to the next function
            function_picker += self.probabilities[method]

            # If probability is in the right bucket
            if probability < function_picker:
                # Execute the corresponding function
                if method == "create_method":
                    self.create_method()
                elif method == "call_method":
                    self.call_method()
                elif method == "update_method":
                    self.update_method()
                elif method == "remove_method":
                    self.remove_method()
                else:
                    self.create_class()

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
        # print("create a method")
        pass

    def call_method(self):
        """
        Sample two random functions from the reference graph and use them to determine a caller and callee
        Use AST class to create a reference:
            AST.create_reference(
                caller method, callee method, callee class
            )       returns: the new reference (does not have to be used)
        Set a new fitness for the caller method
        Then add a new edge from the caller to the callee in the reference graph

        Returns:
            The number of changes made
        """
        # print("call two method")
        pass

    def update_method(self):
        """
        Pick an unfit method using pick_unfit_method()
        Then either use add or delete statement from the AST class:
            AST.add_statement(method)       returns: void
            AST.delete_statement(method)    returns: void
        Finally assign a new fitness to the method

        Returns:
            The number of changes made
        """
        print("update a method")

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
        # print("remove a method")
        pass

    def create_class(self):
        """
        Create class using AST:
            AST.create_class()      returns: Newly created class

        Returns:
            Created class
        """
        # print("create a new class")
        pass

    def pick_unfit_method(self):
        """
        Picks a method based on its (low) fitness

        Returns:
            method
        """
        pass

    def run_model(self):
        """
        Run function that completely runs the model
        """
        for _ in range(self.iterations):
            self.step()
            self.step_n += 1
