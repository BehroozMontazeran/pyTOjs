"""Perform different actions on the code and project folder.
"""

import os
import shutil

from core.log import Log
from config import ROOT, PY_UNITTEST, JS_METHODS, JS_UNITTEST

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
            else:
                self.log.error(f"Unable to write the File: {file_path}, the provided action is not supported.")
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
            else:
                self.log.error(f"Unable to read the File: {file_path}, the provided action is not supported.")
                return None
        except FileNotFoundError:
            self.log.error(f"Unable to read the File: {file_path}")
            return None

    def _type_detector(self, file_path):
        """Detect the type of the file"""
        if file_path.endswith('.py'):
            type_code = 'python'
        elif file_path.endswith('.js'):
            type_code = 'javascript'
        else:
            self.log.error(f"Unable to detect the type of the file: {file_path}")
            return None
        return type_code

class Finder():
    """Find the elements of the code."""
    def __init__(self):
        self.log = Log(self.__class__.__name__)

    def py_class_name(self, signature, module_signature):
        """ Find the class name of a python method in the module signature"""
        for _, class_name in enumerate(module_signature):
            for _, method in enumerate(class_name['body']):
                if signature['name'] in method:
                    return class_name['name']

    def py_module_name(self, path):
        """ Find the python module name of a file"""
        # Get the base name of the file (including extension)
        file_name = os.path.basename(path)

        # Remove the file extension to get the module name
        module_name = os.path.splitext(file_name)[0]
        return module_name

    def py_module_file(self, path):
        """ Find the python module name of a file"""
        # Get the base name of the file (including extension)
        file_name = os.path.basename(path)
        return file_name

class ProjectOperator(Finder):
    """Operate on project folder to create folders and relative path."""
    def __init__(self):
        self.log = Log(self.__class__.__name__)
        super().__init__()

    def project_creator(self, path: str):
        """Create a project folder and all the subfolders"""
        try:
            project_path = f'project_{self.py_module_name(path)}'
            # Create if the project folder doesn't exist
            project_path = self.create_folder_if_not_exists(ROOT, project_path)
            # Create source file in folder
            if not self.is_file_in_folder(project_path, self.py_module_file(path)):
                self.copy_file(path, project_path, self.py_module_file(path))
                # Create all required subfiles
                self.create_file_if_not_exists(project_path, '__init__.py')
                # Create all required subfolders
                self.create_folder_if_not_exists(project_path, PY_UNITTEST)
                self.create_folder_if_not_exists(project_path, JS_UNITTEST)
                self.create_folder_if_not_exists(project_path, JS_METHODS)
                self.log.info(f"Successfully created the project folder: {project_path}")
            return project_path
        except FileExistsError:
            self.log.error(f"Unable to create the project folder: {project_path}")
            return None
                

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

    def create_folder_if_not_exists(self, parent_folder: str, folder_name:str):
        """Create a folder if it doesn't exist"""
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

