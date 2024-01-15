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
from config import MAX_LOOP, START_LOOP, MESSAGES, PATH

class PyTranslator:
    """Prompt for translation of python code to javascript code"""
    def __init__(self, connector) -> None:
        self.log = Log(self.__class__.__name__)
        self.code_extractor = CodeExtractor()
        self.code_op = CodeOperator()
        self.code_finder = Finder()
        self.connector = connector
        self.start_overall_time = time.time()


    def timing(self, start_time):
        """Print the time taken to run the code"""
        end_time = time.time()
        self.log.info(f"Overal time taken to run the code: {end_time - start_time}")


    def py_translator_checker(self, path, signature, dependencies_signature = None, module_elements_signature = None, func_trans=False) -> None | str:
        """read the python file, call translator on it, and save the corrected code """
        try:
            # First prompt on translator
            if func_trans:# if the signature is a function
                js_code = self.translate_func_to_js(signature)
            else:# if the signature is the whole module
                js_code = self.translate_module_to_js(signature, dependencies_signature, module_elements_signature)

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
                        data = {'js_code': js_code, 'error': error}
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
                        self.log.error("Unable to provide a correct js code by GPT 3.5!")
                        return None
                        # break  # Exit the loop if no correct unit test found

            else:
                self.log.error("Unable to provide a js code by GPT 3.5!")
                self.timing(self.start_overall_time)
                return None


            # Save the corrected code
            if func_trans :
                self.code_op.save(f'{path}/functions_code.js', js_code + "\n\n", 'a')
                self.timing(self.start_overall_time)
                return js_code
            else:
                self.code_op.save(f'{path}/{self.code_finder.module_name(PATH)}.js', js_code, 'w')
                self.timing(self.start_overall_time)
                return js_code
            
        except Exception as e:
            self.log.error(f"Unable to read: {signature}.  \n{e}")


    def translate_func_to_js(self, python_code):
        """Translate Python ast of a function to JavaScript"""
        self.log.info("***Translating Python code to JavaScript!")
        start_time = time.time()

        raw_string = MESSAGES['msg_ast_fn'][1]['content']
        data = {'function_code': python_code}
        MESSAGES['msg_ast_fn'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_ast_fn'][1]['content'])
        completion = self.connector.get_completions(MESSAGES['msg_ast_fn'])
        self.code_extractor.set_text(completion.choices[0].message.content)
        MESSAGES['msg_ast_fn'][1]['content'] = raw_string

        # MESSAGES['msg_ast_fn'][1]['content'] = MESSAGES['msg_ast_fn'][1]['content'].format(str(python_code))
        # completion = self.connector.get_completions(MESSAGES['msg_ast_fn'])
        # self.code_extractor.set_text(completion.choices[0].message.content)
        end_time = time.time()
        self.log.info(f"Translation of Python to JavaScript completed! Time elapsed: {end_time - start_time}")
        return self.code_extractor.extract_code()


    def translate_module_to_js(self, class_signature, dependencies_signature, module_elements_signature):
        """Translate Python signature of whole module to JavaScript"""
        self.log.info("***Translating Python module to JavaScript!")
        start_time = time.time()
        module = list(dependencies_signature) + module_elements_signature + class_signature
        raw_string = MESSAGES['msg_ast_ml'][1]['content']
        data = {'number_of_classes': len(class_signature), 'python_module': module}
        MESSAGES['msg_ast_ml'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_ast_ml'][1]['content'])
        completion = self.connector.get_completions(MESSAGES['msg_ast_ml'])
        self.code_extractor.set_text(completion.choices[0].message.content)
        MESSAGES['msg_ast_ml'][1]['content'] = raw_string

        # MESSAGES['msg_ast_ml'][1]['content'] = MESSAGES['msg_ast_ml'][1]['content'].format(len(python_module), str(python_module))
        # completion = self.connector.get_completions(MESSAGES['msg_ast_ml'])
        # self.code_extractor.set_text(completion.choices[0].message.content)
        end_time = time.time()
        self.log.info(f"Translation of Python to JavaScript completed! Time elapsed: {end_time - start_time}")
        return self.code_extractor.extract_code()


    def run_javascript_code(self, path, js_code):
        """Run JavaScript code using Node.js"""
        self.log.info("***Running JavaScript code by subprocess!")
        start_time = time.time()
        # Save the JavaScript code in a temporary file
        with open(f'{path}/temp_js_before_run.js', 'w', encoding='utf-8') as file:
            file.write(js_code)

        # Run the JavaScript code using Node.js subprocess
        process = subprocess.Popen(['node', f'{path}/temp_js_before_run.js'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()
        end_time = time.time()
        self.log.info(f"Run JavaScript code by subprocess! Time elapsed: {end_time - start_time}")

        return output, error
