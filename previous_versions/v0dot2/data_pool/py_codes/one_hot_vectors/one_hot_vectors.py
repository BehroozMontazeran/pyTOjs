# import numpy as np

# Defining the corpus of text
corpus = [
    "The quick brown fox jumped over the lazy dog.",
    "She sells seashells by the seashore.",
    "Peter Piper picked a peck of pickled peppers."
]

# Creating a set of unique words in the corpus
uniqueWords = set()
for sentence in corpus:
    for word in sentence.split(" "):
        uniqueWords.add(word.lower())

# Create a dictionary to map each unique word to an index
wordToIdx = {}
idx = 0
for word in uniqueWords:
    wordToIdx[word] = idx
    idx += 1

# Create one_hot encoded vectors for each word in the corpus
oneHotVectors = []
for sentence in corpus:
    sentenceVectors = []
    for word in sentence.split(" "):
        vector = [0] * len(uniqueWords)
        vector[wordToIdx[word.lower()]] = 1
        sentenceVectors.append(vector)
    oneHotVectors.append(sentenceVectors)

# Print the one_hot encoded vectors for the first sentence
print("One-hot encoded vectors for the first sentence:")
for vector in oneHotVectors[2]:
    print(vector)

# Print the one-hot vectors for each unique word separately
for i, sentence in enumerate(corpus):
    print(f"Sentence {i + 1}:")
    wordsInSentence = sentence.split(" ")
    for j, word in enumerate(wordsInSentence):
        print(f"{word}: {oneHotVectors[i][j]}")
