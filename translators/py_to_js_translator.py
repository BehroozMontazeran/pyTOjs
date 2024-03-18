""" Code translator for unittest from GPT 3.5 with ability of runnning and checking for errors

    Returns:
        None | js code
"""
import subprocess
import re
from core.log import Log
from core.code_extractor import CodeExtractor
from core.operator import CodeOperator, Finder
from core.eval import EVAL
from utils.utils import Utils
from config import MAX_LOOP, START_LOOP, MESSAGES, EVAL_LIST

class PyTranslator:
    """Prompt for translation of python code to javascript code"""
    def __init__(self, connector) -> None:
        self.log = Log(self.__class__.__name__)
        self.code_extractor = CodeExtractor()
        self.code_op = CodeOperator()
        self.code_finder = Finder()
        self.eval = EVAL()
        self.utils = Utils()
        self.connector = connector
        self.start_overall_time = self.utils.get_timestamp()
        self.data = None
        self.unavailable_counterparts = []


    def py_translator_checker(self, path, py_signature, counterparts=None, func_trans=False, cmplx=True, unavailable_counterparts=None) -> None | str:
        """read the python file, call translator on it, and save the corrected code """

        try:
            self.unavailable_counterparts = unavailable_counterparts
            # First prompt on translator
            if func_trans:# Target: Translating a function
                module_signature = py_signature
                js_code = self.translate_function(module_signature, counterparts)
            else:# if the signature is from the whole module
                dependencies_signature = py_signature['dependencies_signature']
                sorted_signature = py_signature['sorted_signature']
                module_signature = py_signature['module_signature'] if len(py_signature['module_signature']) !=0 else self.code_op.read(py_signature['file_path'])
                js_code = self.translate_module(module_signature, dependencies_signature, sorted_signature, counterparts, cmplx)

            if js_code:
                loop_counter = START_LOOP
                while True:
                    # Check if there are errors in the generated js code
                    _ , error = self.run_javascript_code(path, js_code)

                    if error:
                        start_time = self.utils.get_timestamp()
                        self.log.info(f"Found errors in the generated js code. Prompting for corrections. Number of tries: {loop_counter+1}")
                        # Provide the code and error to GPT to make corrections
                        raw_string = MESSAGES['msg_ast_error'][1]['content']
                        data = {'py_code':self.data, 'js_code': js_code, 'error': error}
                        MESSAGES['msg_ast_error'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_ast_error'][1]['content'])
                        correction = self.connector.get_completions(MESSAGES['msg_ast_error'])
                        self.code_extractor.set_text(correction.choices[0].message.content)
                        MESSAGES['msg_ast_error'][1]['content'] = raw_string
                        # extract the corrected code
                        js_code = self.code_extractor.extract_code()
                        self.utils.timing(start_time, self.utils.get_timestamp(), f"JavaScript translation by GPT in try: {loop_counter+1}", "info")
                    else:
                        self.utils.timing(self.start_overall_time, self.utils.get_timestamp(), f"Successfully tested JavaScript translation in try: {loop_counter+1}", "info")
                        break  # Exit the loop if no errors in unit tests
                    # Loop checker, break at maximimum number of loop
                    if loop_counter < MAX_LOOP:
                        loop_counter += 1
                    else:
                        self.utils.timing(self.start_overall_time, self.utils.get_timestamp(), f"Unable to provide a correct JavaScript translation by GPT in try: {loop_counter+1}", "error")
                        return None
                        # break  # Exit the loop if no correct unit test found

            else:
                self.utils.timing(self.start_overall_time, self.utils.get_timestamp(), "Unable to provide a correct JavaScript translation by GPT!", "error")
                return None


            # Save the corrected code
            if func_trans and js_code :
                self.code_op.save(f'{path}/functions_code.js', js_code + "\n\n", 'a')
                return js_code
            else:
                self.code_op.save(f'{path}/{self.code_finder.module_name(path)}.js', js_code, 'w')
                return js_code
            
        except Exception as e:
            self.log.error(f"Unable to feed into GPT: {module_signature}.  \n{e}")


    def translate_function(self, python_code, counterparts):
        """Translate Python ast of a function to JavaScript"""
        start_time = self.utils.get_timestamp()
        raw_string = MESSAGES['msg_ast_mth'][1]['content']
        self.data = {'function_code': python_code, 'counterparts': counterparts}
        MESSAGES['msg_ast_mth'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(self.data.get(x.group(1))), MESSAGES['msg_ast_mth'][1]['content'])
        completion = self.connector.get_completions(MESSAGES['msg_ast_mth'])
        self.code_extractor.set_text(completion.choices[0].message.content)
        MESSAGES['msg_ast_mth'][1]['content'] = raw_string
        self.utils.timing(start_time, self.utils.get_timestamp(), "Translation of Python to JavaScript completed!", "info")
        return self.code_extractor.extract_code()


    def translate_module(self, module_signature, dependencies_signature, sorted_signature, counterparts, cmplx):
        """Translate Python signature of whole module to JavaScript"""
        self.log.info("***Translating Python module to JavaScript!")
        start_time = self.utils.get_timestamp()

        if cmplx:
            num_class = sum(1 for item in sorted_signature if item[0] == 'class')
            num_method = sum(1 for item in sorted_signature if item[0] == 'method')
            num_function = sum(1 for item in sorted_signature if item[0] == 'function')
            num_dependency = sum(1 for item in sorted_signature if item[0] == 'dependency')
            self.data = {'number_of_dependencies': num_dependency,'number_of_classes': num_class, 'number_of_methods': num_method, 'number_of_functions': num_function, 'python_module': module_signature, 'depencencies': dependencies_signature,'counterparts': counterparts}
            raw_string = MESSAGES['msg_ast_ml'][1]['content']
            MESSAGES['msg_ast_ml'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(self.data.get(x.group(1))), MESSAGES['msg_ast_ml'][1]['content'])
            completion = self.connector.get_completions(MESSAGES['msg_ast_ml'])
            self.code_extractor.set_text(completion.choices[0].message.content)
            MESSAGES['msg_ast_ml'][1]['content'] = raw_string
        else:
            data = {'python_module': module_signature, 'dependencies':dependencies_signature , 'counterparts': counterparts}
            raw_string = MESSAGES['msg_ast_fn'][1]['content']
            MESSAGES['msg_ast_fn'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_ast_fn'][1]['content'])
            completion = self.connector.get_completions(MESSAGES['msg_ast_fn'])
            self.code_extractor.set_text(completion.choices[0].message.content)
            MESSAGES['msg_ast_fn'][1]['content'] = raw_string

        self.utils.timing(start_time, self.utils.get_timestamp(), "Translation of Python to JavaScript completed!", "info")
        return self.code_extractor.extract_code()
    

    def run_javascript_code(self, path, js_code):
        """Run JavaScript code using Node.js"""
        start_time = self.utils.get_timestamp()

        self.code_op.save(f'{path}/temp_js.js', js_code, 'w')

        if self.unavailable_counterparts:
            # Run the JavaScript code using Node.js subprocess for only Syntax Error
            self.log.warning(f"No Counterparts for {self.unavailable_counterparts} in JavaScript, the code can only be tested for potential Syntax Error!")
            process = subprocess.Popen(['node', '--check' ,f'{path}/temp_js.js'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output, error = process.communicate()
            self.eval.eval(EVAL_LIST,error, js_code, self.utils.get_formatted_time(self.utils.get_timestamp()))
        else:
            self.log.warning("Running code for potential Syntax and Runtime Errors!")
            # Run the JavaScript code using Node.js subprocess
            process = subprocess.Popen(['node' ,f'{path}/temp_js.js'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output, error = process.communicate()
            self.eval.eval(EVAL_LIST, error, js_code, self.utils.get_formatted_time(self.utils.get_timestamp()))

        self.utils.timing(start_time, self.utils.get_timestamp(), "Run JavaScript code by subprocess!", "info")

        return output, error
