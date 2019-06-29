from plyj.model import MethodDeclaration
from plyj.parser import Parser
from random import random, choice
from utils import sample
from code_modifier import CodeModifier
from os import path
from networkx import DiGraph
import numpy as np


class Evolver:
    def __init__(self, iterations, fitness_method, probabilities, exp_condition, add_state, logging, initial_classes=None):
        """
        :param initial_classes: assuming these classes has no method calls to or inheritances from each other
        :return: None
        """
        # params
        self.iterations = iterations
        self.fitness_method = fitness_method
        self.probabilities = probabilities
        self.exp_condition = exp_condition
        self.add_state = add_state

        if initial_classes is None:
            with open(path.join(path.dirname(__file__), '..', 'App.java')) as java_file:
                parser = Parser()
                tree = parser.parse_file(java_file)
                initial_classes = tree.type_declarations
        self.p_create_class = 0.1
        self.p_no_inherit = 0.2
        self.code_modifier = CodeModifier()
        self.inheritance_graph = DiGraph()
        self.reference_graph = DiGraph()
        self.fitness = []
        self.step_n = 0

        for c in initial_classes:
            self.inheritance_graph.add_node(c.name, {'class': c})
            for m in c.body:
                if isinstance(m, MethodDeclaration):
                    self.reference_graph.add_node(m.name, {'method': m, 'class': c, 'fitness': random(), 'lines': 0})

        # Analysis lists
        self.list_fmin = []
        self.list_action = []
        self.list_fitnesses = []
        self.list_fit_stats = []
        self.total_code_size = []
        self.changes = []


    def save_states(self, action):
        """
        Saves the state of the model every step

        Args:
            action (function): The function that is called this step
        """
        # self.list_fmin.append(self.get_fmin())
        self.list_action.append(action.__name__)
        fitnesses = self.get_fitnesses()
        self.list_fit_stats.append(self.fitness_stats(fitnesses))
        self.total_code_size.append(self.get_total_code_size())


    def get_total_code_size(self):
        """
        Save the total code base size (total amount of method lines) by summing the lines of each method
        """
        nodes_dict = dict(self.reference_graph.nodes(data=True))
        # fitnesses = [data['fitness'] for method, data in self.reference_graph.nodes_iter(True)]

        return sum([nodes_dict[method_node]['lines'] for method_node in self.reference_graph.__iter__()])

    def fitness_stats(self, fitnesses):
        """
        Gets list of fitnesses of the methods as input
        Returns a list of mean, std, min, max values
        """
        fitnesses = np.array(fitnesses)
        return [len(fitnesses), fitnesses.mean(), fitnesses.std(), fitnesses.min(), fitnesses.max()]


    # def get_fitnesses(self):
    #     """
    #     copy of pick_unfit_method
    #     Currently selects the method with lowest fitness
    #
    #     Returns:
    #         list of fitnesses
    #
    #     """
    #     nodes_dict = dict(self.reference_graph.nodes(data=True))
    #     return [nodes_dict[method_node]['data']['fitness'] for method_node in self.reference_graph.__iter__()]


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


    def run_model(self):
        """
        Run function that completely runs the model
        """
        for _ in range(self.iterations):
            self.changes.append(self.step())
            self.step_n += 1

    def step(self):
        p_create_method = 0.2
        p_call_method = 1 - p_create_method
        p_delete_method = 0.1
        p_update_method = 1 - p_delete_method
        change_size = 0
        while change_size == 0:
            action = sample([self.create_method, self.call_method, self.update_method, self.delete_method],
                            [p_create_method, p_call_method, p_update_method, p_delete_method])
            change_size = action()
        print('number of methods: %d' % self.reference_graph.number_of_nodes())

        self.list_fmin.append(self.choose_unfit_method()[1])
        self.save_states(action)
        return change_size

    def create_method(self):
        print('creating a method')
        klass = None
        if random() < self.p_create_class:
            klass = self.create_class()
            changes = 2
        else:
            classes = []
            sizes = []
            for node, data in self.inheritance_graph.nodes_iter(data=True):
                classes.append(data['class'])
                sizes.append(len(data['class'].body))
            klass = sample(classes, [s + 1 for s in sizes])
            changes = 1
        method = self.code_modifier.create_method(klass)
        self.reference_graph.add_node(method.name, {'method': method, 'class': klass, 'fitness': random(), 'lines': 0})
        return changes

    def call_method(self):
        print('calling a method')
        methods = []
        sizes = []
        in_degrees = []
        for node, in_degree in self.reference_graph.in_degree_iter():
            in_degrees.append(in_degree)
            data = self.reference_graph.node[node]
            methods.append(data)
            sizes.append(len(data['method'].body))

        caller_info = sample(methods, [s + 1 for s in sizes])
        callee_info = sample(methods, [d + 1 for d in in_degrees])
        self.code_modifier.create_reference(
            caller_info['method'], callee_info['method'], callee_info['class'])
        # The will introduce some instability when the probability of creating and deleting methods drops to near 0
        caller_info['fitness'] = random()
        callee_info['lines'] += 1
        self.reference_graph.add_edge(caller_info['method'].name, callee_info['method'].name)
        return 1

    def update_method(self):
        print('updating a method')
        method = self.choose_unfit_method()[0]
        method_info = self.reference_graph.node[method]
        self.code_modifier.add_statement(method_info['method'])
        method_info['fitness'] = random()
        method_info['lines'] += 1
        return 1

    def delete_method(self, method=None):
        """
        Delete a method and delete the method call from its callers. It a caller becomes
        empty after deleting the method, delete the caller as well and the deletion propagates
        :param method: The method to be deleted. If None, randomly choose one
        :return: The number of changes made
        """
        print('deleting a method')
        change_size = 0
        if self.reference_graph.number_of_nodes() == 1:
            # Don't delete the last method
            return 0
        if method is None:
            # method = choice(self.reference_graph.nodes())
            method = self.choose_unfit_method()[0]
        method_info = self.reference_graph.node[method]
        class_node = method_info['class']
        void_callers = []
        for caller in self.reference_graph.predecessors_iter(method):
            if caller != method:
                caller_info = self.reference_graph.node[caller]
                caller_node = caller_info['method']
                self.code_modifier.delete_reference(caller_node, method_info['method'], class_node)
                if len(caller_node.body) == 0:
                    void_callers.append(caller)
                else:
                    caller_info['fitness'] = random()
                    caller_info['lines'] -= 1
                    change_size += 1
        self.code_modifier.delete_method(class_node, method_info['method'])
        change_size += 1
        self.reference_graph.remove_node(method)
        if len(class_node.body) == 0:
            self.inheritance_graph.remove_node(class_node.name)
        # recursively remove all void callers
        for caller in void_callers:
            change_size += self.delete_method(caller)
        return -change_size

    def create_class(self):
        superclass_name = None
        if random() > self.p_no_inherit:
            class_names = []
            num_subclasses = []
            for node, in_degree in self.inheritance_graph.in_degree_iter():
                class_names.append(node)
                num_subclasses.append(in_degree)

            superclass_name = sample(class_names, [n + 1 for n in num_subclasses])
        klass = self.code_modifier.create_class(superclass_name)
        self.inheritance_graph.add_node(klass.name, {'class': klass})
        if superclass_name:
            self.inheritance_graph.add_edge(klass.name, superclass_name)
        return klass

    def choose_unfit_method(self):
        """
        :return: the method with least fitness number. Can change to a probabilistic function that biases towards
        less fit methods if the current implementation makes the system too stable
        """
        min_fitness = 1
        unfit_method = None
        for method, data in self.reference_graph.nodes_iter(True):
            if data['fitness'] < min_fitness:
                min_fitness = data['fitness']
                unfit_method = method
        return unfit_method, min_fitness

    def get_fitnesses(self):
        fitnesses = [data['fitness'] for method, data in self.reference_graph.nodes_iter(True)]
        return fitnesses


