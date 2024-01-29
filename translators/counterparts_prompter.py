""" Counterparts Prompter to prompt for collecting and updating python libraries and modules with respective counterparts in javascript

    Returns:
        json: pair of python and javascript libraries and modules
"""
import subprocess
import time
import re
from core.log import Log
from core.code_extractor import CodeExtractor
from core.operator import CodeOperator, Finder
from config import MAX_LOOP, START_LOOP, MESSAGES

class CounterpartsPrompter:
    """Prompt for counterparts of python libraries and modules in javascript"""
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

    def dependencies_prompter_and_installer(self, libs, nonavailables) -> None | str:
        """read the python file, call translator on it, and save the corrected code """
        try:
            # First prompt on translator
            python_libraries = self.translate_dependencies(nonavailables)
            # Update libs with available counterparts in counterparts.json
            libs.update(python_libraries)

            if libs:
                loop_counter = START_LOOP
                while True:
                    # Check if there are errors in the installation of dependencies
                    if all(lib_values[0] is None for lib_values in libs.values()):
                        self.log.info("None of the dependencies have counterparts in javascript!")
                        break

                    if any(lib_values[0] is None for lib_values in libs.values()):
                        self.log.info(f"There are no counterparts for {[lib_key for lib_key, lib_values in libs.items() if lib_values[0] is None]} in javascript!")
                        libs = {lib_key: lib_values for lib_key, lib_values in libs.items() if lib_values[0] is not None}
                        _ , error = self.install_dependencies(libs)
                    else:
                        _ , error = self.install_dependencies(libs)

                    if error:
                        start_time = time.time()
                        self.log.info(f"Found errors when installing counterparts. Prompting for corrections. Number of tries: {loop_counter+1}")
                        # Provide the code and error to GPT to make corrections
                        raw_string = MESSAGES['msg_dependency_installation_error'][1]['content']
                        data = {'libs': libs, 'error': error}
                        MESSAGES['msg_dependency_installation_error'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_dependency_installation_error'][1]['content'])
                        correction = self.connector.get_completions(MESSAGES['msg_dependency_installation_error'])
                        self.code_extractor.set_text(correction.choices[0].message.content)
                        MESSAGES['msg_dependency_installation_error'][1]['content'] = raw_string
                        # extract the corrected code
                        libs = self.code_extractor.create_dict()
                        end_time = time.time()
                        self.log.info(f"Time taken to provide counterparts in javascript by GPT 3.5 in try: {loop_counter+1} Time elapsed: {end_time - start_time}")
                    else:
                        self.log.info("Successfully installed dependencies provided by GPT 3.5!")
                        break  # Exit the loop if no errors in installation
                    # Loop checker, break at maximimum number of loop
                    if loop_counter < MAX_LOOP:
                        loop_counter += 1
                    else:
                        self.log.error(f"Unable to provide correct counterparts by GPT 3.5 after {MAX_LOOP} tries!")
                        return None
            else:
                self.log.error("Unable to provide a js code by GPT 3.5 at early stage!")
                self.timing(self.start_overall_time)
                return None


            # Save the counterparts in a file
            if libs :
                # compare the libs with counterparts.json and update it
                self.code_op.update_json('counterparts.json', libs)
                self.timing(self.start_overall_time)
                return libs
            
        except Exception as e:
            self.log.error(f"Unable to feed signature into GPT 3.5: {python_libraries}.  \n{e}")



    def translate_dependencies(self, python_libraries:list)-> dict:
        """prompt for libraries and modules in python from a list of javascript libraries and modules"""
        # Prompt for python libraries and modules
        raw_string = MESSAGES['msg_counterparts_py'][1]['content']
        data = {'python_libraries': python_libraries}
        MESSAGES['msg_counterparts_py'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_counterparts_py'][1]['content'])
        completion = self.connector.get_completions(MESSAGES['msg_counterparts_py'])
        self.code_extractor.set_text(completion.choices[0].message.content)
        MESSAGES['msg_counterparts_py'][1]['content'] = raw_string
        counterparts_dict = self.code_extractor.create_dict()
        return counterparts_dict
    
    def install_dependencies(self, dependencies:dict):
        """Install dependencies in JavaScript code using npm"""
        self.log.info("***Installing dependencies by subprocess!")
        start_time = time.time()
        # Create a string of dependencies directly
        dependencies_str = " ".join(lib_values[0] for lib_key, lib_values in dependencies.items() if lib_values[0] is not None)

        #[TODO] Check the place of installation if it is in the right place
        # Run the JavaScript code using Node.js subprocess
        process = subprocess.Popen(f'npm install {dependencies_str}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()
        if process.returncode == 0:
            end_time = time.time()
            self.log.info(f"Installing dependencies by subprocess! Time elapsed: {end_time - start_time}")
            return output, None
        else:
            return output, error
