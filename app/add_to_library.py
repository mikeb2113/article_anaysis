def add_word_to_library(word, library_file='NRC-Emotion-Lexicon-Wordlevel-v0.92.txt'):
    emotions = ["anger", "anticipation", "disgust", "fear", "joy", "negative", "positive", "sadness", "surprise", "trust", "volatility"]
    entry_template = "{word}\t{emotion}\t0\n"

    # Open the library file in append mode
    with open(library_file, 'a') as file:
        for emotion in emotions:
            file.write(entry_template.format(word=word, emotion=emotion))
    
    print(f"Word '{word}' has been added to the library.")

if __name__ == "__main__":
    word = input("Enter the word you want to add to the library: ").strip()
    add_word_to_library(word)