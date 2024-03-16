"""Perform different actions on the code and project folder.
"""

from math import e
import os
import shutil
import re
import json
from tkinter import N

from core.log import Log
from config import ROOT, PY_UNITTEST, JS_METHODS, JS_UNITTEST, TRANSLATED_ROOT

class CodeOperator():
    """Operate on code to do various actions like save, read, append, etc."""
    def __init__(self):
        self.log = Log(self.__class__.__name__)

    def save(self, file_path: str, code: str, action='w'or'a'):
        """Write or append the code to the file"""
        try:
            # Check if the file exists
            if action == 'a': #os.path.exists(file_path) and 
                # File exists, open it and append the code
                with open(file_path, f'{action}', encoding='utf-8') as file:
                    file.write(code)
                    self.log.info(f"Successfully appended the corrected {self._type_detector(file_path)} code to the respective path: {file_path}")
            elif action == 'w':
                # File doesn't exist, create it and write the code
                with open(file_path, f'{action}', encoding='utf-8') as file:
                    file.write(code)
                    self.log.info(f"Successfully created and wrote the corrected {self._type_detector(file_path)} code to the respective path: {file_path}")
                # Append to the json file
            elif action == 'j':
                with open(file_path, 'w', encoding='utf-8') as json_file:
                    json.dump(code, json_file)
                    self.log.info(f"Successfully updated {self._type_detector(file_path)} in the respective path: {file_path}")
            else:
                self.log.error(f"Unable to update the File: {file_path}, the provided action is not supported.")
        except FileNotFoundError:
            self.log.error(f"Unable to write the File: {file_path}")

    def read(self, file_path: str, action='r'):
        """Write or append the code to the file"""
        try:
            # Check if the file exists
            if os.path.exists(file_path) and action == 'r':
                # File exists, open it and append the code
                with open(file_path, f'{action}', encoding='utf-8') as file:
                    self.log.info(f"Successfully read {self._type_detector(file_path)} code from respective path: {file_path}")
                    return file.read()

            elif os.path.exists(file_path) and action == 'j':
                with open(file_path, 'r', encoding='utf-8') as json_file:
                    # Load the dictionary from the JSON file
                    self.log.info(f"Successfully read {self._type_detector(file_path)} file from respective path: {file_path}")
                    return json.load(json_file)
            else:
                self.log.error(f"Unable to read the File: {file_path}, the provided action is not supported.")
                return None
        except FileNotFoundError:
            self.log.error(f"Unable to read the File: {file_path}")
            return None


    def update_json(self, json_file_path, input_dict):
        """Update the JSON file with the input dictionary ensuring values are lists."""
        # Load the existing JSON data from the file
        existing_data = self.read(json_file_path, 'j')
        if existing_data:
            # Update the existing data with the input dictionary
            for key, value in input_dict.items():
                # Ensure value is a list
                if not isinstance(value, list):
                    value = [value]

                if key in existing_data:
                    # If the key already exists, append the new values to the existing list if they're not already included
                    for item in value:
                        if item not in existing_data[key]:
                            existing_data[key].append(item)
                else:
                    # If the key doesn't exist, assign the new list as the value
                    existing_data[key] = value

            # Save the updated data back to the JSON file
            self.save('counterparts.json', existing_data, 'j')
        else:
            self.log.error(f"Unable to update the JSON file: {json_file_path}")


    
    # def update_json(self, json_file_path, input_dict):
    #     """Update the JSON file with the input dictionary"""
    #     # Load the existing JSON data from the file
    #     existing_data = self.read(json_file_path, 'j')

    #     # Update the existing data with the input dictionary
    #     for key, value in input_dict.items():
    #         if key in existing_data:
    #             # If the key already exists, append the new values to the existing list
    #             if value in existing_data[key]:
    #                 continue
    #             else:
    #                 existing_data[key].extend(value)
    #         else:
    #             # If the key doesn't exist, create a new list with the values
    #             existing_data[key] = value

    #     # Save the updated data back to the JSON file
    #     self.save('counterparts.json', existing_data, 'j')


    def _type_detector(self, file_path):
        """Detect the type of the file"""
        if file_path.endswith('.py'):
            type_code = 'python'
        elif file_path.endswith('.js'):
            type_code = 'javascript'
        elif file_path.endswith('.json'):
            type_code = 'json'
        else:
            self.log.error(f"Unable to detect the type of the file: {file_path}")
            return None
        return type_code

class Finder(CodeOperator):
    """Find the elements of the code."""
    def __init__(self):
        self.log = Log(self.__class__.__name__)
        super().__init__()

    def py_class_name(self, signature, module_signature):
        """ Find the class name of a python method in the module signature"""
        for _, class_name in enumerate(module_signature):
            if class_name['type'] == 'class' and str(class_name['name']) in signature['name']:
                    return class_name['name']

    def module_name(self, path):
        """ Find the python module name of a file"""
        # Get the base name of the file (including extension)
        file_name = os.path.basename(path)

        # Remove the file extension to get the module name
        module_name = os.path.splitext(file_name)[0]
        return module_name

    def py_module_file(self, path):
        """ Find the name of module file"""
        # Get the base name of the file (including extension)
        file_name = os.path.basename(path)
        return file_name
    
    def path_separator(self,path: str, part: int=-2):
        """ Separate deliberate parts of a path"""
        # Normalize path to convert any \\ to /
        normalized_path = os.path.normpath(path)

        # Split the path into parts
        parts = normalized_path.split(os.sep)
        # and not the top-level directory in the path, you can do:
        if len(parts) > 1:  # This checks if there are enough parts for a directory and a file
            sub_folder = parts[part]
        else:
            sub_folder = None  # No sub-folder available
        return sub_folder
    
    def dependencies_list(self, dependencies_signature):
        """ Find the list of dependencies in a signature"""
        # dependencies = [d['value']+'\n' for d in dependencies_signature]
        dependencies = '\n'.join([d['value'] for d in dependencies_signature])
        return dependencies
    
    def library_finder(self, javascript_code):
        """ Find the list of libraries used in the code"""
        # Regular expression to extract library names excluding those starting with './'
        pattern = re.compile(r"require\(['\"](?!\.\/)([^'\"]+)['\"]\);")

        # Find all matches in the JavaScript code
        matches = pattern.findall(javascript_code)

        # List to store the extracted library names
        libraries = list(set(matches))  # Using set to remove duplicates
        return libraries
    
    def counterparts_finder(self, libraries, files):
        """ Find the counterparts of python dependencies_signatures in json file"""
        # Read the json file
        counterparts = self.read('counterparts.json', 'j')

        # dict to store the counterparts of libraries
        counterparts_dict = {}
        nonavailables = []
        libraries = [lib['name'] for lib in libraries]
        # Find the counterparts of libraries
        for library in libraries:
            if library in counterparts and counterparts :
                counterparts_dict[library] = counterparts[library]
            elif library in files:
                counterparts_dict[library] = 'local'
            else:
                counterparts_dict[library] = [None]
                nonavailables.append(library)

        return counterparts_dict, nonavailables

class ProjectOperator(Finder):
    """Operate on project folder to create folders and relative path."""
    def __init__(self):
        self.log = Log(self.__class__.__name__)
        super().__init__()

    def project_creator(self, path: str, cmplx: bool = True):
        """Create a project folder and all the subfolders"""
        try:
            if cmplx:
                modeule_name = self.module_name(path)
                sub_root = self.path_separator(path)
                # Create if the project folder doesn't exist
                project_path = self.create_folder_if_not_exists(TRANSLATED_ROOT, sub_root, modeule_name)
                if project_path is not None:
                    function_path = self.create_address(project_path,None,'functions_code.js')
                    js_path = self.create_address(project_path,None ,self.module_name(path) + '.js')
                # Create source file in folder
                if project_path is not None and not self.is_file_in_folder(project_path, self.py_module_file(path)):
                    self.copy_file(path, project_path, self.py_module_file(path))
                    # Create all required subfiles or provide their addresses
                    self.create_file_if_not_exists(project_path, '__init__.py')
                    # function_path = self.create_address(project_path, 'functions_code.js')
                    # js_path = self.create_address(project_path, self.module_name(path) + '.js')
                    # Create all required subfolders
                    self.create_folder_if_not_exists(project_path, PY_UNITTEST)
                    self.create_folder_if_not_exists(project_path, JS_UNITTEST)
                    # self.create_folder_if_not_exists(project_path, JS_METHODS)
                    self.log.info(f"Successfully created the project folder: {project_path}")
                return project_path, js_path, function_path
            else:
                modeule_name = self.module_name(path)
                sub_root = self.path_separator(path)
                # Create if the project folder doesn't exist
                project_path = self.create_folder_if_not_exists(TRANSLATED_ROOT, sub_root, modeule_name)
                function_path = None
                if project_path is not None:
                    js_path = self.create_address(project_path,None ,self.module_name(path) + '.js')
                # Create source file in folder
                if project_path is not None and not self.is_file_in_folder(project_path, self.py_module_file(path)):
                    self.copy_file(path, project_path, self.py_module_file(path))
                    # Create all required subfiles or provide their addresses
                    self.create_file_if_not_exists(project_path, '__init__.py')
                    # function_path = self.create_address(project_path, 'functions_code.js')
                    # js_path = self.create_address(project_path, self.module_name(path) + '.js')
                    # Create all required subfolders
                    self.create_folder_if_not_exists(project_path, PY_UNITTEST)
                    self.create_folder_if_not_exists(project_path, JS_UNITTEST)
                    # self.create_folder_if_not_exists(project_path, JS_METHODS)
                    self.log.info(f"Successfully created the project folder: {project_path}")
                return project_path, js_path, function_path
        except FileExistsError:
            self.log.error(f"Unable to create the project folder: {project_path}")
            return None
                

    def create_address(self, path: str, folder_name = None, file_name = None):
        """Create the address of the file"""
        if folder_name is None and file_name:
            file_path = os.path.join(path, file_name)
        elif file_name is None and folder_name:
            file_path = os.path.join(path, folder_name)
        elif folder_name and file_name:
            file_path = os.path.join(path, folder_name, file_name)
        return file_path

    def is_file_in_folder(self, folder_path: str, file_name: str):
        """Check if the file exists in the folder"""
        file_path = os.path.join(folder_path, file_name)
        return os.path.isfile(file_path)
    
    def copy_file(self, source_folder: str, destination_folder: str, file_name: str):
        """Copy the file from source to destination"""
        # source_path = os.path.join(source_folder, file_name)
        destination_path = os.path.join(destination_folder, file_name)
        
        try:
            shutil.copy(source_folder, destination_path)
            self.log.info(f"File '{file_name}' successfully copied from {source_folder} to {destination_folder}.")
        except FileNotFoundError:
            self.log.error(f"File '{file_name}' not found in {source_folder}.")
        except PermissionError:
            self.log.error(f"Permission error: Unable to copy file '{file_name}'.")

    def create_file_if_not_exists(self, folder_path: str, file_name: str):
        """Create a file if it doesn't exist"""
        file_path = os.path.join(folder_path, file_name)
        
        if not os.path.exists(file_path):
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    self.log.info(f"File '{file_name}' created in {folder_path}.")
                    file.write('')
                    return file_path
            except OSError as e:
                self.log.error(f"Error creating file '{file_name}' in {folder_path}: {e}")
                return None
        else:
            self.log.info(f"File '{file_name}' already exists in {folder_path}.")
            return file_path

    def create_folder_if_not_exists(self, parent_folder: str, sub_folder: str| None=None, folder_name:str="") -> str|None:
        """Create a folder if it doesn't exist"""
        if sub_folder is not None:
            folder_path = os.path.join(parent_folder, sub_folder, folder_name)
        else:
            folder_path = os.path.join(parent_folder, folder_name)
        
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
                self.log.info(f"Folder '{folder_name}' created in {parent_folder}.")
                return folder_path
            except OSError as e:
                self.log.error(f"Error creating folder '{folder_name}' in {parent_folder}: {e}")
                return None
        else:
            self.log.info(f"Folder '{folder_name}' already exists in {parent_folder}.")
            return folder_path
        
    def traverse_project(self, folder_path):
        """Traverse the project folder and yield the python file paths"""
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    yield file_path

