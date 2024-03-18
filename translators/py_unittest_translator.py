""" Code Translator from python to javascript using GPT 3.5 from a python file

    Returns:
        Translated javascript codes
"""
import subprocess
import re
from core.log import Log
from core.code_extractor import CodeExtractor
from core.operator import CodeOperator
from core.eval import EVAL
from utils.utils import Utils
from config import MAX_LOOP, START_LOOP, MESSAGES, EVAL_LIST


class PyUnittestTranslator:
    """Translate a unit test code from python to Javascript"""  
    def __init__(self, connector) -> None:
        self.log = Log(self.__class__.__name__)
        self.code_extractor = CodeExtractor()
        self.code_op = CodeOperator()
        self.eval = EVAL()
        self.utils = Utils()
        self.connector = connector
        self.start_overall_time = self.utils.get_timestamp()


    def py_translator_checker(self, path, py_signature, py_unittest, js_code, module=None) -> None | str:
        """read the unittest python file, call translator on it, run unittest on it and save the corrected code 
        """
        signature = py_signature
        if not module:
            function_name = 'module'
        else:
            function_name = signature["name"]
        try:
            # First prompt on unit test
            translated_js_unittest = self.translate_py_to_js(py_unittest)
            
            if translated_js_unittest and js_code:
                loop_counter = START_LOOP
                while True:
                    # Check if there are errors in the generated unit tests
                    error = self.test_translated_code(path, js_code, translated_js_unittest)
                    start_time = self.utils.get_timestamp()
                    if error:
                        self.log.info(f"Found errors in the generated js code. Prompting for corrections. Number of tries: {loop_counter+1}")
                        # Provide the code and error to GPT to make corrections
                        raw_string = MESSAGES['msg_translated_unittest_error'][1]['content']
                        data = {'js_code': str(py_unittest), 'error': str(error), 'py_unittest': str(py_unittest)}
                        MESSAGES['msg_translated_unittest_error'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_translated_unittest_error'][1]['content'])
                        correction = self.connector.get_completions(MESSAGES['msg_translated_unittest_error'])
                        self.code_extractor.set_text(correction.choices[0].message.content)
                        # extract the corrected code
                        js_code = self.code_extractor.extract_code()
                        MESSAGES['msg_translated_unittest_error'][1]['content'] = raw_string

                        self.utils.timing(start_time, self.utils.get_timestamp(), f"JavaScript unittest by GPT in try: {loop_counter+1}", "info")

                    else:
                        # Save the translated unittest code
                        self.code_op.save(f'{path}/js_unittest/test_{function_name}.js', translated_js_unittest, 'w')
                        self.utils.timing(start_time, self.utils.get_timestamp(), f"JavaScript unittest by GPT in try: {loop_counter+1}", "info")
                        break  # Exit the loop if no errors in unit tests
                    # Loop checker, break at maximimum number of loop
                    if loop_counter < MAX_LOOP:
                        loop_counter += 1
                    else:
                        self.utils.timing(self.start_overall_time, self.utils.get_timestamp(), f"Unable to provide a correct JavaScript unittest by GPT in try: {loop_counter+1}", "error")
                        break  # Exit the loop if no correct unit test found

            else:
                self.utils.timing(self.start_overall_time, self.utils.get_timestamp(), "Unable to provide a correct JavaScript unittest by GPT!", "error")
                return None
            
        except FileNotFoundError:
            self.log.error("Unable to read the unittest file!")

        return translated_js_unittest

    def translate_py_to_js(self, python_code):
        """Translate python code to javascript one"""
        start_time = self.utils.get_timestamp()

        raw_string = MESSAGES['msg_translate_unittest'][1]['content']
        data = {'function_code': python_code}
        MESSAGES['msg_translate_unittest'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_translate_unittest'][1]['content'])
        completion = self.connector.get_completions(MESSAGES['msg_translate_unittest'])
        self.code_extractor.set_text(completion.choices[0].message.content)
        MESSAGES['msg_translate_unittest'][1]['content'] = raw_string

        self.utils.timing(start_time, self.utils.get_timestamp(), "Translation of python unittest by GPT!", "info")
        return self.code_extractor.extract_code()

    def test_translated_code(self, path, js_code, js_test_code):
        """Test translated code and unit test to javascript on vscode terminal by subprocess
        """
        start_time = self.utils.get_timestamp()

        self.code_op.save(f"{path}/temp_js.js", js_code, 'w')
        self.code_op.save(f"{path}/temp_unittest.js", js_test_code, 'w')
        # Run the unittest using subprocess
        process = subprocess.Popen(['node', 'temp_unittest.js'], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()
        self.eval.eval(EVAL_LIST, error, js_test_code, self.utils.get_formatted_time(self.utils.get_timestamp()))
        self.utils.timing(start_time, self.utils.get_timestamp(), "Run JavaScript unittest by subprocess!", "info")
        if 'Error' in error or 'Exception' in error:
            return error
