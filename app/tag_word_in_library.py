def tag_word_in_library(word_to_tag):
    file_path='NRC-Emotion-Lexicon-Wordlevel-v0.92.txt'
    try:
        # Read the file content
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Tag the word
        tagged_word = f"#{word_to_tag}"
        updated_lines = []
        for line in lines:
            # Split the line into components
            parts = line.strip().split('\t')
            if parts[0] == word_to_tag:
                parts[0] = tagged_word
            updated_lines.append('\t'.join(parts) + '\n')
        
        # Write the updated content back to the file
        with open(file_path, 'w') as file:
            file.writelines(updated_lines)
        
        print(f"Successfully tagged the word '{word_to_tag}' in the library.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    file_path = 'NRC-Emotion-Lexicon-Wordlevel-v0.92.txt'
    word_to_tag = input("Enter the word you want to tag: ").strip()
    tag_word_in_library(word_to_tag)