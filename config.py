"""Configuration Settings"""

# File path of the python code to be translated
# PATH = 'data_pool/project_example/environment_all.py'
# PATH = 'data_pool/NLP/qa.py'

# Directories
ROOT = "./"
PY_UNITTEST = "py_unittest"
JS_UNITTEST = "js_unittest"
JS_METHODS = "js_methods"
DATA_POOL = "data_pool"
TRANSLATED_ROOT = "translated_codes"

# Directory to store log files
LOG_DIR = "logs"

# Default user settings. Can be overridden by command line arguments.
DEFAULT_SETTINGS = {
    "log_file": f"{LOG_DIR}/system.log",
    "log_level": "INFO",
}

# Controler of loop for GPT prompt
MAX_LOOP = 2
START_LOOP = 0

# Messages to be sent to the GBT 3.5 API [TODO: use counterparts in the prompt messages]
# MESSAGES = { 'msg_ast_mth':[
#             {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
#             {"role": "user", "content": "translate the following function to javascript,  give me just translated function without wrapping it inside any arbitrary class and use the following template for that: \n\n```javascript\n code\n ```\n 1- the functions must be started with the word function function_name()\n 2- there is no __init__ function in js then change __init__ to  constructor if there is any:\n function_code:\n\n{function_code}"}
#         ],
#         'msg_ast_ml':[ 
#             {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
#             {"role": "user", "content": "translate the following ast tree to javascript, there must be {number_of_classes} classes. Use the following template for the whole code: \n\n```javascript\n code\n ```\n  ast tree:\n\n{python_module}"}
#         ],
#         'msg_ast_fn':[ 
#             {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
#             {"role": "user", "content": "translate the following python file completely to javascript.1- the whole file must be translated. 2- when any dependency is not available in the target language comment it out and never remove it 3- Use the following template for the whole code: \n\n```javascript\n code\n ```\n  python file:\n\n{python_module}"}
#         ],
#         'msg_ast_error':[
#             {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
#             {"role": "user", "content": "The javascript code you provided raises an error. Change the included js code in order not to raise the following included error. Always response using the following template for provided code: \n\n```javascript\n provided code\n ```\n\nIncluded js code:\n\n{js_code} \n\nIncluded error:\n\n{error}"}
#         ],
#         'msg_py_ast_error':[
#             {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
#             {"role": "user", "content": "The python unittest code you provided raises an error. Change the included python unittest code in order not to raise the following included error. Always response using the following template for provided code: \n\n```python\n provided code\n ```\n\nIncluded python unittest code:\n\n{py_code} \n\nIncluded error:\n\n{error}"}
#         ],
#         'msg_py_unittest':[
#             {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
#             {"role": "user", "content": "{function_name} is a method of class called {class_name} from the actual module called {module_name}. write a unittest for the following method :\n 1- Use only following for importing the module.\n from {module_name} import {class_name}\n 2-Always response using the following template for provided code: \n\n```python\n provided code\n ```\n\n ast:\n\n{ast}"}
#         ],
#         'msg_translated_unittest_error': [
#             {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
#             {"role": "user", "content": "The translated unit test code you provided raises an error. Change the included unit test code in order not to raise the following included error. Always response using the following template for provided code: \n\n```javascript\n provided code\n ```\n\nIncluded unittest code:\n\n{js_code} \n\nIncluded error:\n\n{error}"}
#         ],
#         'msg_translate_unittest': [
#             {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
#             {"role": "user", "content": "Translate the following Python unit test code to JavaScript unit test. Always response using the following template for provided code: \n\n```javascript\n provided code\n ```\n\npython unit test:\n\n{function_code}"}
#         ],
#         'msg_ast_dp': [
#             {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
#             {"role": "user", "content": "Given the following Python dependencies, provide the JavaScript counterparts or modules for each in one code snippet. 1 -Ensure to provide actual counterparts and modules instead of placeholders. 2- Only for unavailable direct counterparts ,ensure to provide code snippets using hypothetical JavaScript libraries that mimic the functionality of them 3- Ensure to provide code-focused responses. 4- Ensure to provide uncommented codes after any comments :\n\n{ast_signature}"}#   3- to install these counterparts in Node.js, put a list of commented of them at the beginning of the code in this format:\n // npm install counterparts\n
#         ],
#         'msg_dependency_installation_error':[
#             {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
#             {"role": "user", "content": "One or some of the counterparts you provided do not exist in javascript.1- provide alternatives.\n2- Ensure to provide the response using the following template: {python_library; js_library1, js_library2, and so on}. 3 - If there isn't any similar library, response using following template: {python_library; None} python libraries:\n\n{python_libraries}\n\nIncluded libs:\n\n{libs} \n\nIncluded error:\n\n{error}"}
#         ],
#         'msg_counterparts_py':[
#             {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
#             {"role": "user", "content": "given the list of libraries and modules in python,what are their counterparts in javascript. 1- Ensure to provide the response using the following template:\n python_library; js_library1, js_library2, and so on. 2 - If there isn't any similar library, response using following template:\n python_library; None\n python libraries:\n\n{python_libraries}"}
#         ],

        # }
MESSAGES = { 'msg_ast_mth':[
            {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
            {"role": "user", "content": "translate the following function to javascript,  give me just translated function without wrapping it inside any arbitrary class and use the following template for that: \n\n```javascript\n code\n ```\n 1- the functions must be started with the word function function_name()\n 2- there is no __init__ function in js then change __init__ to  constructor if there is any:\n 3- Given counterparts in js must be considered when translating the function to js\n function_code:\n\n{function_code} \n\nGiven counterparts:\n\n{counterparts}"}
        ],
        'msg_ast_ml':[ 
            {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
            {"role": "user", "content": "translate the following ast tree to javascript.\n1- there must be {number_of_classes} classes.\n2- Use the following template for the whole code: \n\n```javascript\n code\n ```\n3- Given counterparts in js must be considered when translating the module to js\n\n  ast tree:\n\n{python_module} \n\nGiven counterparts:\n\n{counterparts}"}
        ],
        'msg_ast_fn':[ 
            {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
            {"role": "user", "content": "translate the following python file completely to javascript.1- the whole file must be translated. 2- Given counterparts in js must be considered when translating the module to js\n 3- Use the following template for the whole code: \n\n```javascript\n code\n ```\n  python file:\n\n{python_module} \n\nGiven counterparts:\n\n{counterparts}"}
        ],
        'msg_ast_error':[
            {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
            {"role": "user", "content": "The javascript code you provided raises an error. Change the included js code in order not to raise the following included error. Always response using the following template for provided code: \n\n```javascript\n provided code\n ```\n\nIncluded js code:\n\n{js_code} \n\nIncluded error:\n\n{error}"}
        ],
        'msg_py_ast_error':[
            {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
            {"role": "user", "content": "The python unittest code you provided raises an error. Change the included python unittest code in order not to raise the following included error. Always response using the following template for provided code: \n\n```python\n provided code\n ```\n\nIncluded python unittest code:\n\n{py_code} \n\nIncluded error:\n\n{error}"}
        ],
        'msg_py_unittest':[
            {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
            {"role": "user", "content": "{function_name} is a method of class called {class_name} from the actual module called {module_name}. write a unittest for the following method :\n 1- Use only following for importing the module.\n from {module_name} import {class_name}\n 2-Always response using the following template for provided code: \n\n```python\n provided code\n ```\n\n ast:\n\n{ast}"}
        ],
        'msg_translated_unittest_error': [
            {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
            {"role": "user", "content": "The translated unit test code you provided raises an error. Change the included unit test code in order not to raise the following included error. Always response using the following template for provided code: \n\n```javascript\n provided code\n ```\n\nIncluded unittest code:\n\n{js_code} \n\nIncluded error:\n\n{error}"}
        ],
        'msg_translate_unittest': [
            {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
            {"role": "user", "content": "Translate the following Python unit test code to JavaScript unit test. Always response using the following template for provided code: \n\n```javascript\n provided code\n ```\n\npython unit test:\n\n{function_code}"}
        ],
        'msg_ast_dp': [
            {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
            {"role": "user", "content": "Given the following Python dependencies, provide the JavaScript counterparts or modules for each in one code snippet. 1 -Ensure to provide actual counterparts and modules instead of placeholders. 2- Only for unavailable direct counterparts ,ensure to provide code snippets using hypothetical JavaScript libraries that mimic the functionality of them 3- Ensure to provide code-focused responses. 4- Ensure to provide uncommented codes after any comments :\n\n{ast_signature}"}#   3- to install these counterparts in Node.js, put a list of commented of them at the beginning of the code in this format:\n // npm install counterparts\n
        ],
        'msg_dependency_installation_error':[
            {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
            {"role": "user", "content": "One or some of the counterparts you provided do not exist in javascript.1- provide alternatives.\n2- Ensure to provide the response using the following template: {python_library; js_library1, js_library2, and so on}. 3 - If there isn't any similar library, response using following template: {python_library; None} python libraries:\n\n{python_libraries}\n\nIncluded libs:\n\n{libs} \n\nIncluded error:\n\n{error}"}
        ],
        'msg_counterparts_py':[
            {"role": "system", "content": "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"},
            {"role": "user", "content": "given the list of libraries and modules in python,what are their counterparts in javascript. 1- Ensure to provide the response using the following template:\n python_library; js_library1, js_library2, and so on. 2 - If there isn't any similar library, response using following template:\n python_library; None\n python libraries:\n\n{python_libraries}"}
        ],

        }