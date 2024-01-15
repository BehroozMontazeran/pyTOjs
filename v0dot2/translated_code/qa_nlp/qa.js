// npm install axios csv-parser fs @transformers/direct bert-tokenizer bert-model @transformers/direct bert-question-answering

const fs = require('fs');
const { BertTokenizer, BertModel, BertForQuestionAnswering } = require('@transformers/direct');

// Conbine different columns of the dataset into one column
const axios = require('axios');
const csv = require('csv-parser');
const { createWriteStream } = require('fs');
const { pipeline } = require('stream');
const { promisify } = require('util');
const streamPipeline = promisify(pipeline);

// Read the original CSV file
const df_part = await axios.get('articles.csv');

// Create a new object with the desired structure
const newObject = {};

// Combine the information into a single property
newObject['Combined_Info'] = (
    'Title: ' + df_part['TI'].fill('None') + '\n' +
    'Abstract: ' + df_part['AB'].fill('None') + '\n' +
    'Authors: ' + df_part['FAU'].fill('None') + '\n' +
    'Data of Publication: ' + df_part['DP'].fill('None') + '\n' +
    'Terms or keywords associated with the article: ' + df_part['OT'].fill('None') + '\n' +
    'Journal Title: ' + df_part['JT'].fill('None') + '\n' +
    'Medical subject headings: ' + df_part['MH'].fill('None')
);

// Save the new object to a CSV file
fs.writeFileSync('combined_data.csv', newObject);

// Function to split CSV
async function splitCsv(inputCsv, outputPrefix, chunkSize) {
    const chunks = [];

    // Read the large CSV file into an array of objects
    await fs.createReadStream(inputCsv)
        .pipe(csv())
        .on('data', (chunk) => chunks.push(chunk))
        .on('end', async () => {
            // Determine the number of chunks needed
            const numChunks = Math.ceil(chunks.length / chunkSize);

            // Split the array into chunks
            for (let i = 0; i < numChunks; i++) {
                const chunk = chunks.slice(i * chunkSize, (i + 1) * chunkSize);
                const outputCsv = `${outputPrefix}_${i + 1}.csv`;

                // Save each chunk as a separate CSV file
                await streamPipeline(
                    new ReadableStream(JSON.stringify(chunk)),
                    fs.createWriteStream(outputCsv)
                );

                console.log(`Chunk ${i + 1} saved to ${outputCsv}`);
            }
        });
}

// Example usage
const inputCsvPath = 'data_1.csv';  // Replace with the path to your large CSV file
const outputPrefix = 'sub_data';  // Prefix for the output CSV files
const chunkSize = 1000;  // Number of rows per chunk

await splitCsv(inputCsvPath, outputPrefix, chunkSize);

// Embedding the abstracts using BERT and saving them to a file

// Load pre-trained BERT model and tokenizer
const tokenizer = await BertTokenizer.fromPretrained('bert-base-uncased');
const model = await BertModel.fromPretrained('bert-base-uncased');

// Tokenize and encode the abstracts
async function encodeAbstractsSlidingWindow(abstracts, windowSize = 512, stride = 256) {
    const encodedAbstracts = [];

    for (const abstract of abstracts) {
        const tokens = await tokenizer.tokenize(abstract);
        const totalLength = tokens.length;

        // Determine the number of overlapping windows
        const numWindows = Math.floor((totalLength - windowSize) / stride) + 1;

        for (let i = 0; i < numWindows * stride; i += stride) {
            // Extract a window of tokens
            const windowTokens = tokens.slice(i, i + windowSize);

            // Convert tokens back to a string
            const windowText = await tokenizer.convertTokensToString(windowTokens);

            // Tokenize and encode the window
            const inputs = await tokenizer(windowText, { return_tensors: 'pt', padding: true, truncation: true });
            const outputs = await model(inputs);

            encodedAbstracts.push(outputs.last_hidden_state.mean(1));
        }
    }

    if (!encodedAbstracts.length) {
        console.log('No encoded abstracts found.');
    }

    return torch.cat(encodedAbstracts, 0);
}

// Function to save encoded abstracts
async function saveEncodedAbstracts(encodedAbstracts, filename) {
    await torch.save(encodedAbstracts, filename);
}

// Function to load encoded abstracts
async function loadEncodedAbstracts(filename) {
    return await torch.load(filename);
}

// Example: Load, encode, and save each part separately
for (let i = 1; i <= 10; i++) {
    const filePath = `sub_data_${i}.csv`;
    const dfPart = await fs.readFileSync(filePath);

    // Encode abstracts
    const encodedAbstractsPart = await encodeAbstractsSlidingWindow(dfPart['Combined_Info']);

    // Save encoded abstracts
    await saveEncodedAbstracts(encodedAbstractsPart, `encoded_data_part_${i}.pt`);
}

// Load and concatenate encoded abstracts from all parts
const encodedAbstractsParts = [];
for (let i = 1; i <= 10; i++) {
    const encodedAbstractsPart = await loadEncodedAbstracts(`encoded_data_part_${i}.pt`);
    encodedAbstractsParts.push(encodedAbstractsPart);
}

// Concatenate the parts
const encodedAbstracts = torch.cat(encodedAbstractsParts, 0);

// Save the encoded_abstracts tensor
await torch.save(encodedAbstracts, 'encoded_data.pt');

// Load pre-trained BERT model and tokenizer
const qaModel = await BertForQuestionAnswering.fromPretrained('bert-large-uncased-whole-word-masking-finetuned-squad');
const qaTokenizer = await BertTokenizer.fromPretrained('bert-large-uncased-whole-word-masking-finetuned-squad');

// Tokenize and encode the abstracts
async function encodeAbstractsSlidingWindow(abstracts, windowSize = 512, stride = 256) {
    const encodedAbstracts = [];

    for (const abstract of abstracts) {
        const tokens = await tokenizer.tokenize(abstract);
        const totalLength = tokens.length;

        // Determine the number of overlapping windows
        const numWindows = Math.floor((totalLength - windowSize) / stride) + 1;

        for (let i = 0; i < numWindows * stride; i += stride) {
            // Extract a window of tokens
            const windowTokens = tokens.slice(i, i + windowSize);

            // Convert tokens back to a string
            const windowText = await tokenizer.convertTokensToString(windowTokens);

            // Tokenize and encode the window
            const inputs = await tokenizer(windowText, { return_tensors: 'pt', padding: true, truncation: true });
            const outputs = await model(inputs);

            encodedAbstracts.push(outputs.last_hidden_state.mean(1));
        }
    }

    if (!encodedAbstracts.length) {
        console.log('No encoded abstracts found.');
    }

    return torch.cat(encodedAbstracts, 0);
}

// Function to load encoded abstracts
async function loadEncodedAbstracts(filename) {
    return await torch.load(filename);
}

// Function to retrieve top k similar abstracts
async function retrieveTopKAbstracts(query, abstracts, df, k = 5) {
    // Encode the query using the sliding window approach (as before)
    const queryEmbedding = await encodeAbstractsSlidingWindow([query]);

    // Calculate cosine similarity between the query and encoded abstracts
    const similarities = cosine_similarity(queryEmbedding, abstracts);

    // Get the indices of the top k most similar abstracts
    const topKIndices = similarities.argsort()[0].slice(-k).reverse();

    if (!topKIndices.length) {
        console.log('No matching abstracts found.');
        return [];
    }

    // Print some information for debugging
    console.log('Top k PMIDs:', df.index[topKIndices].tolist());
    console.log('Abstract lengths:', df.index[topKIndices].map(pmid => df.loc[pmid, 'Combined_Info'].length).tolist());

    return topKIndices;
}

// Function to generate answers using the QA model
async function generateAnswers(question, abstracts, df) {
    const answers = [];

    for (const index of abstracts) {
        // Get the PMID
        const pmid = df.index[index];

        // Get the abstract text
        const abstractText = df.loc[pmid, 'Combined_Info'];

        // Tokenize and encode the question and abstract
        const inputs = await qaTokenizer(question, abstractText, { return_tensors: 'pt', max_length: 512, truncation: true });

        // Perform inference with the QA model
        const outputs = await qaModel(inputs);

        // Get the predicted answer
        const answerStart = torch.argmax(outputs.start_logits);
        const answerEnd = torch.argmax(outputs.end_logits) + 1;
        const answer = await qaTokenizer.convertTokensToString(qaTokenizer.convertIdsToTokens(inputs.input_ids[0].slice(answerStart, answerEnd)));

        answers.push(answer);
    }

    return answers;
}

// Using PMID as the index column
const dfPart = await fs.readFileSync('data_1.csv');
// const dfPart = await fs.readFileSync('articles.csv', { index_col: 'PMID', usecols: ['TI', 'AB', 'FAU', 'DP', 'OT', 'JT', 'MH'] });

// Example usage
const encodedAbstracts = await loadEncodedAbstracts('encoded_data.pt');
const question = 'what is Artificial Intelligence?';
const topKAbstracts = await retrieveTopKAbstracts(question, encodedAbstracts, dfPart, 5);

// Print the top 5 similar abstracts
console.log('Top 5 Similar Abstracts:');
for (const index of topKAbstracts) {
    const pmid = dfPart.index[index];
    console.log('PMID:', pmid);
    console.log('Abstract:', dfPart.loc[pmid, 'Combined_Info']);
}

const answers = await generateAnswers(question, topKAbstracts, dfPart);

// Display the generated answers
console.log('\nGenerated Answers:');
for (const answer of answers) {
    console.log(answer);
}
