"""Run the program by one call."""
# import subprocess
import api
import translators
# import splitter
# import combiner

from config import PATH
from core.operator import CodeOperator, ProjectOperator
from splitter.splitter import Splitter
from combiner.combiner import Combiner




if __name__ == "__main__":
    # Read a complex python code from the file
    python_code = CodeOperator()
    python_code = python_code.read(PATH, 'r')
    # Create a folder and its subfolders for the project
    project_path = ProjectOperator()
    project_path = project_path.project_creator(PATH)
    if project_path:
        # Open a connection to GPT 3.5
        connectors = api.gpt.OpenAIConnector()
        # Split the python code into classes, functions
        split = Splitter()
        module_signature, functions_signature, _,_,_ = split.parse_python_code(python_code)
        # Translate module signature to JavaScript
        py_translator = translators.PyTranslator(connectors)
        module = py_translator.py_translator_checker(project_path, module_signature)
        if module:
            for i, signature in enumerate(functions_signature):
                # Create a unit test code for the python function by GPT 3.5
                py_unittest_prompter = translators.PyUnittestPrompter(connectors)
                py_unittest = py_unittest_prompter.py_unittest_checker(project_path, signature, module_signature)
                if py_unittest:
                    # Translate the python function to javascript by GPT 3.5
                    py_translator = translators.PyTranslator(connectors)
                    translated_func = py_translator.py_translator_checker(project_path, signature, func_trans=True)
                    if translated_func:
                        # Translate the generated unit test code to javascript by GPT 3.5
                        py_unittest_translator = translators.PyUnittestTranslator(connectors)
                        py_unittest_translator.py_translator_checker(project_path, signature, py_unittest, translated_func)

        if module and py_unittest_translator:
            # read the code from the files
            base_code = CodeOperator.read('main_code.js', 'r')
            elements_code = CodeOperator.read('functions_code.js', 'r')

            # Combine the generated code to one file
            combine = Combiner()
            combine.combine(base_code, elements_code)
