
from tiktoken import TokenCounter

class Analyzer:
    def __init__(self):
        self.token_counter = TokenCounter()

    def analyze(self, text):
        self.token_counter.count_tokens(text)

    def get_token_count(self):
        return self.token_counter.get_token_count()


text = "Your input text goes here."

# Create a token counter and count tokens
token_counter = TokenCounter()
token_counter.count_tokens(text)

# Get the total token count
total_tokens = token_counter.get_token_count()

print(f"Total tokens: {total_tokens}")
