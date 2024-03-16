"""Splitter will split a module into functions, classes, and dependencies and save them in the appropriate lists.

    Returns:
        lists: ast trees for each function, class, and dependency
"""

import ast
import astunparse

from core.log import Log

class Splitter:
    """Split a module into functions, classes, and dependencies and save them in the appropriate lists.
    """
    def __init__(self):
        self.log = Log(self.__class__.__name__)
        self.functions = []
        self.classes = []
        self.dependencies = set()
        self.module_elements = []
        self.order = []

    class FunctionVisitor(ast.NodeVisitor):
        """visit each function in the module and save its name, parameters, and body.
            
        """
        def __init__(self, parent):
            self.parent = parent

        def visit_FunctionDef(self, node):
            """keep track of functions and their parameters and body

            Args:
                code: a python module
            """
            function_name = node.name
            start_line = node.lineno
            if function_name != '__init__':
                self.parent.functions.append({
                    'name': function_name,
                    'parameters': [arg.arg for arg in node.args.args],
                    'body': astunparse.unparse(node).strip(),
                    'start_line': start_line
                })
                self.parent.order.append(('function', function_name, start_line))

    class ClassVisitor(ast.NodeVisitor):
        """visit each class in the module and save its name, body, and start line number.
        """
        def __init__(self, parent):
            self.parent = parent

        def visit_ClassDef(self, node):
            """keep track of classes and their body
            Args:
                code: a python module
            """
            class_name = node.name
            start_line = node.lineno

            # Extract class body
            body_elements = self.extract_class_body(node.body)

            self.parent.classes.append({
                'name': class_name,
                'body': body_elements,
                'start_line': start_line
            })
            self.parent.order.append(('class', class_name, start_line))

        def extract_class_body(self, body):
            """extract methods, assignments, and constants inside a class

            Args:
                class: python class

            Returns:
                list(dict): list of elements in the class
            """
            body_elements = []
            for item in body:
                if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                    method_name = item.name
                    method_start_line = item.lineno
                    body_elements.append(('method', method_name, method_start_line, astunparse.unparse(item).strip()))
                elif isinstance(item, ast.FunctionDef) and item.name != '__init__':
                    method_name = item.name
                    method_start_line = item.lineno
                    method_parameters = [arg.arg for arg in item.args.args]
                    body_elements.append(('method', method_name, method_start_line, method_parameters))
                elif isinstance(item, ast.Assign):
                    start_line = item.lineno
                    target_names = [t.id for t in item.targets if isinstance(t, ast.Name)]
                    if target_names:
                        value = astunparse.unparse(item.value).strip()
                        body_elements.append(('assign', target_names, value, start_line))
                elif isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
                    start_line = item.lineno
                    value = item.value.value
                    body_elements.append(('constant', f'constant_{id(item.value)}', value, start_line))
            return body_elements

    class DependencyVisitor(ast.NodeVisitor):
        """visit each dependency in the module and save its name.

        Args:
            code: a python module
        """
        def __init__(self, parent):
            self.parent = parent

        def visit_Import(self, node):
            """keep track of imports
            Args:
                code: a python module
            """
            for alias in node.names:
                self.parent.dependencies.add(alias.name)

        def visit_ImportFrom(self, node):
            """keep track of imports from
            Args:
                code: a python module
            """
            module_name = node.module
            if module_name is not None:
                self.parent.dependencies.add(module_name)

    class ModuleVisitor(ast.NodeVisitor):
        """keep track of the module-level elements and their start line numbers.
            to make sure the elements are not function-level or class-level.
        Args:
            ast (_type_): _description_
        """
        def __init__(self, parent):
            self.parent = parent
            self.within_function_or_class = False

        def visit_FunctionDef(self, node):
            """check if the function is at module-level
            """
            self.within_function_or_class = True
            self.generic_visit(node)
            self.within_function_or_class = False

        def visit_ClassDef(self, node):
            """check if the class is at module-level
            """
            self.within_function_or_class = True
            self.generic_visit(node)
            self.within_function_or_class = False

        def visit_Assign(self, node):
            """keep track of assignments at module-level
            """
            if not self.within_function_or_class:
                start_line = node.lineno
                target_names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                if target_names:
                    value = astunparse.unparse(node.value).strip()
                    self.parent.module_elements.append({
                        'names': target_names,
                        'value': value,
                        'start_line': start_line
                    })
                    for name in target_names:
                        self.parent.order.append(('assign', name, start_line))

        def visit_Constant(self, node):
            """keep track of constants at module-level
            """
            if not self.within_function_or_class:
                start_line = node.lineno
                self.parent.module_elements.append({
                    'names': [f'constant_{id(node)}'],
                    'value': node.value,
                    'start_line': start_line
                })
                self.parent.order.append(('constant', f'constant_{id(node)}', start_line))

        def visit_Expr(self, node):
            """keep track of assignments at module-level
            """
            if isinstance(node.value, ast.Constant) and not self.within_function_or_class:
                start_line = node.lineno
                value = node.value.value
                self.parent.module_elements.append({
                    'names': [f'constant_{id(node.value)}'],
                    'value': value,
                    'start_line': start_line
                })
                self.parent.order.append(('constant', f'constant_{id(node.value)}', start_line))

        def visit_Import(self, node):
            """keep track of imports and their start line numbers
            """
            start_line = node.lineno
            for alias in node.names:
                self.parent.dependencies.add(alias.name)
                self.parent.order.append(('import', alias.name, start_line))

        def visit_ImportFrom(self, node):
            """keep track of import from and their start line numbers
            """
            start_line = node.lineno
            module_name = node.module
            if module_name is not None:
                self.parent.dependencies.add(module_name)
                self.parent.order.append(('import_from', module_name, start_line))

    def parse_python_code(self, code):
        """parse the python code and extract the elements.

        Args:
            code : python code
        """
        tree = ast.parse(code)

        function_visitor = self.FunctionVisitor(self)
        class_visitor = self.ClassVisitor(self)
        dependency_visitor = self.DependencyVisitor(self)
        module_visitor = self.ModuleVisitor(self)

        function_visitor.visit(tree)
        class_visitor.visit(tree)
        dependency_visitor.visit(tree)
        module_visitor.visit(tree)

        # Sort the order list based on start line
        sorted_order = sorted(self.order, key=lambda item: item[-1])

        # self.log.info(f"Functions: {self.functions}")
        # self.log.info(f"Classes: {self.classes}")
        # self.log.info(f"Dependencies: {self.dependencies}")
        # self.log.info(f"Module Elements: {self.module_elements}")
        # self.log.info(f"Sorted Order: {sorted_order}")
        self.log.info("The whole module is splitted into functions, classes, dependencies, and module elements.")
        return self.classes, self.functions, self.dependencies, self.module_elements, sorted_order

    def get_stats(self):
        """get the stats of the python code.
        """
        num_functions = len(self.functions)
        num_classes = len(self.classes)
        num_dependencies = len(self.dependencies)
        num_module_elements = len(self.module_elements)
        num_total_items = num_functions + num_classes + num_dependencies + num_module_elements

        self.log.info(f"Number of functions: {num_functions}")
        self.log.info(f"Number of classes: {num_classes}")
        self.log.info(f"Number of dependencies: {num_dependencies}")
        self.log.info(f"Number of module elements: {num_module_elements}")
        self.log.info(f"Total number of items: {num_total_items}")



# [TODO] write a translator that translates the ast tree of classes to js,
#  using the following prompt: 
# User
# use the following ast output of a python file and make the classes,
# functions  assignments and constants in the proper order based on start line in javascript: 

# [TODO]These lines should be moved to loop.py
# if __name__ == "__main__":
#     with open('py_codes/project_example/environment_all.py', 'r', encoding="utf-8") as f:
#         python_code = f.read()

#     splitter = Splitter()
#     ast_classes, ast_functions, _,_,_ = splitter.parse_python_code(python_code)
#     splitter.get_stats()
    