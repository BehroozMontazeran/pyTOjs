""" Counterparts Prompter to prompt for collecting and updating python libraries and modules with respective counterparts in javascript

    Returns:
        json: pair of python and javascript libraries and modules saved in counterparts.json
"""

import subprocess
import re
from core.log import Log
from core.code_extractor import CodeExtractor
from core.operator import CodeOperator, Finder
from utils.utils import Utils
from config import MAX_LOOP, START_LOOP, MESSAGES

class CounterpartsPrompter:
    """Prompt for counterparts of python libraries and modules in javascript"""
    def __init__(self, connector) -> None:
        self.log = Log(self.__class__.__name__)
        self.code_extractor = CodeExtractor()
        self.code_op = CodeOperator()
        self.code_finder = Finder()
        self.utils = Utils()
        self.connector = connector
        self.start_overall_time = self.utils.get_timestamp()
        self.installed_lib = None
        self.unavailable_counterparts = []


    def dependencies_prompter_and_installer(self, libs, unavailables):
        """read the python file, call translator on it, and save the corrected code """
        try:
            # First prompt on translator
            translated_libraries = self.translate_dependencies(unavailables)
            # Update libs with available counterparts in counterparts.json
            libs.update(translated_libraries)
            complete_libs = libs.copy()


            if libs:
                loop_counter = START_LOOP
                while True:
                    # Check if there are errors in the installation of dependencies
                    if all(lib_values[0] is None for lib_values in libs.values()):
                        self.log.warning("None of the dependencies have counterparts in javascript!")
                        break

                    if any(lib_values[0] is None for lib_values in libs.values()):
                        self.unavailable_counterparts = [lib_key for lib_key, lib_values in libs.items() if lib_values[0] is None]
                        self.log.warning(f"There are no counterparts for {self.unavailable_counterparts} in javascript!")
                        libs = {lib_key: lib_values for lib_key, lib_values in libs.items() if lib_values[0] is not None}
                        errors = self.install_dependencies(libs)
                    else:
                        errors = self.install_dependencies(libs)

                    if errors:
                        # for failure in failed_dependencies:
                        start_time = self.utils.get_timestamp()
                        self.log.info("Found errors when installing counterparts. Prompting for corrections...")
                        # Provide the code and error to GPT to make corrections
                        raw_string = MESSAGES['msg_dependency_installation_error'][1]['content']
                        data = {'errors': errors}
                        MESSAGES['msg_dependency_installation_error'][1]['content'] = re.sub(r'\{(\w+)\}', lambda x: str(data.get(x.group(1))), MESSAGES['msg_dependency_installation_error'][1]['content'])
                        correction = self.connector.get_completions(MESSAGES['msg_dependency_installation_error'])
                        self.code_extractor.set_text(correction.choices[0].message.content)
                        MESSAGES['msg_dependency_installation_error'][1]['content'] = raw_string
                        # extract the corrected code
                        libs = self.code_extractor.create_dict()
                        self.utils.timing(start_time, self.utils.get_timestamp(), f"Providing counterparts by GPT in try: {loop_counter+1}", "info")
                    else:
                        self.utils.timing(self.start_overall_time, self.utils.get_timestamp(), "Successfully installed dependencies provided by GPT!", "info")
                        break  # Exit the loop if no errors in installation
                    # Loop checker, break at maximimum number of loop
                    if loop_counter < MAX_LOOP:
                        loop_counter += 1
                    else:
                        self.log.error(f"Unable to provide correct counterparts by GPT 3.5 after {MAX_LOOP} tries!")
                        return [], []
            else:
                self.utils.timing(self.start_overall_time, self.utils.get_timestamp(), "Unable to provide counterparts by GPT!", "error")
                return [], []

            # Return the installed libraries and local modules
            if complete_libs:
                local_libs = {key: value for key, value in complete_libs.items() if value == 'local'}
                if len(local_libs)!=0:
                    self.installed_lib.update(local_libs)
                else:
                    self.unavailable_counterparts = [key for key, value in complete_libs.items() if value[0] is None]
                    self.utils.timing(self.start_overall_time, self.utils.get_timestamp(), "Providing counterparts", "info")
                return self.installed_lib, self.unavailable_counterparts
            
        except Exception as e:
            self.log.error(f"Unable to feed into GPT!\n{translated_libraries}  \n {e}")

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
    

    def is_library_installed(self, library_name: str) -> bool:
        """Check if a library is installed using npm"""
        process = subprocess.Popen(f'npm list {library_name}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, _ = process.communicate()
        return library_name in output

    def install_dependencies(self, dependencies: dict):
        """Install dependencies in JavaScript code using npm"""
        self.log.info("*"*10+"Installing dependencies by subprocess!"+"*"*10)

        first_words = {}
        for key, value_list in dependencies.items():
            if value_list[0] is not None and 'local' not in value_list and 'None' not in value_list:
                first_words[key] = [value.split()[0].lower() for value in value_list]
        failed_list = []
        success_list = []
        for key, value in first_words.items():
            if self.is_library_installed(value[0]):
                success_list.append((key, value[0]))
                self.log.info(f"{value[0]} is already installed.")
            else:
                process = subprocess.Popen(f'npm install {value[0]}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                output, error = process.communicate()
                if process.returncode == 0:
                    success_list.append((key, value[0]))
                    self.log.info(f"Installed {value[0]} successfully!")
                else:
                    self.log.error(f"Unable to install {value[0]} successfully!")
                    failed_dependencies = {'python_library': key, 'suggested_js_library': value[0], 'error': error}
                    failed_list.append(failed_dependencies)
        # Save the counterparts in a file
        if success_list:
            # compare the libs with counterparts.json and update it
            self.code_op.update_json('counterparts.json', dict(success_list))
            if self.installed_lib:
                self.installed_lib.update(dict(success_list))
            else:
                self.installed_lib = dict(success_list)
        return failed_list
