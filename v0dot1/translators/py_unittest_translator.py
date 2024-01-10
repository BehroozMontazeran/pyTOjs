""" Code Translator from python to javascript using GPT 3.5 from a python file

    Returns:
        Translated javascript codes
"""
import subprocess
import time
import re
from core.log import Log
from core.code_extractor import CodeExtractor
from core.operator import CodeOperator
from config import MAX_LOOP, START_LOOP, MESSAGES


class PyUnittestTranslator:
    """Translate a unit test code from python to Javascript"""  
    def __init__(self, connector) -> None:
        self.log = Log(self.__class__.__name__)
        self.code_extractor = CodeExtractor()
        self.code_op = CodeOperator()
        self.connector = connector
        self.start_overall_time = time.time()
        
    def timing(self, start_time):
        """Print the time taken to run the code"""
        end_time = time.time()
        self.log.info(f"Overal time taken to run the code: {end_time - start_time}")

    def py_translator_checker(self, path, signature, py_unittest, js_code):
        """read the unittest python file, call translator on it, run unittest on it and save the corrected code 
        """
        try:
            # First prompt on unit test
            translated_js_unittest = self.translate_py_to_js(py_unittest)
            
            if translated_js_unittest and js_code:
                loop_counter = START_LOOP
                while True:
                    # Check if there are errors in the generated unit tests
                    error = self.test_translated_code(path, js_code, translated_js_unittest)
                    start_time = time.time()
                    if error:
                        self.log.info(f"Found errors in the generated js code. Prompting for corrections. Number of tries: {loop_counter+1}")
                        # Provide the code and error to GPT to make corrections
                        raw_string = MESSAGES['msg_translated_unittest_error'][1]['content']
                        data = {'js_code': str(py_unittest), 'error': str(error)}
                        MESSAGES['msg_translated_unittest_error'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_translated_unittest_error'][1]['content'])
                        correction = self.connector.get_completions(MESSAGES['msg_translated_unittest_error'])
                        self.code_extractor.set_text(correction.choices[0].message.content)
                        # extract the corrected code
                        js_code = self.code_extractor.extract_js_code()
                        MESSAGES['msg_translated_unittest_error'][1]['content'] = raw_string
                        end_time = time.time()
                        self.log.info(f"Time taken to provide a translated js unit test code by GPT 3.5 in try: {loop_counter+1} Time elapsed: {end_time - start_time}")

                    else:
                        # Save the translated unittest code
                        self.code_op.save(f'{path}/js_unittest/test_{signature["name"]}.js', translated_js_unittest, 'w')
                        end_time = time.time()
                        self.log.info(f"Time taken to provide a python unittest by GPT 3.5 in try: {loop_counter+1} Time elapsed: {end_time - start_time}")
                        break  # Exit the loop if no errors in unit tests
                    # Loop checker, break at maximimum number of loop
                    if loop_counter < MAX_LOOP:
                        loop_counter += 1
                    else:
                        self.log.error("Unable to provide a correct js unittest by GPT 3.5!")
                        break  # Exit the loop if no correct unit test found

            else:
                self.log.error("Unable to provide a js code by GPT 3.5!")
                self.timing(self.start_overall_time)
                return None
            
        except FileNotFoundError:
            self.log.error("Unable to read the unittest file!")

        return translated_js_unittest

    def translate_py_to_js(self, python_code):
        """Translate python code to javascript one"""
        self.log.info("***Prompting for translation of python unittest to js unittest by GPT 3.5!")
        start_time = time.time()
        MESSAGES['msg_translate_unittest'][1]['content'] = MESSAGES['msg_translate_unittest'][1]['content'].format(str(python_code))
        completion = self.connector.get_completions(MESSAGES['msg_translate_unittest'])
        self.code_extractor.set_text(completion.choices[0].message.content)
        end_time = time.time()
        self.log.info(f"First Prompt fo translation of Python unit test to JavaScript unit test completed! Time elapsed: {end_time - start_time}")
        return self.code_extractor.extract_js_code()

    def test_translated_code(self, path, js_code, js_test_code):
        """Test translated code and unit test to javascript on vscode

        Args:
            js_code (.js): translated code
            js_test_code (.js): translated unit test

        Returns:
            _type_: srting of error if any
        """
        start_time = time.time()
        self.log.info("***Running JavaScript unittest and main JavaScript by subprocess!")
        
        # Write translated JS code to a temporary file
        js_code_file = f'{path}/temp_js_before_run.js'
        with open(js_code_file, 'w', encoding='utf-8') as file:
            file.write(js_code)

        # Write translated JS unit test code to a temporary file
        js_test_file = f'{path}/temp_unittest_js_before_run.js'
        with open(js_test_file, 'w', encoding='utf-8') as file:
            file.write(js_test_code)

        # Command to run in VS Code terminal
        command = f'code -r {js_code_file} {js_test_file}'

        try:
            # Run the command
            process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Check for errors in the output
            if 'Error' in process.stderr or 'Exception' in process.stderr:
                end_time = time.time()
                self.log.info(f"Run python unittest by subprocess! Time elapsed: {end_time - start_time}")
                return process.stderr.strip()
            else:
                return None  # No errors
        except Exception as e:
            return f"Error during code execution: {str(e)}"
