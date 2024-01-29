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
    # Initialize the classes
    operator = CodeOperator()
    split = Splitter()
    combine = Combiner()
    project_path = ProjectOperator()
    # Read a complex python code from the file
    python_code = operator.read(PATH)
    # Create a folder and its subfolders for the project
    project_path, js_path, function_path = project_path.project_creator(PATH)
    if project_path:
        # Open a connection to GPT 3.5
        connectors = api.gpt.OpenAIConnector()
        # Split the python code into classes, functions
        module_signature, methods_signature, dependencies_signature, module_elements_signature,_ = split.parse_python_code(python_code)
        # combine the signatures based on need
        signatures = combine.sort_by_start_line([module_signature, methods_signature, dependencies_signature, module_elements_signature])
        # Translate all non-module signature to JavaScript
        py_translator = translators.PyTranslator(connectors)
        if len(module_signature) == 0:
            module = None
            non_module = py_translator.py_translator_checker(project_path, python_code)
        else:
            # Translate module signature to JavaScript
            module = py_translator.py_translator_checker(project_path, module_signature, dependencies_signature, module_elements_signature)
        if module:
            for i, signature in enumerate(methods_signature):
                # Create a unit test code for the python function by GPT 3.5
                py_unittest_prompter = translators.PyUnittestPrompter(connectors)
                py_unittest = py_unittest_prompter.py_unittest_checker(project_path, signature, module_signature)
                if py_unittest:
                    # Translate the python method to javascript by GPT 3.5
                    py_translator = translators.PyTranslator(connectors)
                    translated_func = py_translator.py_translator_checker(project_path, signature, func_trans=True)
                    if translated_func:
                        # Translate the generated unit test code to javascript by GPT 3.5
                        py_unittest_translator = translators.PyUnittestTranslator(connectors)
                        py_unittest_translator.py_translator_checker(project_path, signature, py_unittest, translated_func)

        if module and py_unittest_translator:
            # read the code from the files
            base_code = operator.read(js_path)
            elements_code = operator.read(function_path)
            # Combine the generated code to one file
            combine.combine(js_path, base_code, elements_code)

