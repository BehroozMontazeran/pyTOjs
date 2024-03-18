""" This module is responsible for evaluating the results of subprocess throughout the program. """

import matplotlib.pyplot as plt

from tabulate import tabulate

from core.log import Log
from config import EVAL_LIST


class EVAL():
    " Collect and evaluate the results of subprocess throughout the program."
    eval_calls = 0  # Class-level variable to store the total number of eval method calls
    
    def __init__(self):
        self.log = Log(self.__class__.__name__)
        self.error_types = ['SyntaxError', 'ReferenceError', 'TypeError', 'AssertionError', 'NameError', 'RangeError', 'ZeroDivisionError', 'ValueError', 'ImportError', 'IndexError', 'KeyError', 'MemoryError', 'OverflowError']
        self.error_counts = {error_type: 0 for error_type in self.error_types}
        self.error_data = []

    def eval(self, eval_list, message, context, t ):
        """Evaluate the message from subprocess"""
        EVAL.eval_calls += 1  # Increment the class-level counter
        if message == "":
            pass
        else:
            for error_type in self.error_types:
                if error_type in message:
                    eval_list.append({'error_type': error_type, 'context': context, 'message': message, 'time': t})


    def count_errors(self):
        """Count the errors based on type and print the results"""
        for error in EVAL_LIST:
            self.error_counts[error['error_type']] += 1
        
        total_prompts = EVAL.eval_calls
        

        total_errors = 0  # Total count of all errors
        for error_type, count in self.error_counts.items():
            self.error_data.append([error_type, count, f"{(count / total_prompts) * 100:.2f}%"])
            total_errors += count
        
        # Calculate success percentage
        success_percentage = ((total_prompts - total_errors) / total_prompts) * 100
        
        # Append the total number of eval calls and success percentage as additional rows
        self.error_data.append(['Success', '', f"{success_percentage:.2f}%"])
        self.error_data.append(['Failure', '', f"{abs(100-success_percentage):.2f}%"])
        self.error_data.append(['Total Prompts', EVAL.eval_calls, '100.00%'])
        
        self.log.info("Error Counts:")
        self.log.info(tabulate(self.error_data, headers=['Error Type', 'Count', 'Percentage'], tablefmt='grid'))

    def plot_errors(self):
        """Plot the error counts based on percentages"""
        error_data_filtered = self.error_data[:-1]
        
        error_types = [error[0] for error in error_data_filtered]
        percentages = [error[2].rstrip('%') for error in error_data_filtered]  # Remove '%' symbol
        
        # Assigning colors based on error type
        colors = ['skyblue'] * len(error_types)
        
        # Color the success rate green
        success_index = len(error_types) - 2
        colors[success_index] = 'green'
        
        # Color the failure rate red
        failure_index = len(error_types) - 1
        colors[failure_index] = 'red'
        
        plt.bar(error_types, [float(p) for p in percentages], color=colors)
        plt.xlabel('Error Type')
        plt.ylabel('Percentage')
        plt.title('Error Percentage')
        plt.xticks(rotation=90)
        # Set y-axis limits based on the maximum percentage value
        max_percentage = max(map(float, percentages))
        plt.ylim(0, max_percentage + 10)  # Add some padding to ensure readability
        
        plt.tight_layout()
        plt.show()

