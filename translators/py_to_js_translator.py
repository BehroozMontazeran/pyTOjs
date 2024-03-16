""" Code translator for unittest from GPT 3.5 with ability of runnning and checking for errors

    Returns:
        None | js code
"""
import subprocess
import time
import re
from core.log import Log
from core.code_extractor import CodeExtractor
from core.operator import CodeOperator, Finder
from config import MAX_LOOP, START_LOOP, MESSAGES

class PyTranslator:
    """Prompt for translation of python code to javascript code"""
    def __init__(self, connector) -> None:
        self.log = Log(self.__class__.__name__)
        self.code_extractor = CodeExtractor()
        self.code_op = CodeOperator()
        self.code_finder = Finder()
        self.connector = connector
        self.start_overall_time = time.time()
        self.data = None
        self.unavailable_counterparts = []


    def timing(self, start_time):
        """Print the time taken to run the code"""
        end_time = time.time()
        self.log.info(f"Overal time taken to run the code: {end_time - start_time}")


    def py_translator_checker(self, path, py_signature, counterparts=None, func_trans=False, cmplx=True, unavailable_counterparts=None) -> None | str:
        """read the python file, call translator on it, and save the corrected code """

        try:
            self.unavailable_counterparts = unavailable_counterparts
            # First prompt on translator
            if func_trans:# Target: Translating a function
                module_signature = py_signature
                js_code = self.translate_function(module_signature, counterparts)
                # py_code = signature + counterparts
            else:# if the signature is from the whole module
                # if noncomplex:
                dependencies_signature = py_signature['dependencies_signature']
                sorted_signature = py_signature['sorted_signature']
                module_signature = py_signature['module_signature'] if len(py_signature['module_signature']) !=0 else self.code_op.read(py_signature['file_path'])
                js_code = self.translate_module(module_signature, dependencies_signature, sorted_signature, counterparts, cmplx)
                # else:
                #     dependencies_signature = py_signature['dependencies_signature']
                #     # module_elements_signature = py_signature['module_signature']
                #     module_signature = py_signature['module_signature'] if len(py_signature['module_signature']) !=0 else self.code_op.read(py_signature['file_path'])
                #     js_code = self.translate_module(module_signature, dependencies_signature, counterparts, )

            if js_code:
                loop_counter = START_LOOP
                while True:
                    # Check if there are errors in the generated js code
                    _ , error = self.run_javascript_code(path, js_code)

                    if error:
                        start_time = time.time()
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
                        end_time = time.time()
                        self.log.info(f"Time taken to provide a translated javascript code by GPT 3.5 in try: {loop_counter+1} Time elapsed: {end_time - start_time}")
                    else:
                        self.log.info("Successfully tested the js code provided by GPT 3.5!")
                        break  # Exit the loop if no errors in unit tests
                    # Loop checker, break at maximimum number of loop
                    if loop_counter < MAX_LOOP:
                        loop_counter += 1
                    else:
                        self.log.error(f"Unable to provide a correct js code by GPT 3.5 after {MAX_LOOP} tries!")
                        return None
                        # break  # Exit the loop if no correct unit test found

            else:
                self.log.error("Unable to provide a js code by GPT 3.5 at early stage!")
                self.timing(self.start_overall_time)
                return None


            # Save the corrected code
            if func_trans and js_code : #[TODO: change the function based on flag, not to create unsed folders]
                self.code_op.save(f'{path}/functions_code.js', js_code + "\n\n", 'a')
                self.timing(self.start_overall_time)
                return js_code
            else:
                self.code_op.save(f'{path}/{self.code_finder.module_name(path)}.js', js_code, 'w')
                self.timing(self.start_overall_time)
                return js_code
            
        except Exception as e:
            self.log.error(f"Unable to feed signature into GPT 3.5: {module_signature}.  \n{e}")


    def translate_function(self, python_code, counterparts):
        """Translate Python ast of a function to JavaScript"""
        self.log.info("***Translating Python code to JavaScript!")
        start_time = time.time()

        raw_string = MESSAGES['msg_ast_mth'][1]['content']
        self.data = {'function_code': python_code, 'counterparts': counterparts}
        MESSAGES['msg_ast_mth'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(self.data.get(x.group(1))), MESSAGES['msg_ast_mth'][1]['content'])
        completion = self.connector.get_completions(MESSAGES['msg_ast_mth'])
        self.code_extractor.set_text(completion.choices[0].message.content)
        MESSAGES['msg_ast_mth'][1]['content'] = raw_string

        end_time = time.time()
        self.log.info(f"Translation of Python to JavaScript completed! Time elapsed: {end_time - start_time}")
        return self.code_extractor.extract_code()


    def translate_module(self, module_signature, dependencies_signature, sorted_signature, counterparts, cmplx):
        """Translate Python signature of whole module to JavaScript"""
        self.log.info("***Translating Python module to JavaScript!")
        start_time = time.time()

        if cmplx:
            # module = module_signature

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
            # module = module_signature
            data = {'python_module': module_signature, 'dependencies':dependencies_signature , 'counterparts': counterparts}
            raw_string = MESSAGES['msg_ast_fn'][1]['content']
            MESSAGES['msg_ast_fn'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_ast_fn'][1]['content'])
            completion = self.connector.get_completions(MESSAGES['msg_ast_fn'])
            self.code_extractor.set_text(completion.choices[0].message.content)
            MESSAGES['msg_ast_fn'][1]['content'] = raw_string

        end_time = time.time()
        self.log.info(f"Translation of Python to JavaScript completed! Time elapsed: {end_time - start_time}")
        return self.code_extractor.extract_code()
    

    def run_javascript_code(self, path, js_code):
        """Run JavaScript code using Node.js"""
        self.log.info("***Running JavaScript code by subprocess!")
        # start_time = time.time()
        # Save the JavaScript code in a temporary file
        # with open(f'{path}/temp_js_before_run.js', 'w', encoding='utf-8') as file:
        #     file.write(js_code)

        self.code_op.save(f'{path}/temp_js_before_run.js', js_code, 'w')

        if self.unavailable_counterparts:
            # Run the JavaScript code using Node.js subprocess
            self.log.warning(f"No Counterparts for {self.unavailable_counterparts} in JavaScript, the code can only be tested for potential Syntax Error!")
            process = subprocess.Popen(['node', '--check' ,f'{path}/temp_js_before_run.js'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output, error = process.communicate()
        else:
            self.log.warning("Running code for potential Syntax and Runtime Errors!")
            # Run the JavaScript code using Node.js subprocess
            process = subprocess.Popen(['node' ,f'{path}/temp_js_before_run.js'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) #, '--check'
            output, error = process.communicate()
            end_time = time.time()
        # self.log.info(f"Run JavaScript code by subprocess! Time elapsed: {end_time - start_time}")

        return output, error
