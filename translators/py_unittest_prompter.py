""" Code prompter for unittest from GPT with the ability of runnning and checking for errors

    Returns:
        None | python unittest
"""
import subprocess
import re

from core.log import Log
from core.eval import EVAL
from core.code_extractor import CodeExtractor
from core.operator import CodeOperator, Finder, ProjectOperator
from utils.utils import Utils
from config import MAX_LOOP, SOURCE_ROOT, START_LOOP, MESSAGES, EVAL_LIST


class PyUnittestPrompter:
    """Prompt for python unittest, run and test it until success or reaching the maximum loop."""  
    def __init__(self, connector) -> None:
        self.log = Log(self.__class__.__name__)
        self.code_extractor = CodeExtractor()
        self.code_op = CodeOperator()
        self.code_finder = Finder()
        self.pr_op = ProjectOperator()
        self.eval = EVAL()
        self.utils = Utils()
        self.connector = connector
        self.start_overall_time = self.utils.get_timestamp()
        self.class_name = None
        self.module_name = None
        self.function_name = None
        self.fn_dependencies = None


    def py_unittest_checker(self, path, fn_signature, signatures, module=None, cmplx=True) -> None | str:
        """Call translator on signature of python file, run unittest for it and save the corrected code 
        """
            
        try:
            # First prompt on unit test for single function or module without function
            if not cmplx:
                self.function_name = [item['name'] for (_, item) in enumerate(signatures['module_signature']) if item['type'] == 'function'][0]
                self.module_name = self.code_finder.module_name(path)
                fn_signature = self.code_op.read(fn_signature['file_path'])
                py_unittest = self.py_unittest_prompter(fn_signature, signatures)
            # First prompt on unit test for a function from a module with multiple functions or classes
            elif module:
                # Find the corresponding class_name
                self.class_name = self.code_finder.py_class_name(fn_signature, signatures)
                # Extract module name
                self.module_name = self.code_finder.module_name(path)
                self.function_name = fn_signature["name"]
                # Find the dependent functions inside the given function
                py_unittest = self.py_unittest_prompter(fn_signature, signatures)


            if py_unittest:
                loop_counter = START_LOOP
                while True:
                    # Check if there are errors in the generated unit tests
                    _ , error = self.run_python_unittest(path, py_unittest)
                    start_time = self.utils.get_timestamp()
                    if 'FAILED' in error or 'SyntaxError' in error: #NameError
                        
                        self.log.info(f"Found errors in the generated unit tests. Prompting for corrections. Number of tries: {loop_counter+1}")
                        # Provide the code and error to GPT to make corrections
                        raw_string = MESSAGES['msg_py_unittest_error'][1]['content']
                        data = {'unittest': str(py_unittest), 'error': str(error), 'py_code': str(fn_signature), 'module_signature': str(signatures['module_signature'])}
                        MESSAGES['msg_py_unittest_error'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_py_unittest_error'][1]['content'])
                        correction = self.connector.get_completions(MESSAGES['msg_py_unittest_error'])
                        self.code_extractor.set_text(correction.choices[0].message.content)
                        # extract the corrected code
                        py_unittest = self.code_extractor.extract_code()
                        MESSAGES['msg_py_unittest_error'][1]['content'] = raw_string

                        self.utils.timing(start_time, self.utils.get_timestamp(), f"Python unittest by GPT in try: {loop_counter+1}", "info")
                    else:
                        self.code_op.save(f'{path}/py_unittest/test_{self.function_name}.py', py_unittest, 'w')
                        self.utils.timing(start_time, self.utils.get_timestamp(), f"Python unittest by GPT in try: {loop_counter+1}", "info")
                        break  # Exit the loop if no errors in unit tests
                    # Loop checker, break at maximimum number of loop
                    if loop_counter < MAX_LOOP:
                        loop_counter += 1
                    else:
                        self.utils.timing(self.start_overall_time, self.utils.get_timestamp(), f"Unable to provide a correct python unittest by GPT in try: {loop_counter+1}", "error")
                        break  # Exit the loop if no correct unit test provided


            else:
                self.utils.timing(self.start_overall_time, self.utils.get_timestamp(), "Unable to provide a correct python unittest by GPT!", "error")
                return None

        except FileNotFoundError:
            self.log.error("Unable to read the python code!")
            return None
        return py_unittest

    def py_unittest_prompter(self, signature, signatures):
        """Prompt unittest for python code"""
        start_time = self.utils.get_timestamp()
        if self.class_name:
            raw_string = MESSAGES['msg_fn_from_cl_unittest'][1]['content']
            data = {'function_name': self.function_name, 'class_name': self.class_name, 'module_name': self.module_name, 'ast': str(signature), 'module_signature': str(signatures['module_signature'])}
            MESSAGES['msg_fn_from_cl_unittest'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_fn_from_cl_unittest'][1]['content'])
            completion = self.connector.get_completions(MESSAGES['msg_fn_from_cl_unittest'])
            self.code_extractor.set_text(completion.choices[0].message.content)
            MESSAGES['msg_fn_from_cl_unittest'][1]['content'] = raw_string
        else:
            raw_string = MESSAGES['msg_py_unittest'][1]['content']
            data = {'code': str(signature), 'module_signature': str(signatures['module_signature'])}
            MESSAGES['msg_py_unittest'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_py_unittest'][1]['content'])
            completion = self.connector.get_completions(MESSAGES['msg_py_unittest'])
            self.code_extractor.set_text(completion.choices[0].message.content)
            MESSAGES['msg_py_unittest'][1]['content'] = raw_string
        self.utils.timing(start_time, self.utils.get_timestamp(), "Python unittest by GPT!", "info")
        return self.code_extractor.extract_code()



    def run_python_unittest(self, path, unittest_code):
        """Run unittest on python code"""
        start_time = self.utils.get_timestamp()
        self.code_op.save(f"{SOURCE_ROOT['source']}/temp_py_unittest.py", unittest_code, 'w')

        # Run the unittest using subprocess
        process = subprocess.Popen(['python', '-Xfrozen_modules=off', '-m', 'temp_py_unittest'], cwd=SOURCE_ROOT['source'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()
        self.eval.eval(EVAL_LIST, error, unittest_code, self.utils.get_formatted_time(self.utils.get_timestamp()))
        self.utils.timing(start_time, self.utils.get_timestamp(), "Run python unittest by subprocess!", "info")

        return output, error

