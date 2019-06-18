from plyj.model import MethodDeclaration, ClassDeclaration, Type, Name,\
                        MethodInvocation, ExpressionStatement, VariableDeclaration,\
                        Variable, Literal, VariableDeclarator

class AST:
    """
    Main class to deal with the parsed .java file AST

    It can be used to create, update, remove, or call methods
    As well as creating and removing statements
    """
    def __init__(self):
        self.counter = 0

    def create_method(self, class_node):
        """
        Create a static method with an empty body
        The name is determined by how many methods have been created so far

        Args:
            class_node: Node of the class to create the method in

        Returns:
            Newly created method
        """
        method = MethodDeclaration(
            # Method name
            'method_' + str(self.counter),
            # Empty body
            body=[], modifiers=['static']
        )

        self.counter += 1

        # Append the method to the class
        class_node.body.append(method)
        return method

    def delete_method(self, class_node, method):
        """
        Delete a method by removing the method from a class node

        Args:
            class_node: Node of the class to remove method in
            method: Method to remove in class_node

        Returns: void
        """
        class_node.body.remove(method)

    def create_class(self, superclass_name=None):
        """
        Creates an empty class
        If superclass name is provided, the created class will extend the super class
        Otherwise, the created class will be independent

        Args:
            superclass_name: The name of the superclass to extend, default value: None

        Returns:
            Created class
        """
        java_class = ClassDeclaration('Class_' + str(self.counter), [])
        if superclass_name:
            java_class.extends = Type(Name(superclass_name))
        self.counter += 1
        return java_class

    def create_reference(self, caller_method, callee_method, callee_class):
        """
        Create a reference (call a method) from a method in a class

        Args:
            caller_method: The method to make the method call from
            callee_method: The method to call
            callee_class: The class of the method to call

        Returns:
            Created reference
        """
        ref = MethodInvocation(callee_method.name, target=Name(callee_class.name))
        caller_method.body.append(ExpressionStatement(ref))
        return ref

    def delete_reference(self, caller_method, callee_method, callee_class):
        """
        Delete a reference (method call) from a method in a class

        Args:
            caller_method: The method to make the method call from
            callee_method: The method to call
            callee_class: The class of the method to call

        Returns: void
        """
        # Add all statements that have the correct name and class
        to_delete = [stmt for stmt in caller_method.body
                     if isinstance(stmt, ExpressionStatement) and
                        isinstance(stmt.expression, MethodInvocation) and
                        stmt.expression.name == callee_method.name and
                        stmt.expression.target.value == callee_class.name]
        # Delete all correct references
        for stmt in to_delete:
            caller_method.body.remove(stmt)

    def add_statement(self, method):
        """
        Create a statement, then add it to the body of a method

        Args:
            Method to add the statement to

        Returns: void
        """
        stmt = self.create_statement()
        method.body.append(stmt)

    def create_statement(self):
        """
        Generate a variable declaration statement

        Returns:
            The created variable declaration statement
        """
        var = VariableDeclaration(
            # Create int
            type='int',
            # Declarate a variable with name counter and initialise with value counter
            variable_declarators=[VariableDeclarator(
                    variable=Variable(
                    name='var' + str(self.counter)
                ),
                initializer=Literal(self.counter)
            )]
        )
        self.counter += 1
        return var

    def delete_statement(self, method, statement):
        """
        Delete a statement in a method body after finding it

        Returns: void
        """
        stmt = next((stmt for stmt in method.body if stmt == statement), None)
        if stmt:
            method.body.remove(stmt)