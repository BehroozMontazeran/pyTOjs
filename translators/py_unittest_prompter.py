""" Code prompter for unittest from GPT 3.5 with ability of runnning and checking for errors

    Returns:
        None | python unittest
"""
import subprocess
import time
import re

from core.log import Log
from core.code_extractor import CodeExtractor
from core.operator import CodeOperator, Finder
from config import MAX_LOOP, START_LOOP, MESSAGES


class PyUnittestPrompter:
    """Prompt for python unittest, run and test it until success or reaching the maximum loop."""  
    def __init__(self, connector) -> None:
        self.log = Log(self.__class__.__name__)
        self.code_extractor = CodeExtractor()
        self.code_op = CodeOperator()
        self.code_finder = Finder()
        self.connector = connector
        self.start_overall_time = time.time()
        self.class_name = None
        self.module_name = None

    def timing(self, start_time):
        """Print the time taken to run the code"""
        end_time = time.time()
        self.log.info(f"Overal time taken to run the code: {end_time - start_time}")


    def py_unittest_checker(self, path, signature, module_signature) -> None | str:
        """Call translator on signature of python file, run unittest for it and save the corrected code 
        """
        try:

            # Find the corresponding class_name
            self.class_name = self.code_finder.py_class_name(signature, module_signature)

            # Extract module name
            self.module_name = self.code_finder.module_name(path)

            # First prompt on unit test
            py_unittest = self.py_unittest_prompter(signature)

            if py_unittest:
                loop_counter = START_LOOP
                while True:
                    # Check if there are errors in the generated unit tests
                    _ , error = self.run_python_unittest(path, py_unittest)
                    start_time = time.time()
                    if 'FAILED' in error:
                        
                        self.log.info(f"Found errors in the generated unit tests. Prompting for corrections. Number of tries: {loop_counter+1}")
                        # Provide the code and error to GPT to make corrections
                        raw_string = MESSAGES['msg_py_ast_error'][1]['content']
                        data = {'py_code': str(py_unittest), 'error': str(error)}
                        MESSAGES['msg_py_ast_error'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_py_ast_error'][1]['content'])
                        correction = self.connector.get_completions(MESSAGES['msg_py_ast_error'])
                        self.code_extractor.set_text(correction.choices[0].message.content)
                        # extract the corrected code
                        py_unittest = self.code_extractor.extract_code()
                        MESSAGES['msg_py_ast_error'][1]['content'] = raw_string
                        end_time = time.time()
                        self.log.info(f"Time taken to provide a python unittest by GPT 3.5 in try: {loop_counter+1} Time elapsed: {end_time - start_time}")
                    else:
                        self.code_op.save(f'{path}/py_unittest/test_{signature["name"]}.py', py_unittest, 'w')
                        end_time = time.time()
                        self.log.info(f"Time taken to provide a python unittest by GPT 3.5 in try: {loop_counter+1} Time elapsed: {end_time - start_time}")
                        break  # Exit the loop if no errors in unit tests
                    # Loop checker, break at maximimum number of loop
                    if loop_counter < MAX_LOOP:
                        loop_counter += 1
                    else:
                        self.log.error("Unable to provide a correct python unittest by GPT 3.5!")
                        break  # Exit the loop if no correct unit test provided


            else:
                self.log.error("Unable to provide a python unittest by GPT 3.5!")
                self.timing(self.start_overall_time)
                return None

        except FileNotFoundError:
            self.log.error("Unable to read the python code!")
            return None
        return py_unittest

    def py_unittest_prompter(self, signature):
        """Prompt unittest for python code"""
        self.log.info("***Prompting for the python unittest by GPT 3.5!")
        start_time = time.time()
        raw_string = MESSAGES['msg_py_unittest'][1]['content']
        data = {'function_name': signature["name"], 'class_name': self.class_name, 'module_name': self.module_name, 'ast': str(signature)}
        MESSAGES['msg_py_unittest'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_py_unittest'][1]['content'])
        completion = self.connector.get_completions(MESSAGES['msg_py_unittest'])
        self.code_extractor.set_text(completion.choices[0].message.content)
        end_time = time.time()
        MESSAGES['msg_py_unittest'][1]['content'] = raw_string
        self.log.info(f"First Prompt for the python unittest by GPT 3.5! Time elapsed: {end_time - start_time}")
        return self.code_extractor.extract_code()

    def run_python_unittest(self, path, unittest_code):
        """Run unittest on python code"""
        start_time = time.time()
        self.log.info("***Running python unittest by subprocess!")
        # Save the Python unittest in a temporary file
        with open(f'{path}/temp_py_unittest_before_run.py', 'w', encoding='utf-8') as file:
            file.write(unittest_code)

        # Run the unittest using subprocess
        process = subprocess.Popen(['python', f'{path}/temp_py_unittest_before_run.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()
        end_time = time.time()
        self.log.info(f"Run python unittest by subprocess! Time elapsed: {end_time - start_time}")

        return output, error
