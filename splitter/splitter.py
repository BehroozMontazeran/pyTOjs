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
        self.dependencies = []
        self.module_elements = []
        self.order = []



    # class FunctionVisitor(ast.NodeVisitor):
    #     """Visit each function in the module and save its name, parameters, and body."""

    #     def __init__(self, parent):
    #         self.parent = parent
    #         self.current_function = []

    #     def visit_ClassDef(self, node):
    #         """Keep track of class name and enter class context."""
    #         self.current_function.append(node.name)
    #         self.generic_visit(node)
    #         self.current_function.pop()

    #     def visit_FunctionDef(self, node):
    #         """Keep track of functions and their parameters and body."""
    #         if self.current_function:  # Check if inside a class
    #             function_name = node.name
    #             self.current_function.append(function_name)
    #             full_function_name = ".".join(self.current_function)
    #             start_line = node.lineno

    #             if function_name != '__init__':
    #                 self.parent.functions.append({
    #                     'name': full_function_name,
    #                     'parameters': [arg.arg for arg in node.args.args],
    #                     'body': astunparse.unparse(node).strip(),
    #                     'start_line': start_line
    #                 })
    #                 self.parent.order.append(('function', full_function_name, start_line))

    #             # Recursively handle nested functions
    #             self.generic_visit(node)

    #             # Remove the last function name from the stack
    #             self.current_function.pop()


    class FunctionVisitor(ast.NodeVisitor):
        """Visit each function in the module and save its name, parameters, and body."""

        def __init__(self, parent):
            self.parent = parent
            self.current_function = []

        def visit_ClassDef(self, node):
            """Keep track of class name and enter class context."""
            self.current_function.append(node.name)
            self.generic_visit(node)
            self.current_function.pop()

        def visit_FunctionDef(self, node):
            """Keep track of functions and their parameters and body."""
            if self.current_function:  # Check if inside a class
                function_name = node.name
                self.current_function.append(function_name)
                full_function_name = ".".join(self.current_function)
                start_line = node.lineno

                # Check if the function is a nested function
                is_nested_function = len(self.current_function) > 2

                if function_name != '__init__' and not is_nested_function:
                    self.parent.functions.append({
                        'name': full_function_name,
                        'parameters': [arg.arg for arg in node.args.args],
                        'body': astunparse.unparse(node).strip(),
                        'start_line': start_line
                    })
                    self.parent.order.append(('function', full_function_name, start_line))

                # Recursively handle nested functions
                self.generic_visit(node)

                # Remove the last function name from the stack
                self.current_function.pop()



    # class FunctionVisitor(ast.NodeVisitor):
    #     """Visit each function in the module and save its name, parameters, and body."""

    #     def __init__(self, parent):
    #         self.parent = parent
    #         self.current_function = []

    #     def visit_FunctionDef(self, node):
    #         """Keep track of functions and their parameters and body."""
    #         function_name = node.name
    #         self.current_function.append(function_name)
    #         full_function_name = ".".join(self.current_function)
    #         start_line = node.lineno

    #         if function_name != '__init__':
    #             self.parent.functions.append({
    #                 'name': full_function_name,
    #                 'parameters': [arg.arg for arg in node.args.args],
    #                 'body': astunparse.unparse(node).strip(),
    #                 'start_line': start_line
    #             })
    #             self.parent.order.append(('function', full_function_name, start_line))

    #         # Recursively handle nested functions
    #         self.generic_visit(node)

    #         # Remove the last function name from the stack
    #         self.current_function.pop()


    class ClassVisitor(ast.NodeVisitor):
        """Visit each class in the module and save its name, body, and start line number."""
        def __init__(self, parent):
            self.parent = parent
            self.current_class = []

        def visit_ClassDef(self, node):
            """Keep track of classes and their body."""
            class_name = node.name
            self.current_class.append(class_name)
            full_class_name = ".".join(self.current_class)
            start_line = node.lineno

            # Extract class body
            body_elements = self.extract_class_body(node.body)

            # Remove the last class name from the current class stack
            self.current_class.pop()

            self.parent.classes.append({
                'name': full_class_name,
                'body': body_elements,
                'start_line': start_line
            })
            self.parent.order.append(('class', full_class_name, start_line))

        def extract_class_body(self, body):
            """Extract methods, assignments, and constants inside a class."""
            body_elements = []
            for item in body:
                if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                    method_name = item.name
                    method_start_line = item.lineno
                    body_elements.append(('method', ".".join(self.current_class), method_name, method_start_line, astunparse.unparse(item).strip()))
                elif isinstance(item, ast.FunctionDef) and item.name != '__init__':
                    method_name = item.name
                    method_start_line = item.lineno
                    method_parameters = [arg.arg for arg in item.args.args]
                    body_elements.append(('method', ".".join(self.current_class), method_name, method_start_line, method_parameters))
                elif isinstance(item, ast.Assign):
                    start_line = item.lineno
                    target_names = [t.id for t in item.targets if isinstance(t, ast.Name)]
                    if target_names:
                        value = astunparse.unparse(item.value).strip()
                        body_elements.append(('assign', ".".join(self.current_class), target_names, value, start_line))
                elif isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
                    start_line = item.lineno
                    value = item.value.value
                    body_elements.append(('constant', ".".join(self.current_class), f'constant_{id(item.value)}', value, start_line))
                elif isinstance(item, ast.ClassDef):
                    # Recursively handle nested classes
                    self.current_class.append(item.name)
                    nested_class_elements = self.extract_class_body(item.body)
                    body_elements.extend(nested_class_elements)
                    self.current_class.pop()

            return body_elements

    # class ClassVisitor(ast.NodeVisitor):
    #     """visit each class in the module and save its name, body, and start line number.
    #     """
    #     def __init__(self, parent):
    #         self.parent = parent

    #     def visit_ClassDef(self, node):
    #         """keep track of classes and their body
    #         Args:
    #             code: a python module
    #         """
    #         class_name = node.name
    #         start_line = node.lineno

    #         # Extract class body
    #         body_elements = self.extract_class_body(node.body)

    #         self.parent.classes.append({
    #             'name': class_name,
    #             'body': body_elements,
    #             'start_line': start_line
    #         })
    #         self.parent.order.append(('class', class_name, start_line))

    #     def extract_class_body(self, body):
    #         """extract methods, assignments, and constants inside a class

    #         Args:
    #             class: python class

    #         Returns:
    #             list(dict): list of elements in the class
    #         """
    #         body_elements = []
    #         for item in body:
    #             if isinstance(item, ast.FunctionDef) and item.name == '__init__':
    #                 method_name = item.name
    #                 method_start_line = item.lineno
    #                 body_elements.append(('method', method_name, method_start_line, astunparse.unparse(item).strip()))
    #             elif isinstance(item, ast.FunctionDef) and item.name != '__init__':
    #                 method_name = item.name
    #                 method_start_line = item.lineno
    #                 method_parameters = [arg.arg for arg in item.args.args]
    #                 body_elements.append(('method', method_name, method_start_line, method_parameters))
    #             elif isinstance(item, ast.Assign):
    #                 start_line = item.lineno
    #                 target_names = [t.id for t in item.targets if isinstance(t, ast.Name)]
    #                 if target_names:
    #                     value = astunparse.unparse(item.value).strip()
    #                     body_elements.append(('assign', target_names, value, start_line))
    #             elif isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
    #                 start_line = item.lineno
    #                 value = item.value.value
    #                 body_elements.append(('constant', f'constant_{id(item.value)}', value, start_line))
    #         return body_elements

    class DependencyVisitor(ast.NodeVisitor):
        """Visit each dependency in the module and save its name, value, and start_line."""
        def __init__(self, parent):
            self.parent = parent
            # self.dependencies_list = []

        def visit_Import(self, node):
            """Keep track of imports."""
            for alias in node.names:
                self.parent.dependencies.append({
                    'name': alias.name,
                    'value': 'import ' + alias.name,  # Import statements don't have values
                    'start_line': node.lineno
                })
                # self.dependencies_list.append(dependency_info)

        def visit_ImportFrom(self, node):
            """Keep track of imports from."""
            module_name = node.module
            for alias in node.names:
                self.parent.dependencies.append({
                    'name': alias.name,
                    'value': 'from ' + module_name + ' import ' + alias.name if module_name else alias.name,
                    'start_line': node.lineno
                })
                # self.dependencies_list.append(dependency_info)


    class ModuleVisitor(ast.NodeVisitor):
        """keep track of the module-level elements and their start line numbers.
            to make sure the elements are not function-level or class-level.
        Args:
            ast (_type_): _description_
        """
        def __init__(self, parent):
            self.parent = parent
            self.within_function_or_class_stack = []

        # def visit_FunctionDef(self, node):
        #     """check if the function is at module-level
        #     """
        #     self.within_function_or_class = True
        #     self.generic_visit(node)
        #     self.within_function_or_class = False
            
        def within_function_or_class(self):
            """Check if the current node is within a function or class."""
            return any(self.within_function_or_class_stack)

        def visit_FunctionDef(self, node):
            """Check if the function is at module-level and not within a class."""
            if not self.within_function_or_class():
                function_name = node.name
                start_line = node.lineno
                self.parent.module_elements.append({
                    'name': function_name,
                    'parameters': [arg.arg for arg in node.args.args],
                    'body': astunparse.unparse(node).strip(),
                    'start_line': start_line
                })
                self.parent.order.append(('function', function_name, start_line))

            # Recursively handle nested functions
            self.within_function_or_class_stack.append(True)
            self.generic_visit(node)
            self.within_function_or_class_stack.pop()


        def visit_ClassDef(self, node):
            """check if the class is at module-level
            """
            self.within_function_or_class_stack.append(True)
            self.generic_visit(node)
            self.within_function_or_class_stack.pop()

        # def visit_Assign(self, node):
        #     """Handle DataFrame assignment."""
        #     if not self.within_function_or_class():
        #         for target in node.targets:
        #             if (
        #                 isinstance(target, ast.Subscript)
        #                 and isinstance(target.slice, ast.Index)
        #                 and isinstance(target.slice.value, ast.Constant)
        #                 and isinstance(target.value, ast.Name)
        #             ):
        #                 dataframe_name = target.value.id
        #                 column_name = target.slice.value.s
        #                 start_line = node.lineno
        #                 value = astunparse.unparse(node.value).strip()

        #                 self.parent.module_elements.append({
        #                     'name': f'{dataframe_name}["{column_name}"]',
        #                     'value': value,
        #                     'start_line': start_line
        #                 })

        #                 self.parent.order.append(('assign', f'{dataframe_name}["{column_name}"]', start_line))

        #     self.generic_visit(node)

        def visit_Assign(self, node):
            """keep track of assignments at module-level
            """
            if not self.within_function_or_class():
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
            if not self.within_function_or_class():
                start_line = node.lineno
                self.parent.module_elements.append({
                    'names': [f'constant_{id(node)}'],
                    'value': node.value,
                    'start_line': start_line
                })
                self.parent.order.append(('constant', f'constant_{id(node)}', start_line))

        def visit_Expr(self, node):
            """keep track of expressions at module-level
            """
            if not self.within_function_or_class():
                start_line = node.lineno
                value = self.get_expression_source(node)

                self.parent.module_elements.append({
                    'id': f'expr_{id(node)}',
                    'value': value,
                    'start_line': start_line
                })

                self.parent.order.append(('expression', f'expr_{id(node)}', start_line))

            self.generic_visit(node)


        def visit_For(self, node):
            if not self.within_function_or_class():
                start_line = node.lineno
                value = self.get_expression_source(node)

                self.parent.module_elements.append({
                    'id': f'for_{id(node)}',
                    'value': value,
                    'start_line': start_line
                })

                self.parent.order.append(('for', f'for_{id(node)}', start_line))

        def visit_If(self, node):
            if not self.within_function_or_class():
                start_line = node.lineno
                value = self.get_expression_source(node)

                self.parent.module_elements.append({
                    'id': f'if_{id(node)}',
                    'value': value,
                    'start_line': start_line
                })

                self.parent.order.append(('if', f'if_{id(node)}', start_line))


        def get_expression_source(self, node):
            """Recursively reconstruct the source code for an expression."""
            if isinstance(node, ast.Expr):
                return self.get_expression_source(node.value)
            elif isinstance(node, ast.BinOp):
                left = self.get_expression_source(node.left)
                op = astunparse.unparse(node.op)
                right = self.get_expression_source(node.right)
                return f"{left} {op} {right}"
            elif isinstance(node, ast.UnaryOp):
                op = astunparse.unparse(node.op)
                operand = self.get_expression_source(node.operand)
                return f"{op}{operand}"
            elif isinstance(node, ast.Attribute):
                value = self.get_expression_source(node.value)
                attr = node.attr
                return f"{value}.{attr}"
            elif isinstance(node, ast.Call):
                func = self.get_expression_source(node.func)
                args = ', '.join(self.get_expression_source(arg) for arg in node.args)
                return f"{func}({args})"
            elif isinstance(node, ast.If):
                test = self.get_expression_source(node.test)
                body = '\n'.join(self.get_expression_source(stmt) for stmt in node.body)
                orelse = '\n'.join(self.get_expression_source(stmt) for stmt in node.orelse)
                return f"if {test}:\n{body}\nelse:\n{orelse}"
            elif isinstance(node, ast.For):
                target = self.get_expression_source(node.target)
                iter_expr = self.get_expression_source(node.iter)
                body = '\n'.join(self.get_expression_source(stmt) for stmt in node.body)
                return f"for {target} in {iter_expr}:\n{body}"
            else:
                return astunparse.unparse(node).strip()




        # def visit_Expr(self, node):
        #     """keep track of assignments and expressions at module-level
        #     """
        #     if not self.within_function_or_class:
        #         start_line = node.lineno

        #         if isinstance(node.value, ast.Constant):
        #             # Handle constant expressions
        #             value = node.value.value
        #             self.parent.module_elements.append({
        #                 'names': [f'constant_{id(node.value)}'],
        #                 'value': value,
        #                 'start_line': start_line
        #             })
        #             self.parent.order.append(('constant', f'constant_{id(node.value)}', start_line))
        #         else:
        #             # Handle other expressions
        #             value = astunparse.unparse(node.value).strip()
        #             self.parent.module_elements.append({
        #                 'names': [f'expr_{id(node)}'],
        #                 'value': value,
        #                 'start_line': start_line
        #             })
        #             self.parent.order.append(('expression', f'expr_{id(node)}', start_line))

        #     self.generic_visit(node)


    # class ModuleVisitor(ast.NodeVisitor):
    #     """keep track of the module-level elements and their start line numbers.
    #         to make sure the elements are not function-level or class-level.
    #     Args:
    #         ast (_type_): _description_
    #     """
    #     def __init__(self, parent):
    #         self.parent = parent
    #         self.within_function_or_class = False

    #     def visit_FunctionDef(self, node):
    #         """check if the function is at module-level
    #         """
    #         self.within_function_or_class = True
    #         self.generic_visit(node)
    #         self.within_function_or_class = False

    #     def visit_ClassDef(self, node):
    #         """check if the class is at module-level
    #         """
    #         self.within_function_or_class = True
    #         self.generic_visit(node)
    #         self.within_function_or_class = False

    #     def visit_Assign(self, node):
    #         """keep track of assignments at module-level
    #         """
    #         if not self.within_function_or_class:
    #             start_line = node.lineno
    #             target_names = [t.id for t in node.targets if isinstance(t, ast.Name)]
    #             if target_names:
    #                 value = astunparse.unparse(node.value).strip()
    #                 self.parent.module_elements.append({
    #                     'names': target_names,
    #                     'value': value,
    #                     'start_line': start_line
    #                 })
    #                 for name in target_names:
    #                     self.parent.order.append(('assign', name, start_line))

    #     def visit_Constant(self, node):
    #         """keep track of constants at module-level
    #         """
    #         if not self.within_function_or_class:
    #             start_line = node.lineno
    #             self.parent.module_elements.append({
    #                 'names': [f'constant_{id(node)}'],
    #                 'value': node.value,
    #                 'start_line': start_line
    #             })
    #             self.parent.order.append(('constant', f'constant_{id(node)}', start_line))

    #     def visit_Expr(self, node):
    #         """keep track of assignments at module-level
    #         """
    #         if isinstance(node.value, ast.Constant) and not self.within_function_or_class:
    #             start_line = node.lineno
    #             value = node.value.value
    #             self.parent.module_elements.append({
    #                 'names': [f'constant_{id(node.value)}'],
    #                 'value': value,
    #                 'start_line': start_line
    #             })
    #             self.parent.order.append(('constant', f'constant_{id(node.value)}', start_line))


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

