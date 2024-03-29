### External imports
# Standard imports
import numpy as np
import pandas as pd
from os import path
import time

# Specific imports
from plyj.model import MethodDeclaration, VariableDeclaration, MethodInvocation, ExpressionStatement
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
        exp_condition (string): String of the experiment condition
        add_state (float): Probability of adding a statement
        logging (boolean): Indicates whether a custom gource log should be made
        pref_attach_condition (integer): Condition for what kind of preferential attachment to use:
            0 = Caller and callee use pref attachment
            1 = Only caller
            2 = Only callee
            3 = No preferential attachment
    """
    def __init__(self, iterations, fitness_method, probabilities, exp_condition, add_state, logging, pref_attach_condition):
        # params
        self.iterations = iterations
        self.fitness_method = fitness_method
        self.probabilities = probabilities
        self.exp_condition = exp_condition
        self.add_state = add_state
        self.pref_attach_condition = pref_attach_condition

        # initialisations
        self.start = time.time()
        self.running = True
        self.logging = logging
        self.step_n = 0
        self.possible_actions = [self.create_method, self.call_method, self.update_method, self.remove_method]
        self.changes = []
        self.fitness = []

        # AST modifications
        self.AST = AST()

        # AST log file
        self.create_dir_prob = 0.5
        self.directory_map = {}

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
            self.directory_map[java_class.name] = ''
            self.append_log_line('A', '/' + java_class.name, 'w')
            for java_element in java_class.body:
                if isinstance(java_element, MethodDeclaration):
                    self.reference_graph.add_node(java_element.name, data={'method': java_element, 'class': java_class, 'fitness': self.get_fitness(), 'lines': 0})
                    self.append_log_line('M', '/' + java_class.name)

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

        self.reference_graph.add_node(method.name, data={'method': method, 'class': selected_class, 'fitness': fitness, 'lines': 0})
        self.append_log_line('M', self.directory_map[selected_class.name] + '/' + selected_class.name)


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
        for node, in_degree in self.reference_graph.in_degree():
            in_degrees.append(in_degree)
            data = self.reference_graph.node[node]['data']
            methods.append(data)
            sizes.append(len(data['method'].body))

        sizes = [1 if s == 0 else s+1 for s in sizes]
        in_degrees = [1 if s == 0 else s+1 for s in in_degrees]
        caller_method_probabilities = list(np.array(sizes)/np.sum(sizes))
        callee_method_probabilities = list(np.array(in_degrees)/np.sum(in_degrees))

        # Preferential attachment 2
        if self.pref_attach_condition == 0:
            caller_info = self.sample(methods, caller_method_probabilities)
            callee_info = self.sample(methods, callee_method_probabilities)
        # Caller pref attachment
        elif self.pref_attach_condition == 1:
            caller_info = self.sample(methods, caller_method_probabilities)
            callee_info = np.random.choice(methods)
        # callee pref attachment
        elif self.pref_attach_condition == 2:
            caller_info = np.random.choice(methods)
            callee_info = self.sample(methods, callee_method_probabilities)
        # No preferential attachment
        elif self.pref_attach_condition == 3:
            caller_info = np.random.choice(methods)
            callee_info = np.random.choice(methods)

        if self.exp_condition != 'reproduce':
            callee_info = self.find_callee(caller_info, callee_info, methods, callee_method_probabilities, sizes,
                                           in_degrees)
        if callee_info is None:
            return 0

        self.AST.create_reference(
            caller_info['method'], callee_info['method'], callee_info['class']
        )

        caller_info['fitness'] = self.get_fitness()
        caller_info['lines'] += 1
        self.reference_graph.add_edge(caller_info['method'].name, callee_info['method'].name)
        self.append_log_line('M', self.directory_map[caller_info['class'].name] + '/' + caller_info['class'].name)
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
        method = node['data']['method']
        change = 0
        if np.random.random() <= self.add_state:
            self.AST.add_statement(method)
            self.reference_graph.node[node['data']['method'].name]['data']['lines'] += 1
            change = 1
        else:
            stmt = self.pick_statement(method)
            if stmt:
                self.AST.delete_statement(method, stmt)
                self.reference_graph.node[node['data']['method'].name]['data']['lines'] -= 1 if self.reference_graph.node[node['data']['method'].name]['data']['lines'] > 0 else 0
                change = -1
        self.append_log_line('M', self.directory_map[node['data']['class'].name] + '/' + node['data']['class'].name)
        self.reference_graph.node[node['data']['method'].name]['data']['fitness'] = self.get_fitness()
        return change

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
            node = self.pick_unfit_method()

        method_info = node
        class_node = node['data']['class']
        method = node['data']['method'].name

        void_callers = []
        for caller in self.reference_graph.predecessors(method):
            if caller != method:
                # Get the caller and delete the reference
                caller_info = self.reference_graph.node[caller]['data']
                caller_node = caller_info['method']
                self.AST.delete_reference(caller_node, method_info['data']['method'], class_node)
                self.append_log_line('M', self.directory_map[method_info['data']['class'].name] + '/' + method_info['data']['class'].name)
                # If the caller has become empty, add it to the queue to delete later
                if len(caller_node.body) == 0:
                    void_callers.append(caller)
                else:
                    # Otherwise change its fitness
                    caller_info['fitness'] = self.get_fitness()
                    caller_info['lines'] -= 1
                    change_size -= 1
        # Delete the method after deleting all the invocation statements
        self.AST.delete_method(class_node, method_info['data']['method'])
        self.append_log_line('M', self.directory_map[method_info['data']['class'].name] + '/' + method_info['data']['class'].name)
        self.reference_graph.remove_node(method)
        if len(class_node.body) == 0:
            self.classes.remove(class_node)
            self.append_log_line('D', self.directory_map[class_node.name] + '/' + class_node.name)
            del self.directory_map[class_node.name]
        change_size -= 1

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
        self.directory_map[class_node.name] = self.get_dir()
        self.append_log_line('A', self.directory_map[class_node.name] + '/' + class_node.name)
        return class_node

    def pick_unfit_method(self):
        """
        Picks a method based on its (low) fitness

        Currently selects the method with lowest fitness

        Returns:
            method
        """
        method_fitness = ('empty', 2)
        nodes_dict = dict(self.reference_graph.nodes(data=True))
        for method_node in self.reference_graph.__iter__():
            node_data = nodes_dict[method_node]
            fitness = node_data['data']['fitness']

            if fitness < method_fitness[1]:
                method_fitness = (node_data, fitness)

        return method_fitness[0]

    def get_fmin(self):
        """
        copy of pick_unfit_method
        Currently selects the method with lowest fitness

        returns fmin
        """
        method_fitness = ('empty', 2)
        nodes_dict = dict(self.reference_graph.nodes(data=True))
        for method_node in self.reference_graph.__iter__():
            node_data = nodes_dict[method_node]['data']
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
            self.probabilities['delete_method']
        ]

    def get_fitnesses(self):
        """
        copy of pick_unfit_method
        Currently selects the method with lowest fitness

        Returns:
            list of fitnesses

        """
        nodes_dict = dict(self.reference_graph.nodes(data=True))
        return [nodes_dict[method_node]['data']['fitness'] for method_node in self.reference_graph.__iter__()]

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
        return sum([nodes_dict[method_node]['data']['lines'] for method_node in self.reference_graph.__iter__()])

    def get_dir(self):
        if self.logging == False:
            return ''

        if np.random.random() <= self.create_dir_prob:
            num = len(self.directory_map.values())
            if np.random.random() <= 0.6:
                nlp = list(self.directory_map.values()).copy()
                if '' in nlp:
                    nlp.remove('')
                if len(nlp) == 0:
                    nlp.append('/dir_' + str(int(np.random.random() * 10000)))
                return np.random.choice(nlp) + self.get_dir()
            return '/dir_' + str(num)
        else:
            return np.random.choice(list(self.directory_map.values()))

    def append_log_line(self, action, fl, param='a+'):
        if self.logging == False:
            return
        time = self.start + self.step_n * 100
        user = 'user_' + str(np.random.randint(1, 10))

        f = open("./vid/code.log", param)
        f.write(str(int(time)) + '|' + user + '|' + action + '|' + fl + '\n')
