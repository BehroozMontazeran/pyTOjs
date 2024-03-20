""" The main file of the project. """
import api
import translators


from config import RESOURCE,EVAL_LIST, TEMP_JSON
from core.eval import EVAL
from core.operator import CodeOperator, ProjectOperator, Finder
from splitter.splitter import Splitter
from combiner.combiner import Combiner



def run(code_operator, finder, combiner, project_operator, py_signatures, files, cmplx=True):
    """Run the program on each module separately."""

    project_path, js_path, function_path = project_operator.project_creator(py_signatures['file_path'], cmplx)
    if project_path:
        # Open a connection to GPT 3.5
        connectors = api.gpt.OpenAIConnector()
        py_translator = translators.PyTranslator(connectors)
        # check if corresponding dependencies are in counterparts.json
        counterparts, unavailables = finder.counterparts_finder(py_signatures['dependencies_signature'], files)
        # Prompt for counterparts of python libraries that are not in counterparts.json, update counterparts.json and install them as well
        counterparts_prompter = translators.CounterpartsPrompter(connectors)
        if unavailables:
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
        # Translate simple code to JavaScript
        if not cmplx:
            module = None
            non_module = py_translator.py_translator_checker(project_path, py_signatures, installed_counterparts, cmplx=cmplx, unavailable_counterparts=unavailable_counterpart)
            if non_module:
                # Create a unit test
                py_unittest_prompter = translators.PyUnittestPrompter(connectors)
                py_unittest = py_unittest_prompter.py_unittest_checker(project_path, py_signatures, py_signatures, module=module, cmplx=cmplx)
                if py_unittest:
                    # Translate the generated unit test code to javascript
                    py_unittest_translator = translators.PyUnittestTranslator(connectors)
                    py_unittest_translator.py_translator_checker(project_path, py_signatures, py_unittest, non_module, module=module)
        else:
            # Translate module signature to JavaScript for complex codes
            module = py_translator.py_translator_checker(project_path, py_signatures, installed_counterparts, unavailable_counterparts=unavailable_counterpart)
        if module:
            for _, fn_signature in enumerate(py_signatures['methods_signature']):
                # Create a unit test for each method
                py_unittest_prompter = translators.PyUnittestPrompter(connectors)
                py_unittest = py_unittest_prompter.py_unittest_checker(project_path, fn_signature, py_signatures, module)
                if py_unittest:
                    # Translate the python method to javascript
                    py_translator = translators.PyTranslator(connectors)
                    translated_func = py_translator.py_translator_checker(project_path, fn_signature, installed_counterparts, func_trans=True, unavailable_counterparts=unavailable_counterpart)
                    if translated_func:
                        # Translate the generated unit test code to javascript
                        py_unittest_translator = translators.PyUnittestTranslator(connectors)
                        py_unittest_translator.py_translator_checker(project_path, fn_signature, py_unittest, translated_func, module=module)
                    else:
                        py_unittest_translator = None
        code_operator.save(TEMP_JSON, EVAL_LIST, 'j')
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
    evaluate = EVAL()
    CMPLX = False

    # Split the given project into python signatures and its files
    py_sigs, project_files = splitters.split(RESOURCE)

    for _, py_sig in enumerate(py_sigs):
        # analyze the python module
        for item in py_sig['sorted_signature']:
            if 'class' in item:
                CMPLX = True
        if len(py_sig['methods_signature']) > 1 or CMPLX:
            # Complex modules which need splitting and combining
            run(code_operators, finders, combiners, project_operators, py_sig, project_files)

        else:
            # Simple modules which don't need splitting and combining
            run(code_operators, finders, combiners, project_operators, py_sig, project_files, cmplx=False)
    # Evaluate the results
    evaluate.count_errors()
    evaluate.plot_errors()