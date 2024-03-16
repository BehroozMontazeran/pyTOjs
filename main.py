"""Run the program by one call."""
# import subprocess
# from itertools import count
import api
import translators
# import splitter
# import combiner

from config import DATA_POOL #PATH
from core.analyzer import Analyzer
from core.operator import CodeOperator, ProjectOperator, Finder
from splitter.splitter import Splitter
from combiner.combiner import Combiner


def run(code_operator, finder, splitter, combiner, project_operator, py_signature, files, cmplx=True):
    """Run the program on each module separately."""

    project_path, js_path, function_path = project_operator.project_creator(py_signature['file_path'], cmplx)
    if project_path:
        # Open a connection to GPT 3.5
        connectors = api.gpt.OpenAIConnector()
        py_translator = translators.PyTranslator(connectors)
        # Split the python code into classes, functions
        # module_signature, methods_signature, dependencies_signature, module_elements_signature,_ = splitter.parse_python_code(python_code)
        # check if corresponding dependencies are in counterparts.json
        counterparts, unavailables = finder.counterparts_finder(py_signature['dependencies_signature'], files)
        # Remove the dependencies that are modules and classes inside the repo based on output of tree sitter
        # [TODO: Write a dependecy cleaner]
        # Prompt for counterparts of python libraries that are not in counterparts.json and update counterparts.json and install them
        counterparts_prompter = translators.CounterpartsPrompter(connectors)
        if unavailables:
            # counterparts_prompter = translators.CounterpartsPrompter(connectors)
            installed_counterparts, unavailable_counterpart = counterparts_prompter.dependencies_prompter_and_installer(counterparts, unavailables)
        elif counterparts:
            # Check if all needed counterparts are installed
            error = counterparts_prompter.install_dependencies(counterparts)
            if not error:
                installed_counterparts = counterparts
                unavailable_counterpart = None
        else:
            installed_counterparts = None
            unavailable_counterpart = None
        # Translate dependencies to JavaScript
        # if dependencies_signature:
        #     dependencies = py_translator.dependencies_translator_and_installer(dependencies_signature)
        # Combine the signatures based on need
        # sorted_signatures = combiner.sort_by_start_line([py_signature[1], py_signature[2], py_signature[3], py_signature[4]])
        # Translate noncomplex code to JavaScript
        if not cmplx:
            module = None
            non_module = py_translator.py_translator_checker(project_path, py_signature, installed_counterparts, cmplx=cmplx, unavailable_counterparts=unavailable_counterpart)
            if non_module:
                # Create a unit test code for the python module by GPT 3.5
                py_unittest_prompter = translators.PyUnittestPrompter(connectors)
                py_unittest = py_unittest_prompter.py_unittest_checker(project_path, py_signature, module=module, cmplx=cmplx)
                if py_unittest:
                    # Translate the generated unit test code to javascript by GPT 3.5
                    py_unittest_translator = translators.PyUnittestTranslator(connectors)
                    py_unittest_translator.py_translator_checker(project_path, py_signature, py_unittest, non_module, module=module)
        else:
            # Translate module signature to JavaScript
            module = py_translator.py_translator_checker(project_path, py_signature, installed_counterparts, unavailable_counterparts=unavailable_counterpart)
            # [TODO: check if the module is translated correctly]
            # module = not None
        if module:
            for _, signature in enumerate(py_signature['methods_signature']):
                # Create a unit test code for the python function by GPT 3.5
                py_unittest_prompter = translators.PyUnittestPrompter(connectors)
                py_unittest = py_unittest_prompter.py_unittest_checker(project_path, signature, py_signature['module_signature'], module)
                if py_unittest:
                    # Translate the python method to javascript by GPT 3.5
                    py_translator = translators.PyTranslator(connectors)
                    translated_func = py_translator.py_translator_checker(project_path, signature, installed_counterparts, func_trans=True, unavailable_counterparts=unavailable_counterpart)
                    if translated_func:
                        # Translate the generated unit test code to javascript by GPT 3.5
                        py_unittest_translator = translators.PyUnittestTranslator(connectors)
                        py_unittest_translator.py_translator_checker(project_path, signature, py_unittest, translated_func, module=module)

        if module and py_unittest_translator:
            # read the code from the files
            base_code = code_operator.read(js_path)
            elements_code = code_operator.read(function_path)
            # Combine the generated code to one file
            combiner.combine(js_path, base_code, elements_code)

if __name__ == "__main__":

    # Initialize the classes
    code_operators = CodeOperator()
    finders = Finder()
    splitters = Splitter()
    combiners = Combiner()
    project_operators = ProjectOperator()
    analyzer = Analyzer()
    cmplx = False

    # # Create a generator object for .py files
    # py_file_generator = project_operators.traverse_project(DATA_POOL)

    py_signatures, project_files = splitters.split(DATA_POOL)
    # Iterate through the generator
    for _, py_signature in enumerate(py_signatures):
        # analyze the python module
        for item in py_signature['sorted_signature']:
            if 'class' in item:
                cmplx = True
        if len(py_signature['methods_signature']) > 1 or cmplx:
        # loc = analyzer.analyze(py_signature['file_path'])
        # if loc < 200:
            # Run for complex modules which need splitting and combining
            run(code_operators, finders, splitters, combiners, project_operators, py_signature, project_files)

        else:
            # Run for small modules which don't need splitting and combining
            run(code_operators, finders, splitters, combiners, project_operators, py_signature, project_files, cmplx=False)