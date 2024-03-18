""" OpenAI API connector
"""

import os
from openai import OpenAI
from core.log import Log

class OpenAIConnector:
    """Set a connection to openAI via API"""
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.log = Log(self.__class__.__name__)
        if not self.api_key:
            raise ValueError("OpenAI API key is missing. Set the OPENAI_API_KEY environmental variable.")

        self.client = OpenAI(api_key=self.api_key)
        self.log.info("OpenAI API connection established")

    def get_completions(self, messages):
        """Send a message to GPT 3.5"""
        try:
        # self.log.info("Sending messages to GPT 3.5")
            return self.client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
        except Exception as e:
            self.log.error(f"Error in get_completions: {e}")
            return None