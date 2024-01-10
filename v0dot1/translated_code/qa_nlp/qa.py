# Conbine different columns of the dataset into one column

import pandas as pd
import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from transformers import BertForQuestionAnswering, BertTokenizer
from sklearn.metrics.pairwise import cosine_similarity

# Read the original CSV file
df_part = pd.read_csv('articles.csv', index_col='PMID', usecols=['PMID', 'TI', 'AB', 'FAU', 'DP', 'OT', 'JT', 'MH'])

# Create a new DataFrame with the desired structure
new_df = pd.DataFrame(index=df_part.index)

# Combine the information into a single column
new_df['Combined_Info'] = (
    'Title: ' + df_part['TI'].fillna('None') + '\n' +
    'Abstract: ' + df_part['AB'].fillna('None') + '\n' +
    'Authors: ' + df_part['FAU'].fillna('None') + '\n' +
    'Data of Publication: ' + df_part['DP'].fillna('None') + '\n' +
    'Terms or keywords associated with the article: ' + df_part['OT'].fillna('None') + '\n' +
    'Journal Title: ' + df_part['JT'].fillna('None') + '\n' +
    'Medical subject headings: ' + df_part['MH'].fillna('None')
)

# Save the new DataFrame to a CSV file
new_df.to_csv('combined_data.csv')

def split_csv(input_csv, output_prefix, chunk_size):
    # Read the large CSV file into a pandas DataFrame
    df = pd.read_csv(input_csv)

    # Determine the number of chunks needed
    num_chunks = (len(df) // chunk_size) + 1

    # Split the DataFrame into chunks
    chunks = [df[i * chunk_size:(i + 1) * chunk_size] for i in range(num_chunks)]

    # Save each chunk as a separate CSV file
    for i, chunk in enumerate(chunks):
        output_csv = f"{output_prefix}_{i + 1}.csv"
        chunk.to_csv(output_csv, index=False)
        print(f"Chunk {i + 1} saved to {output_csv}")

# Example usage
input_csv_path = 'data_1.csv'  # Replace with the path to your large CSV file
output_prefix = 'sub_data'  # Prefix for the output CSV files
chunk_size = 1000  # Number of rows per chunk

split_csv(input_csv_path, output_prefix, chunk_size)
# Embedding the abstracts using BERT and saving them to a file


# Load pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Tokenize and encode the abstracts
def encode_abstracts_sliding_window(abstracts, window_size=512, stride=256):
    encoded_abstracts = []

    for abstract in tqdm(abstracts, desc="Encoding Abstracts", unit="abstract"):
        tokens = tokenizer.tokenize(abstract)
        total_length = len(tokens)

        # Determine the number of overlapping windows
        num_windows = abs(total_length - window_size) // stride + 1

        for i in range(0, num_windows * stride, stride):
            # Extract a window of tokens
            window_tokens = tokens[i:i + window_size]

            # Convert tokens back to a string
            window_text = tokenizer.convert_tokens_to_string(window_tokens)

            # Tokenize and encode the window
            inputs = tokenizer(window_text, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                outputs = model(**inputs)

            encoded_abstracts.append(outputs.last_hidden_state.mean(dim=1))

    if not encoded_abstracts:
        print("No encoded abstracts found.")
    return torch.cat(encoded_abstracts, dim=0)


# Function to save encoded abstracts
def save_encoded_abstracts(encoded_abstracts, filename):
    torch.save(encoded_abstracts, filename)

# Function to load encoded abstracts
def load_encoded_abstracts(filename):
    return torch.load(filename)

# Example: Load, encode, and save each part separately
for i in tqdm(range(1, 11), desc="Processing Parts", unit="part"):
    file_path = f'sub_data_{i}.csv'
    df_part = pd.read_csv(file_path)

    # Encode abstracts
    encoded_abstracts_part = encode_abstracts_sliding_window(df_part['Combined_Info'])

    # Save encoded abstracts
    save_encoded_abstracts(encoded_abstracts_part, f'encoded_data_part_{i}.pt')

# Load and concatenate encoded abstracts from all parts
encoded_abstracts_parts = []
for i in tqdm(range(1, 11), desc="Loading Parts", unit="part"):
    encoded_abstracts_part = load_encoded_abstracts(f'encoded_data_part_{i}.pt')
    encoded_abstracts_parts.append(encoded_abstracts_part)

# Concatenate the parts
encoded_abstracts = torch.cat(encoded_abstracts_parts, dim=0)

# Save the encoded_abstracts tensor
torch.save(encoded_abstracts, 'encoded_data.pt')

# Load pre-trained BERT model and tokenizer
qa_model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
qa_tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')


# Tokenize and encode the abstracts
def encode_abstracts_sliding_window(abstracts, window_size=512, stride=256):
    encoded_abstracts = []

    for abstract in tqdm(abstracts, desc="Encoding Abstracts", unit="abstract"):
        tokens = tokenizer.tokenize(abstract)
        total_length = len(tokens)

        # Determine the number of overlapping windows
        num_windows = abs(total_length - window_size) // stride + 1

        for i in range(0, num_windows * stride, stride):
            # Extract a window of tokens
            window_tokens = tokens[i:i + window_size]

            # Convert tokens back to a string
            window_text = tokenizer.convert_tokens_to_string(window_tokens)

            # Tokenize and encode the window
            inputs = tokenizer(window_text, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                outputs = model(**inputs)

            encoded_abstracts.append(outputs.last_hidden_state.mean(dim=1))

    if not encoded_abstracts:
        print("No encoded abstracts found.")
    return torch.cat(encoded_abstracts, dim=0)

# Function to load encoded abstracts
def load_encoded_abstracts(filename):
    return torch.load(filename)

# Function to retrieve top k similar abstracts
def retrieve_top_k_abstracts(query, abstracts, df, k=5):
    # Encode the query using the sliding window approach (as before)
    query_embedding = encode_abstracts_sliding_window([query])
    
    # Calculate cosine similarity between the query and encoded abstracts
    similarities = cosine_similarity(query_embedding, abstracts)
    
    # Get the indices of the top k most similar abstracts
    top_k_indices = similarities.argsort()[0, -k:][::-1]

    if len(top_k_indices) == 0:
        print("No matching abstracts found.")
        return []

    # Print some information for debugging
    print("Top k PMIDs:", df.index[top_k_indices].tolist())
    print("Abstract lengths:", [len(df.loc[pmid, 'Combined_Info']) for pmid in df.index[top_k_indices]])

    return top_k_indices


# Function to generate answers using the QA model
def generate_answers(question, abstracts, df):
    answers = []

    for index in abstracts:
        # Get the PMID
        pmid = df.index[index]

        # Get the abstract text
        abstract_text = df.loc[pmid, 'Combined_Info']

        # Tokenize and encode the question and abstract
        inputs = qa_tokenizer(question, abstract_text, return_tensors="pt", max_length=512, truncation=True)
        
        # Perform inference with the QA model
        with torch.no_grad():
            outputs = qa_model(**inputs)

        # Get the predicted answer
        answer_start = torch.argmax(outputs.start_logits)
        answer_end = torch.argmax(outputs.end_logits) + 1
        answer = qa_tokenizer.convert_tokens_to_string(qa_tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end]))

        answers.append(answer)

    return answers

# Using PMID as the index column
df_part = pd.read_csv('data_1.csv', index_col='PMID')
# df_part = pd.read_csv('articles.csv', index_col='PMID', usecols=['TI', 'AB', 'FAU', 'DP', 'OT', 'JT', 'MH'])

# Example usage
encoded_abstracts = load_encoded_abstracts('encoded_data.pt')
question = "what is Artificial Intelligence?"
top_k_abstracts = retrieve_top_k_abstracts(question, encoded_abstracts, df_part, k=5)

# Print the top 5 similar abstracts
print("Top 5 Similar Abstracts:")
for index in top_k_abstracts:
    pmid = df_part.index[index]
    print("PMID:", pmid)
    print("Abstract:", df_part.loc[pmid, 'Combined_Info'])

answers = generate_answers(question, top_k_abstracts, df_part)

# Display the generated answers
print("\nGenerated Answers:")
for answer in answers:
    print(answer)