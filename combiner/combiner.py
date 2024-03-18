"""Combines the code of the splitted files from functions and target js module into the target js file. 
"""
import esprima
import escodegen
import jsbeautifier

from core.operator import CodeOperator
from core.log import Log

class Combiner:
    """Combines the code of the splitted files into one file"""
    def __init__(self):
        self.log = Log(self.__class__.__name__)
        self.code_saver = CodeOperator()

    def combine(self,js_path, base_code, elements_code):
        """Combine the base code with the elements code"""

        # parse the code into an AST
        base_ast, elements_ast = self.ast_creator(base_code, elements_code)

        # Create a dictionary of functions from the functions AST
        elements_dict = {node.id.name: node for node in elements_ast if isinstance(node, esprima.nodes.FunctionDeclaration)}

        # Replace functions in the AST
        self.replace_functions(base_ast, elements_dict)

        # Create the code from the AST
        modified_code = self.ast_to_code(base_ast.body)

        # Save the code
        self.code_saver.save(js_path, modified_code, 'w')

    def ast_to_code(self,node):
        """Convert the AST to code"""
        if isinstance(node, list):
            return ''.join(self.ast_to_code(child) for child in node)
        elif isinstance(node, esprima.nodes.FunctionDeclaration):
            params = ', '.join(param.name for param in node.params if param.name is not None)
            body = self.ast_to_code(node.body)
            return f'function {node.id.name}({params}) {body}'
        elif isinstance(node, esprima.nodes.BlockStatement):
            return f'{{{"; ".join(self.ast_to_code(statement) for statement in node.body)}}}'
        else:
            # options for beautifying the code
            opts = jsbeautifier.default_options()
            opts.indent_size = 2  # Set indentation size to 2 spaces
            opts.indent_char = ' '  # Use space for indentation (use '\t' for tabs)
            opts.max_preserve_newlines = -1  # Unlimited newlines
            opts.preserve_newlines = True
            opts.keep_array_indentation = False
            opts.break_chained_methods = True
            opts.indent_scripts = 'normal'
            opts.brace_style = 'collapse,preserve-inline'
            opts.space_before_conditional = True
            opts.unescape_strings = False
            opts.jslint_happy = False
            opts.end_with_newline = True
            opts.wrap_line_length = 0  # Disable line wrapping
            opts.indent_empty_lines = False
            opts.comma_first = False

            # Beautify the generated code with specified options
            beautified_code = jsbeautifier.beautify(escodegen.generate(node), opts)
            return beautified_code

    def replace_functions(self, node, functions_code):
        """Replace the functions in the AST with the code from the functions_code dict"""

        cl_fn_list = self.cl_fn_separator(functions_code)
        try:
            # Replace methods of a class
            for i, _ in enumerate(node.body):
                if node.body[i].type == 'ClassDeclaration':
                    for j, _ in enumerate(node.body[i].body.body):
                        for _, (key, class_name, function_name) in enumerate(cl_fn_list):
                            if (node.body[i].body.body[j].type == 'MethodDefinition' and
                                node.body[i].body.body[j].key.name == function_name and
                                node.body[i].body.body[j].key.name != 'constructor'):
                                replacement_ast = functions_code[key]
                                # Replace the body and params of the function with the one from the functions code
                                node.body[i].body.body[j].value.params = replacement_ast.params
                                node.body[i].body.body[j].value.body = replacement_ast.body
                                # Drop the function, not to be used for furthur classes.
                                functions_code.pop(key)
                # Replace the functions inside the class or without a class
                elif node.body[i].type == 'FunctionDeclaration':
                    for _, (key, class_name, function_name) in enumerate(cl_fn_list):
                        if (node.body[i].type == 'FunctionDeclaration' and
                            node.body[i].id.name == function_name):
                            # Replace the body and params of the function with the one from the functions code
                            replacement_ast = functions_code[key]
                            node.body[i].params = replacement_ast.params
                            node.body[i].body = replacement_ast.body
                            # Drop the function, not to be used for furthur usages.
                            functions_code.pop(key)
                            break
            return node
        except Exception as e:
            self.log.error(f"Error in replacing_functions: {e}")
            return None
    
    def ast_creator(self, base_code, elements):
        """Create an AST from the base code and the elements code"""
        # Beautify the main code (optional, but can help with parsing)
        beautified_code = jsbeautifier.beautify(base_code)

        # Parse the beautified code to generate an AST
        base_ast = esprima.parseScript(beautified_code, loc=True)

        # Parse the functions code to create AST nodes
        elements_ast = esprima.parseScript(elements, loc=True).body

        return base_ast, elements_ast
    
    def sort_by_start_line(self, list_of_lists):
        """Sort the list of lists based on the start_line of the first element in the list"""
        # Flatten the list of lists into a single list of dictionaries
        flat_list = [item for sublist in list_of_lists for item in sublist]
        
        # Sort the flat list based on 'start_line'
        sorted_list = sorted(flat_list, key=lambda x: x.get('start_line', float('inf')))
        
        return sorted_list
    
    def cl_fn_separator(self, functions_code):
        """Separate translated function names into classes and functions based on the naming convention from splitter"""
        cl_fn_list = []

        for key in list(functions_code.keys()):  # Using list() to avoid RuntimeError during iteration
            if key[0].isupper():
                class_name, function_name = key.split('_', 1)
                cl_fn_list.append((key, class_name, function_name))

            else:
                cl_fn_list.append((key, '_', key))

        return cl_fn_list
