import numpy as np

def tokenize(sentence, token_mapping):
   # we stick to simple blank space tokenization
   tokenized = []
   for word in sentence.lower().split(" "):

        if word in token_mapping:
            tokenized.append(token_mapping[word])
        else:
            # As 0 is assigned to ',' in en_dict and EOS in fr_dict we use -1 here for unknown words.
            tokenized.append(-1)

   return tokenized

def embed(tokens, embeddings):
    """ get the embedding for the tokens in a sentence stacked in a simple matrix (sequence length, embedding size)
        tokens: tokenized sentence
        embeddings: dictionary of token to embeddings.
    """
    embed_size = embeddings.shape[1]

    # Not considering -1 word id
    embedded_tokens = [embeddings[token] for token in tokens if token != -1]
    output = np.stack(embedded_tokens)


    return output


def softmax(x, axis=0):
    """
    x: input matrix
    axis: defines which axis to compute the softmax over 0 for rows and 1 for columns
        axis=0 calculates softmax across rows which means each column sums to 1
        axis=1 calculates softmax across columns which means each row sums to 1
    """

    
    exp_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    softmax_x= exp_x / np.sum(exp_x, axis=axis, keepdims=True)
    

    return softmax_x

def calc_weights(queries, keys):
    """
    queries: queries matrix
    keys: keys matrix
    """

    # Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)).V
    d_k = keys.shape[1]
    similarity = np.dot(queries, keys.T) / np.sqrt(d_k)
    weights = softmax(similarity, axis=1)


    return weights

def attention(queries, keys, values):
    """  scaled dot-product attention
    queries: query matrix
    keys: key matrix
    value: value matrix
    """


    weights = calc_weights(queries, keys)
    attention = np.matmul(weights, values)

    return attention
