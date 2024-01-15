"""Combines the code of the splitted files into one file

    Returns:
        js code: save javascript code
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

        # print(functions_ast)
        # Create a dictionary of functions from the functions AST
        elements_dict = {node.id.name: node for node in elements_ast if isinstance(node, esprima.nodes.FunctionDeclaration)}
        # print(functions_dict)
        # Replace functions in the AST
        self.replace_functions(base_ast, elements_dict)

        # Create the code from the AST
        modified_code = self.ast_to_code(base_ast.body)
        # print(modified_code)
        # with open('combined_code.js', 'w') as file:
        #     file.write(modified_code)
        # Save the code
        self.code_saver.save(js_path, modified_code, 'w')

    def ast_to_code(self,node):
        """Convert the AST to code"""
        if isinstance(node, list):
            return ''.join(self.ast_to_code(child) for child in node)
        elif isinstance(node, esprima.nodes.FunctionDeclaration):
            params = ', '.join(param.name for param in node.params)
            body = self.ast_to_code(node.body)
            return f'function {node.id.name}({params}) {body}'
        elif isinstance(node, esprima.nodes.BlockStatement):
            return f'{{{"; ".join(self.ast_to_code(statement) for statement in node.body)}}}'
        else:
            return jsbeautifier.beautify(escodegen.generate(node))

    def replace_functions(self, node, functions_code):
        """Replace the functions in the AST with the code from the functions_code dict"""
        for i, _ in enumerate(node.body):
            for j, _ in enumerate(node.body[i].body.body):
                # print("///////////"+ node.body[i].body.body[j].key.name)
                if node.body[i].body.body[j].key.name in functions_code:  
                    # Replace only the body of the function with the one from the functions code
                    replacement_ast = functions_code[node.body[i].body.body[j].key.name]
                    # print( replacement_ast.body)
                    node.body[i].body.body[j].value.params = replacement_ast.params
                    node.body[i].body.body[j].value.body = replacement_ast.body
                    # Drop the function, not to be used for furthur classes.
                    functions_code.pop(node.body[i].body.body[j].key.name)
                    # print("************"+ functions_code.id.name +'//////'+functions_code.id.body)
                # else:
                    # print("///////////Not a function")
        
        # # Recursively process statements within the body
        # if hasattr(node, 'body') and isinstance(node.body, list):
        #     for i, statement in enumerate(node.body):
        #         node.body[i] = replace_functions(statement, functions_code)
        
        return node
    
    def ast_creator(self, base_code, elements):
        """Create an AST from the base code and the elements code"""
        # Beautify the main code (optional, but can help with parsing)
        beautified_code = jsbeautifier.beautify(base_code)

        # Parse the beautified code to generate an AST
        base_ast = esprima.parseScript(beautified_code, loc=True)

        # Parse the functions code to create AST nodes
        elements_ast = esprima.parseScript(elements, loc=True).body

        return base_ast, elements_ast
