import os

def add_sentiment_to_library(new_sentiment):
    file_path = 'NRC-Emotion-Lexicon-Wordlevel-v0.92.txt'

    updated_lines = []
    
    with open(file_path, 'r') as file:
        for line in file:
            word, emotion, value = line.strip().split('\t')
            updated_lines.append(line.strip())
            if emotion == 'volatility':  # Assuming this is the last emotion in the list. Update with the current last word
                updated_lines.append(f"{word}\t{new_sentiment}\t0")

    with open(file_path, 'w') as file:
        for updated_line in updated_lines:
            file.write(f"{updated_line}\n")

    print(f"Added new sentiment '{new_sentiment}' to the library.")

if __name__ == "__main__":
    new_sentiment = input("Enter the new sentiment to add: ")
    add_sentiment_to_library(new_sentiment)