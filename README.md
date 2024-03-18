# pyTOjs


This repository is a toolkit to translate python to JavaScript codes using LLMs, especially GPT.

Even translating a simple code from one programming language to another one using GPT would be challenging, though a repository. So far, many has attempted to find a solution for translating simple codes like [CodeGen](https://github.com/facebookresearch/CodeGen). In this repository, I tried to provide a base method to split repository using [ast](https://docs.python.org/3/library/ast.html), [astunparse](https://pypi.org/project/astunparse/), to translate chunks of codes using GPT Turbo 3.5, to write, to translate unittest for each function using GPT and finally to combine the chunks in the target language using [esprima](https://esprima.org/), [escodegen](https://github.com/estools/escodegen) and [jsbeautifier](https://beautifier.io/).

## Intuition
### Splitting
A repository will be traversed for `.py` files and a list of signatures for each module will be made.
 Codes are separated to simple and complex ones based on existence of classes and number of functions.
#### simple codes
* if a module has only one function or no function it will be simple codes.
#### complex codes
* any other codes rather than simple ones are complex code, even codes with two functions and more or if a class exists  in the code.

This method of splitting comes from many tests of different  types of codes and GPT limitations in translation of the codes. To find a trade-off between the accuracy and lowest number of prompts, it is needed to obey a separation logic to split the codes to [module_signature](#module_signature), [methods_signature](#methods_signature), [dependencies_signature](#dependencies_signature),[sorted_signature](sorted_signatures), [calls](calls) in [splitter](splitter).

#### module_signature
* In this all the module level components will be collected. To reduce the size of message for prompting functions and methods are recorded without their bodies, except for `__init__ `constructors, which are needed to be feed into GPT with respective class to increase the accuracy.

 #### methods_signature
 * Functions and methods with their bodies are collected under this signature. which will be used later for unittest prompting and translating as well as evaluation of GPT responses.

#### dependencies_signature
* All imports and from-imports will be retained under this signature, that will be used to resolve the dependencies of complex code.

#### sorted_signatures
sorted_signatures are used to order the components of the module at the time of prompting.

#### calls
This a reserved signature for further  developments, which will collect all the calls inside the given code with their context of occurrence,e.g: function, method, class

## Prompting
This project will use zero-shot prompting.
Using GPT 3.5 Turbo with its maximum number of tokens, which is needed to send the whole module_signature of a complex code at the first prompt and later at the time of error occurrence module_signature + translated code + error message to GPT for the sake of accuracy of the response. 
Each prompt messages in [config.py](config.py) have been developed and improved based on respective use cases.

## Combining
[simple codes](#simple-codes) do not need any combinations, however, complex codes are combined based on separated functions and methods that are translated and tested separately from [module_signature](#module_signature).
In [combiner](combiner), signatures of the translated components  in JavaScript are made, based on which the combination of a module with its isolated components are done.

## Dependency Resolving
This part is heavily dependent on [counterparts.json](counterparts.json), which will keep the record  of all corresponding python libraries and their counterparts in JavaScript.
Those codes that are dependent on libraries or modules will be addressed in [counterparts_prompter.py](translators/counterparts_prompter.py). All local modules are listed in split phase in order not to be used in prompt messages for counterparts finding. Moreover, those libraries that are available in [counterparts.json](counterparts.json) will not be added to the prompt messages as well. After receiving the response from GPT to provide counterparts for the missing libraries of python in JavaScript, the suggestions will be install locally using [subprocess](https://docs.python.org/3/library/subprocess.html) to validate the suggestions, by which two targets are followed. First evaluation of suggested counterparts. Second installing necessary dependencies in JavaScript for further tests and usage. After successful tests of counterparts, they will be added to the [counterparts.json](counterparts.json) and in case of any failures, the prompt will be repeated with the list of missing counterparts and error.

## Translations/Completions
This part of the project will run in three phases. 
#### [py_unittest_prompter](translators/py_unittest_prompter.py)
Firstly, the function or method codes, will be feed separately into GPT to create unittest for each one. These unittests will be used later for inside evaluation of the project and additionally feed again into GPT to be translated to JavaScript to have unittests for translated JavaScript codes as well. The successful unittests run by subprocess are stored separately in the respective folder `py_unittests` under the name of each module. At the time of error the prompt will be repeated until success or reaching the maximum level of loop, which can be set in [config.py](config.py). In this case the prompt message would be concatenation of function_signature + translated function + error.

#### [py_to_js_translator](translators/py_to_js_translator.py)
Then the functions, methods or modules will be prompted for translation.
The same process will happen as [py_unittest_prompter](#py_unittest_prompter) but for translation. The big difference is translation of module_signature as a base file for combination phase that is saved under the same name of given module in `.js`. The successful translated functions and methods will be concatenated in `functions.js` under the same folder of respective module.

#### [py_unittest_translator](translators/py_unittest_translator.py)

Lastly the translated functions and methods are prompted for translation. The successful translated ones will be saved in the respective folder `js_unittests` under the name of each module. 

## [main.py](main.py)
Each part of the main is as follows:

* Split the given project into python signatures and its files
```python
py_sigs, project_files = splitters.split(DATA_POOL)
```

* Decide on simple code or complex one
```python

    for _, py_sig in enumerate(py_sigs):
        # analyze the python module
        for item in py_sig['sorted_signature']:
            if 'class' in item:
                CMPLX = True
        if len(py_sig['methods_signature']) > 1 or CMPLX:
            # Complex modules which need splitting and combining
            run(code_operators, finders, combiners, project_operators, py_sig, project_files)

        else:
            # Simple modules which don't need splitting and combining
            run(code_operators, finders, combiners, project_operators, py_sig, project_files, cmplx=False)
```

* Inside evaluation of the results
```python
evaluate.count_errors()
evaluate.plot_errors()
```

* Create neccessary files and folders
```python
project_path, js_path, function_path = project_operator.project_creator(py_signatures['file_path'], cmplx)

```
* Handle the dependencies

```python
    counterparts, unavailables = finder.counterparts_finder(py_signatures['dependencies_signature'], files)
    # Prompt for counterparts of python libraries that are not in counterparts.json, update counterparts.json and install them as well
    counterparts_prompter = translators.CounterpartsPrompter(connectors)
    if unavailables:
        installed_counterparts, unavailable_counterpart = counterparts_prompter.dependencies_prompter_and_installer(counterparts, unavailables)
    elif counterparts:
        # Check if all needed counterparts are installed
        error = counterparts_prompter.install_dependencies(counterparts)
        if not error:
            installed_counterparts = counterparts
            unavailable_counterpart = None
    else:
        installed_counterparts = None
        unavailable_counterpart = None
```

* Prompt for unittests and translations of simple codes

```python
 # Translate simple code to JavaScript
if not cmplx:
    module = None
    non_module = py_translator.py_translator_checker(project_path, py_signatures, installed_counterparts, cmplx=cmplx, unavailable_counterparts=unavailable_counterpart)
    if non_module:
        # Create a unit test
        py_unittest_prompter = translators.PyUnittestPrompter(connectors)
        py_unittest = py_unittest_prompter.py_unittest_checker(project_path, py_signatures, py_signatures, module=module, cmplx=cmplx)
        if py_unittest:
            # Translate the generated unit test code to javascript
            py_unittest_translator = translators.PyUnittestTranslator(connectors)
            py_unittest_translator.py_translator_checker(project_path, py_signatures, py_unittest, non_module, module=module)
        else:
```

* Prompt for unittests and translations of complex codes

```python
# Translate module signature to JavaScript for complex codes
    module = py_translator.py_translator_checker(project_path, py_signatures, installed_counterparts, unavailable_counterparts=unavailable_counterpart)
if module:
    for _, fn_signature in enumerate(py_signatures['methods_signature']):
        # Create a unit test for each method
        py_unittest_prompter = translators.PyUnittestPrompter(connectors)
        py_unittest = py_unittest_prompter.py_unittest_checker(project_path, fn_signature, py_signatures, module)
        if py_unittest:
            # Translate the python method to javascript
            py_translator = translators.PyTranslator(connectors)
            translated_func = py_translator.py_translator_checker(project_path, fn_signature, installed_counterparts, func_trans=True, unavailable_counterparts=unavailable_counterpart)
            if translated_func:
                # Translate the generated unit test code to javascript
                py_unittest_translator = translators.PyUnittestTranslator(connectors)
                py_unittest_translator.py_translator_checker(project_path, fn_signature, py_unittest, translated_func, module=module)
```

* Combine the complex codes
```python

if module and py_unittest_translator:
    # read the code from the files
    base_code = code_operator.read(js_path)
    elements_code = code_operator.read(function_path)
    # Combine the generated code to one file
    combiner.combine(js_path, base_code, elements_code)

```

## Run the project

### Dependencies
* Run [requirements.txt](requirements.txt).
The project is written based on [PEP8](https://peps.python.org/pep-0008/)
### Run
* Put your repository or folder of python modules in the [data_pool](data_pool) and set the respective address as the value of `RESOURCE` in [config.py](config.py).

* Simply run the `python -m main` in the root direction of the project. Logs and the results of evaluation will be found in [logs](logs) folder and the final graph of the results will be popped up at end of translating the whole given repository or folder.

## Further improvments

This mega huge project needs more time to be a commercial  product. As there are limitations in ast library, GPT and the proper unittests running. However, as expressed earlier this can be a foundation for further attempts to resolve the problem of translating complex codes and repository using LLMs.
To be more specific the following can be addressed as a follow-up process:
* Providing a comprehensive `counterparts.json` which can be added to project by [RAG](https://blogs.nvidia.com/blog/what-is-retrieval-augmented-generation/) or any other innovative method.
* Running `JavaScript unittests` is challenging using subprocess, another method is suggested.
* Other methods of evaluating GPT responses can be added to the project.
* Dependencies that do not have any counterparts in JavaScript needs to be resolved. Unless some modules can not be translated properly at all. 
