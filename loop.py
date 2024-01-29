"""Run the program by one call."""
# import subprocess
import api
import translators
# import splitter
# import combiner

from config import DATA_POOL #PATH
from core.analyzer import Analyzer
from core.operator import CodeOperator, ProjectOperator, Finder
from splitter.splitter import Splitter
from combiner.combiner import Combiner


def run(code_operator, finder, splitter, combiner, project_operator, file_path, noncomplex=False):
    """Run the program on each module separately."""
    # Read a complex python code from the file
    python_code = code_operator.read(file_path)
    # Create a folder and its subfolders for the project[TODO: check the address]
    project_path, js_path, function_path = project_operator.project_creator(file_path)
    if project_path:
        # Open a connection to GPT 3.5
        connectors = api.gpt.OpenAIConnector()
        py_translator = translators.PyTranslator(connectors)
        # Split the python code into classes, functions
        module_signature, methods_signature, dependencies_signature, module_elements_signature,_ = splitter.parse_python_code(python_code)
        # check if corresponding dependencies are in counterparts.json
        counterparts, nonavailables = finder.counterparts_finder(dependencies_signature)
        # Prompt for counterparts of python libraries that are not in counterparts.json and update counterparts.json and install them
        if nonavailables:
            counterparts_prompter = translators.CounterpartsPrompter(connectors)
            installed_counterparts = counterparts_prompter.dependencies_prompter_and_installer(counterparts, nonavailables)
        else:
            # Check if all needed counterparts are installed
            _, error = counterparts_prompter.install_dependencies(counterparts)
            if not error:
                installed_counterparts = counterparts
        # Translate dependencies to JavaScript
        # if dependencies_signature:
        #     dependencies = py_translator.dependencies_translator_and_installer(dependencies_signature)
        # Combine the signatures based on need
        sorted_signatures = combiner.sort_by_start_line([module_signature, methods_signature, dependencies_signature, module_elements_signature])
        # Translate noncomplex code to JavaScript
        if noncomplex:
            module = None
            non_module = py_translator.py_translator_checker(project_path, python_code, installed_counterparts)
            if non_module:
                # Create a unit test code for the python module by GPT 3.5
                py_unittest_prompter = translators.PyUnittestPrompter(connectors)
                py_unittest = py_unittest_prompter.py_unittest_checker(project_path, python_code, module_signature)
                if py_unittest:
                    # Translate the generated unit test code to javascript by GPT 3.5
                    py_unittest_translator = translators.PyUnittestTranslator(connectors)
                    py_unittest_translator.py_translator_checker(project_path, python_code, py_unittest, non_module)
        else:
            # Translate module signature to JavaScript
            module = py_translator.py_translator_checker(project_path, module_signature, installed_counterparts, dependencies_signature, module_elements_signature)
        if module:
            for _, signature in enumerate(methods_signature):
                # Create a unit test code for the python function by GPT 3.5
                py_unittest_prompter = translators.PyUnittestPrompter(connectors)
                py_unittest = py_unittest_prompter.py_unittest_checker(project_path, signature, module_signature)
                if py_unittest:
                    # Translate the python method to javascript by GPT 3.5
                    py_translator = translators.PyTranslator(connectors)
                    translated_func = py_translator.py_translator_checker(project_path, signature, installed_counterparts, func_trans=True)
                    if translated_func:
                        # Translate the generated unit test code to javascript by GPT 3.5
                        py_unittest_translator = translators.PyUnittestTranslator(connectors)
                        py_unittest_translator.py_translator_checker(project_path, signature, py_unittest, translated_func)

        if module and py_unittest_translator:
            # read the code from the files
            base_code = code_operator.read(js_path)
            elements_code = code_operator.read(function_path)
            # Combine the generated code to one file
            combiner.combine(js_path, base_code, elements_code)
    # # Read a complex python code from the file
    # python_code = code_operator.read(file_path)
    # # Create a folder and its subfolders for the project[TODO: check the address]
    # project_path, js_path, function_path = project_operator.project_creator(file_path)
    # if project_path:
    #     # Open a connection to GPT 3.5
    #     connectors = api.gpt.OpenAIConnector()
    #     py_translator = translators.PyTranslator(connectors)
    #     # Split the python code into classes, functions
    #     module_signature, methods_signature, dependencies_signature, module_elements_signature,_ = splitter.parse_python_code(python_code)
    #     # check if corresponding dependencies are in counterparts.json
    #     counterparts, nonavailables = finder.counterparts_finder(dependencies_signature)
    #     # Prompt for counterparts of python libraries that are not in counterparts.json and update counterparts.json
    #     if nonavailables:
    #         counterparts_prompter = translators.CounterpartsPrompter(connectors)
    #         installed_counterparts = counterparts_prompter.dependencies_prompter_and_installer(counterparts, nonavailables)
    #     # Translate dependencies to JavaScript
    #     # if dependencies_signature:
    #     #     dependencies = py_translator.dependencies_translator_and_installer(dependencies_signature)
    #     # Combine the signatures based on need
    #     sorted_signatures = combiner.sort_by_start_line([module_signature, methods_signature, dependencies_signature, module_elements_signature])
    #     # Translate all non-module signature to JavaScript
    #     if len(module_signature) == 0:
    #         module = None
    #         non_module = py_translator.py_translator_checker(project_path, python_code, installed_counterparts)
    #     else:
    #         # Translate module signature to JavaScript
    #         module = py_translator.py_translator_checker(project_path, module_signature, installed_counterparts, dependencies_signature, module_elements_signature)
    #     if module:
    #         for _, signature in enumerate(methods_signature):
    #             # Create a unit test code for the python function by GPT 3.5
    #             py_unittest_prompter = translators.PyUnittestPrompter(connectors)
    #             py_unittest = py_unittest_prompter.py_unittest_checker(project_path, signature, module_signature)
    #             if py_unittest:
    #                 # Translate the python method to javascript by GPT 3.5
    #                 py_translator = translators.PyTranslator(connectors)
    #                 translated_func = py_translator.py_translator_checker(project_path, signature, installed_counterparts, func_trans=True)
    #                 if translated_func:
    #                     # Translate the generated unit test code to javascript by GPT 3.5
    #                     py_unittest_translator = translators.PyUnittestTranslator(connectors)
    #                     py_unittest_translator.py_translator_checker(project_path, signature, py_unittest, translated_func)

    #     if module and py_unittest_translator:
    #         # read the code from the files
    #         base_code = code_operator.read(js_path)
    #         elements_code = code_operator.read(function_path)
    #         # Combine the generated code to one file
    #         combiner.combine(js_path, base_code, elements_code)

if __name__ == "__main__":

    # Initialize the classes
    code_operators = CodeOperator()
    finders = Finder()
    splitters = Splitter()
    combiners = Combiner()
    project_operators = ProjectOperator()
    analyzer = Analyzer()

    # Create a generator object for .py files
    py_file_generator = project_operators.traverse_project(DATA_POOL)

    # Iterate through the generator
    for py_path in py_file_generator:
        # analyze the python module
        loc = analyzer.analyze(py_path)
        if loc < 200:
            # Run for small modules which don't need splitting and combining
            run(code_operators, finders, splitters, combiners, project_operators, py_path, noncomplex=True)
        # Process the .py file
        run(code_operators, finders, splitters, combiners, project_operators, py_path)