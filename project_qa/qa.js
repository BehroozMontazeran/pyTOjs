// Conbine different columns of the dataset into one column

const pandas = require('pandas-js');
const torch = require('torch-js');
// Commenting out the next two lines since transformers is not available in JS
// const { BertTokenizer, BertModel, BertForQuestionAnswering } = require('transformers-js');
const { cosine_similarity } = require('sklearn-metrics-js');
const { tqdm } = require('tqdm-js');

// Read the original CSV file
const df_part = pandas.read_csv('articles.csv', { index_col: 'PMID', usecols: ['PMID', 'TI', 'AB', 'FAU', 'DP', 'OT', 'JT', 'MH'] });

// Create a new DataFrame with the desired structure
const new_df = pandas.DataFrame.empty(df_part.index);

// Combine the information into a single column
new_df['Combined_Info'] = (
    'Title: ' + df_part['TI'].fillna('None') + '\n' +
    'Abstract: ' + df_part['AB'].fillna('None') + '\n' +
    'Authors: ' + df_part['FAU'].fillna('None') + '\n' +
    'Data of Publication: ' + df_part['DP'].fillna('None') + '\n' +
    'Terms or keywords associated with the article: ' + df_part['OT'].fillna('None') + '\n' +
    'Journal Title: ' + df_part['JT'].fillna('None') + '\n' +
    'Medical subject headings: ' + df_part['MH'].fillna('None')
);

// Save the new DataFrame to a CSV file
new_df.to_csv('combined_data.csv');

function split_csv(input_csv, output_prefix, chunk_size) {
    // Read the large CSV file into a pandas DataFrame
    const df = pandas.read_csv(input_csv);

    // Determine the number of chunks needed
    const num_chunks = Math.floor(df.length / chunk_size) + 1;

    // Split the DataFrame into chunks
    const chunks = [];
    for (let i = 0; i < num_chunks; i++) {
        chunks.push(df.slice(i * chunk_size, (i + 1) * chunk_size));
    }

    // Save each chunk as a separate CSV file
    for (let i = 0; i < chunks.length; i++) {
        const output_csv = `${output_prefix}_${i + 1}.csv`;
        pandas.to_csv(chunks[i], output_csv, { index: false });
        console.log(`Chunk ${i + 1} saved to ${output_csv}`);
    }
}

// Example usage
const input_csv_path = 'data_1.csv';  // Replace with the path to your large CSV file
const output_prefix = 'sub_data';  // Prefix for the output CSV files
const chunk_size = 1000;  // Number of rows per chunk

split_csv(input_csv_path, output_prefix, chunk_size);

// Embedding the abstracts using BERT and saving them to a file

// Load pre-trained BERT model and tokenizer
// Commenting out the next two lines since transformers is not available in JS
// const tokenizer = BertTokenizer.from_pretrained('bert-base-uncased');
// const model = BertModel.from_pretrained('bert-base-uncased');

// Tokenize and encode the abstracts
function encode_abstracts_sliding_window(abstracts, window_size = 512, stride = 256) {
    const encoded_abstracts = [];

    for (let abstract of tqdm(abstracts, "Encoding Abstracts", "abstract")) {
        const tokens = tokenizer.tokenize(abstract);
        const total_length = tokens.length;

        // Determine the number of overlapping windows
        const num_windows = Math.floor(Math.abs(total_length - window_size) / stride) + 1;

        for (let i = 0; i < num_windows * stride; i += stride) {
            // Extract a window of tokens
            const window_tokens = tokens.slice(i, i + window_size);

            // Convert tokens back to a string
            const window_text = window_tokens.join(' ');

            // Tokenize and encode the window
            const inputs = tokenizer(window_text, { return_tensors: "pt", padding: true, truncation: true });
            const outputs = model(inputs);

            encoded_abstracts.push(outputs.last_hidden_state.mean(dim=1));
        }
    }

    if (encoded_abstracts.length === 0) {
        console.log("No encoded abstracts found.");
    }

    return torch.cat(encoded_abstracts, { dim: 0 });
}

// Function to save encoded abstracts
function save_encoded_abstracts(encoded_abstracts, filename) {
    torch.save(encoded_abstracts, filename);
}

// Function to load encoded abstracts
function load_encoded_abstracts(filename) {
    return torch.load(filename);
}

// Example: Load, encode, and save each part separately
for (let i = 1; i <= 10; i++) {
    const file_path = `sub_data_${i}.csv`;
    const df_part1 = pandas.read_csv(file_path);

    // Encode abstracts
    const encoded_abstracts_part = encode_abstracts_sliding_window(df_part1['Combined_Info']);

    // Save encoded abstracts
    save_encoded_abstracts(encoded_abstracts_part, `encoded_data_part_${i}.pt`);
}

// Load and concatenate encoded abstracts from all parts
const encoded_abstracts_parts = [];
for (let i = 1; i <= 10; i++) {
    const encoded_abstracts_part1 = load_encoded_abstracts(`encoded_data_part_${i}.pt`);
    encoded_abstracts_parts.push(encoded_abstracts_part1);
}

// Concatenate the parts
const encoded_abstracts1 = torch.cat(encoded_abstracts_parts, { dim: 0 });

// Save the encoded_abstracts tensor
torch.save(encoded_abstracts1, 'encoded_data.pt');

// Load pre-trained BERT model and tokenizer
// Commenting out the next two lines since transformers is not available in JS
// const qa_model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad');
// const qa_tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad');

// Function to retrieve top k similar abstracts
function retrieve_top_k_abstracts(query, abstracts, df, k = 5) {
    // Encode the query using the sliding window approach (as before)
    const query_embedding = encode_abstracts_sliding_window([query]);

    // Calculate cosine similarity between the query and encoded abstracts
    const similarities = cosine_similarity(query_embedding, abstracts);

    // Get the indices of the top k most similar abstracts
    const top_k_indices = similarities.argsort()[0].slice(-k).reverse();

    if (top_k_indices.length === 0) {
        console.log("No matching abstracts found.");
        return [];
    }

    // Print some information for debugging
    console.log(`Top k PMIDs: ${df.index[top_k_indices].tolist()}`);
    console.log(`Abstract lengths: ${top_k_indices.map((index) => df.iloc(0)[index]['Combined_Info'].length)}`);

    return top_k_indices;
}

// Function to generate answers using the QA model
function generate_answers(question, abstracts, df) {
    const answers = [];

    for (let index of abstracts) {
        // Get the PMID
        const pmid = df.index[index];

        // Get the abstract text
        const abstract_text = df.iloc(0)[index]['Combined_Info'];

        // Tokenize and encode the question and abstract
        const inputs = qa_tokenizer(question, abstract_text, { return_tensors: "pt", max_length: 512, truncation: true });

        // Perform inference with the QA model
        const outputs = qa_model(inputs);

        // Get the predicted answer
        const answer_start = torch.argmax(outputs.start_logits);
        const answer_end = torch.argmax(outputs.end_logits) + 1;
        const answer = qa_tokenizer.convert_ids_to_tokens(inputs.input_ids[0].slice(answer_start, answer_end)).join(' ');

        answers.push(answer);
    }

    return answers;
}

// Using PMID as the index column
const df_part3 = pandas.read_csv('data_1.csv', { index_col: 'PMID' });

// Example usage
const encoded_abstracts = load_encoded_abstracts('encoded_data.pt');
const question = "what is Artificial Intelligence?";
const top_k_abstracts = retrieve_top_k_abstracts(question, encoded_abstracts, df_part3, 5);

// Print the top 5 similar abstracts
console.log("Top 5 Similar Abstracts:");
for (let index of top_k_abstracts) {
    const pmid = df_part3.index[index];
    console.log(`PMID: ${pmid}`);
    console.log(`Abstract: ${df_part3.iloc(0)[index]['Combined_Info']}`);
}

const answers = generate_answers(question, top_k_abstracts, df_part3);

// Display the generated answers
console.log("\nGenerated Answers:");
for (let answer of answers) {
    console.log(answer);
}