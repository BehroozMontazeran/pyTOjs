"""Splitter will split a module into its components such as module_signature,
    methods_signature, dependencies_signature,sorted_signature, calls and save them in a appropriate list.

    Returns:
        lists: ast trees for Module components
"""

import os
import ast
import astunparse

from core.operator import CodeOperator, Finder
from core.log import Log

class Splitter:
    """Split a module into functions, classes, dependencies and more and save them in a appropriate list.
    """
    def __init__(self):
        self.log = Log(self.__class__.__name__)
        self.functions = []
        self.dependencies = []
        self.module_elements = []
        self.order = []
        self.calls = []
        self.code_operator = CodeOperator()
        self.finder = Finder()


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
                        'type': 'method',
                        'name': full_function_name,
                        'parameters': [arg.arg for arg in node.args.args],
                        'body': astunparse.unparse(node).strip(),
                        'start_line': start_line
                    })
                    self.parent.order.append(('method', full_function_name, start_line))

                # Recursively handle nested functions
                self.generic_visit(node)

                # Remove the last function name from the stack
                self.current_function.pop()
            else:
                function_name = node.name
                self.current_function.append(function_name)
                start_line = node.lineno

                # Check if the function is a nested function
                is_nested_function = len(self.current_function) > 2
                if function_name != '__init__' and not is_nested_function:
                    self.parent.functions.append({
                        'type': 'function',
                        'name': function_name,
                        'parameters': [arg.arg for arg in node.args.args],
                        'body': astunparse.unparse(node).strip(),
                        'start_line': start_line
                    })
                    self.parent.order.append(('function', function_name, start_line))

                # Recursively handle nested functions
                self.generic_visit(node)

                # Remove the last function name from the stack
                self.current_function.pop()

        def visit_Call(self, node):
            """Collect calls and their arguments."""
            call_name = astunparse.unparse(node.func).strip()
            arguments = [astunparse.unparse(arg).strip() for arg in node.args]
            context = ".".join(self.current_function)
            self.parent.calls.append({
                'call_name': call_name,
                'arguments': arguments,
                'context': context,
                'start_line': node.lineno
            })
            self.generic_visit(node)

    class DependencyVisitor(ast.NodeVisitor):
        """Visit each dependency in the module and save its name, value, and start_line."""
        def __init__(self, parent):
            self.parent = parent

        def visit_Import(self, node):
            """Keep track of imports."""
            for alias in node.names:
                self.parent.dependencies.append({
                    'type': 'dependency',
                    'name': alias.name,
                    'value': 'import ' + alias.name,  # Import statements don't have values
                    'start_line': node.lineno
                })
                self.parent.order.append(('dependency', alias.name, node.lineno))

        def visit_ImportFrom(self, node):
            """Keep track of imports from."""
            module_name = node.module
            for alias in node.names:
                self.parent.dependencies.append({
                    'type': 'dependency',
                    'name': alias.name,
                    'value': 'from ' + module_name + ' import ' + alias.name if module_name else alias.name,
                    'start_line': node.lineno
                })
                self.parent.order.append(('dependency', alias.name, node.lineno))


    class ModuleVisitor(ast.NodeVisitor):
        """keep track of the module-level elements and their start line numbers.
            to make sure the elements are not function-level or class-level.
        Args:
            ast (_type_): _description_
        """
        def __init__(self, parent):
            self.parent = parent
            self.within_function_or_class_stack = []
            self.current_class = []  # Track current class for nested class definitions
            
        def within_function_or_class(self):
            """Check if the current node is within a function or class."""
            return any(self.within_function_or_class_stack)
        
        def current_class_name(self):
            """Get the current full class name joined by dots."""
            return ".".join(self.current_class)

        def visit_FunctionDef(self, node):
            """Check if the function is at module-level and not within a class."""
            if not self.within_function_or_class():
                function_name = node.name
                start_line = node.lineno
                self.parent.module_elements.append({
                    'type': 'function',
                    'name': function_name,
                    'parameters': [arg.arg for arg in node.args.args],
                    'start_line': start_line
                })

            # Recursively handle nested functions
            self.within_function_or_class_stack.append(True)
            self.generic_visit(node)
            self.within_function_or_class_stack.pop()

        def visit_ClassDef(self, node):
            """check if the class is at module-level"""
            if self.within_function_or_class():
                # Handle nested classes
                self.current_class.append(node.name)
                full_class_name = self.current_class_name()
                start_line = node.lineno
                body_elements = self.extract_class_body(node.body)
                self.current_class.pop()  # After visiting the class, revert the current class context
            else:
                # Class at module level
                class_name = node.name
                self.current_class.append(class_name)
                full_class_name = self.current_class_name()
                start_line = node.lineno
                # Extract inheritance information
                bases = [base.id for base in node.bases if isinstance(base, ast.Name)] if node.bases else []
                # Append inheritance information to class metadata
                class_metadata = {
                    'type': 'class',
                    'name': full_class_name,
                    'bases': bases,
                    'start_line': start_line
                }
                # Extract other class elements
                body_elements = self.extract_class_body(node.body)
                # Append class metadata along with other class elements
                class_metadata['body'] = body_elements
                # Append class metadata to module elements
                self.parent.module_elements.append(class_metadata)
                # Append class to order list
                self.parent.order.append(('class', full_class_name, start_line))
                self.current_class.pop()
            # This ensures we don't count the class body as being within a function or class for module-level checks
            self.within_function_or_class_stack.append(True)
            self.generic_visit(node)
            self.within_function_or_class_stack.pop()

        def extract_class_body(self, body):
            """Extract methods, assignments, and constants inside a class."""
            body_elements = []
            for item in body:
                if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                    method_name = item.name
                    method_start_line = item.lineno
                    method_parameters = [arg.arg for arg in item.args.args]
                    class_name = ".".join(self.current_class)
                    body_elements.append(
                        {'type': 'method',
                         'class_name': class_name,
                         'name': method_name,
                         'parameters': method_parameters,
                         'body': astunparse.unparse(item).strip(),
                         'start_line': method_start_line})
                elif isinstance(item, ast.FunctionDef) and item.name != '__init__':
                    method_name = item.name
                    method_start_line = item.lineno
                    method_parameters = [arg.arg for arg in item.args.args]
                    class_name = ".".join(self.current_class)
                    body_elements.append(
                        {'type': 'method',
                         'class_name': class_name,
                         'name': method_name,
                         'parameters': method_parameters,
                         'start_line': method_start_line})
                elif isinstance(item, ast.Assign):
                    start_line = item.lineno
                    target_names = [t.id for t in item.targets if isinstance(t, ast.Name)]
                    if target_names:
                        value = astunparse.unparse(item.value).strip()
                        class_name = ".".join(self.current_class)
                        body_elements.append(
                            {'type': 'assign',
                            'class_name': class_name,
                            'name': target_names,
                            'value': value,
                            'start_line': start_line})
                elif isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
                    start_line = item.lineno
                    value = item.value.value
                    class_name = ".".join(self.current_class)
                    body_elements.append(
                        {'type': 'constant',
                        'class_name': class_name,
                        'value': value,
                        'start_line': start_line})
                elif isinstance(item, ast.ClassDef):
                    # Recursively handle nested classes
                    self.current_class.append(item.name)
                    nested_class_elements = self.extract_class_body(item.body)
                    body_elements.extend(nested_class_elements)
                    self.current_class.pop()

            return body_elements


        def visit_Assign(self, node):
            """keep track of assignments at module-level
            """
            if not self.within_function_or_class():
                start_line = node.lineno
                target_names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                if target_names:
                    value = astunparse.unparse(node.value).strip()
                    self.parent.module_elements.append({
                        'type': 'assign',
                        'name': target_names,
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
                    'type': 'constant',
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
                    'type': 'expression',
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
                    'type': 'for',
                    'value': value,
                    'start_line': start_line
                })

                self.parent.order.append(('for', f'for_{id(node)}', start_line))

        def visit_If(self, node):
            if not self.within_function_or_class():
                start_line = node.lineno
                value = self.get_expression_source(node)

                self.parent.module_elements.append({
                    'type': 'if',
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
                body = self.get_expression_source(node.body)
                orelse = self.get_expression_source(node.orelse)
                return f"if {test}:\n{body}\nelse:\n{orelse}"
            elif isinstance(node, ast.For):
                target = self.get_expression_source(node.target)
                iter_expr = self.get_expression_source(node.iter)
                body = '\n'.join(self.get_expression_source(stmt) for stmt in node.body)
                return f"for {target} in {iter_expr}:\n{body}"
            elif isinstance(node, ast.Constant):
                return repr(node.value)
            elif isinstance(node, ast.Assign):
                targets = ', '.join(self.get_expression_source(target) for target in node.targets)
                value = self.get_expression_source(node.value)
                return f"{targets} = {value}"
            else:
                return astunparse.unparse(node).strip()


    def parse_python_code(self, code):
        """parse the python code and extract the elements.

        Args:
            code : python code
        """
        tree = ast.parse(code)

        function_visitor = self.FunctionVisitor(self)
        dependency_visitor = self.DependencyVisitor(self)
        module_visitor = self.ModuleVisitor(self)
        self.functions, self.dependencies, self.module_elements, self.order, self.calls = [], [], [], [], []

        function_visitor.visit(tree)
        dependency_visitor.visit(tree)
        module_visitor.visit(tree)

        # Sort the order list based on start line
        sorted_order = sorted(self.order, key=lambda item: item[-1])

        
        return self.module_elements, self.functions, self.dependencies, sorted_order, self.calls

    def get_stats(self):
        """get the stats of the python code.
        """

        num_functions = len(self.functions)
        num_dependencies = len(self.dependencies)
        num_module_elements = len(self.module_elements)
        num_total_items = num_functions  + num_dependencies + num_module_elements

        self.log.info(f"Number of functions: {num_functions}")
        self.log.info(f"Number of dependencies: {num_dependencies}")
        self.log.info(f"Number of module elements: {num_module_elements}")
        self.log.info(f"Total number of items: {num_total_items}")


    def split(self, folder_path):
        """Traverse the project folder and yield the python file paths"""
        signature_list = []
        files_list = []

        if not self.finder.file_exist(folder_path):
            self.log.error(f"Folder {folder_path} does not exist")
            return [],[]
        
        def traverse_folder(folder_path):
            
            for root, dirs, files in os.walk(folder_path):
                # Filter out directories starting with dot
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    # Create a list of module names to remove local imports from prompt
                    file_name, _ = os.path.splitext(file)
                    files_list.append(file_name)
                    if file.endswith(".py") and not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        python_code = self.code_operator.read(file_path)
                        module_signature, methods_signature, dependencies_signature,sorted_signature, calls = self.parse_python_code(python_code)
                        
                        signature_dict = {
                            "file_path":file_path,
                            "module_signature":module_signature,
                            "methods_signature":methods_signature, 
                            "dependencies_signature":dependencies_signature,
                            "sorted_signature":sorted_signature,
                            "calls":calls,
                            }
                        signature_list.append(signature_dict)
            self.log.info(f"Successfully splitted {folder_path}")

        traverse_folder(folder_path)
        return signature_list, files_list
