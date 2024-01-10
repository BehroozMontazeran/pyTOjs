"""Code extractor for different translated codes by GPT 3.5

Returns:
    text: runnable code
    """
import re

class CodeExtractor():
    """Code extractor from content of response of GPT 3.5"""
    def __init__(self):
        self.text = None

    def set_text(self, text):
        """Set the text for code extraction"""
        self.text = text

    def extract_python_code(self):
        """Python code extractor

        Returns:
            text: runnable code
            None: None
        """
        if self.text is None:
            print("Error: No text provided for extraction.")
            return None
        # Use regex to find the usual structure of the python code
        if re.findall(r'```python', self.text):
            # Use regex to find Python code within triple backticks
            code_match = re.search(r'```python\n(.*?)\n```', self.text, re.DOTALL)

            if code_match:
                python_code = code_match.group(1)
                return python_code.strip()
            else:
                return None
        else:
            return self.text
        
    def extract_js_code(self):
        """JavaScript code extractor

        Returns:
            text: runnable code
            None: None
        """
        if self.text is None:
            print("Error: No text provided for extraction.")
            return None
        # Use regex to find the usual structure of the javascript code
        if re.findall(r'```javascript', self.text):
            # Use regex to find js code within triple backticks
            code_match = re.search(r'```javascript\n(.*?)\n```', self.text, re.DOTALL)

            if code_match:
                js_code = code_match.group(1)
                return js_code.strip()
            else:
                return None
        else:
            return self.text
        
    # def extract_js_unittest(self):
    #     """JavaScript unittest code extractor

    #     Returns:
    #         text: runnable code
    #         None: None
    #     """
    #     if self.text is None:
    #         print("Error: No text provided for extraction.")
    #         return None

    #     # Use regex to find js code within triple backticks
    #     code_match = re.search(r"\n\n(.*?)\}\)\;\'", self.text, re.DOTALL)

    #     if code_match:
    #         js_code = code_match.group(1)
    #         # Remove the first line from the extracted code
    #         lines = js_code.strip().split('\n')[1:]
    #         return '\n'.join(lines).strip()
    #     else:
    #         return self.text

