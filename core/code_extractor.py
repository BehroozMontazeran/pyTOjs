"""Code extractor for different translated codes by GPT 3.5

Returns:
    text: runnable code
    """
import re
import ast

class CodeExtractor():
    """Code extractor from content of response of GPT 3.5"""
    def __init__(self):
        self.text = None

    def set_text(self, text):
        """Set the text for code extraction"""
        self.text = text

    def extract_code(self):
        """code extractor

        Returns:
            text: runnable code
            None: None
        """
        if self.text is None:
            return None
        # Use regex to find the usual structure of the python code
        elif re.findall(r'```python', self.text):
            # Use regex to find Python code within triple backticks
            code_match = re.search(r'```python\n(.*?)\n```', self.text, re.DOTALL)

            if code_match:
                python_code = code_match.group(1)
                return python_code.strip()
            else:
                return None
        elif re.findall(r'```javascript', self.text):
            # Use regex to find js code within triple backticks
            code_match = re.search(r'```javascript\n(.*?)\n```', self.text, re.DOTALL)

            if code_match:
                js_code = code_match.group(1)
                return js_code.strip()
            else:
                return None
        # elif re.findall(r'```message', self.text):
        #     # Use regex to find js code within triple backticks
        #     code_match = re.search(r'```message\n(.*?)\n```', self.text, re.DOTALL)

        #     if code_match:
        #         js_code = code_match.group(1)
        #         return js_code.strip()
        #     else:
        #         return None
        else:
            return self.text
        
                
    def create_dict(self):
        """Create a dictionary from the extracted code"""
        if self.text is None:
            return None
        else:
            # Convert the new data text to a dictionary
            new_data = {}
            lines = self.text.strip().split('\n')
            if len(lines) != 0:
                # lines = self.text.strip().split('\n')
                for line in lines:
                    if ';' in line:
                        key, value = line.split(';', 1)  # Split only once to handle cases where value contains ';'
                        key = key.strip()
                        value = value.strip()
                        new_data[key] = [None] if value == 'None' else value.split(', ')
                return new_data
        
    # def create_dict(self):
    #     """Create a dictionary from the extracted code"""
    #     if self.text is None:
    #         return None
    #     else:
    #         # Convert the new data text to a dictionary
    #         new_data = {}
    #         lines = self.text.strip().split('\n')
    #         if len(lines) == 1:
    #             new_data = ast.literal_eval(self.text)
    #             return new_data
    #         else:
    #             for line in lines:
    #                 if ';' in line:
    #                     key, value = line.split(';', 1)  # Split only once to handle cases where value contains ';'
    #                     key = key.strip()
    #                     value = value.strip()
    #                     new_data[key] = [None] if value == 'None' else value.split(', ')
    #             return new_data
            

