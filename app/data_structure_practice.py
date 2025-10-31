import re
import string
"""
class Node:
    def __init__(self, value=None):
        self.value = value
        self.left = None
        self.right = None

class DancingLinksList:
    def __init__(self, words):
        self.head = None
        self.build_dancing_links(words)
        self.frequency_map = self.create_frequency_map()  # Initialize frequency map for weighted search

    def build_dancing_links(self, words):
        # Sort words alphabetically
        sorted_words = sorted(words)
        
        # Initialize the first node (head) and link remaining nodes
        prev = None
        for word in sorted_words:
            new_node = Node(word)
            if not self.head:
                self.head = new_node  # Set the head for the first node
            else:
                prev.right = new_node  # Link the previous node's right to the new node
                new_node.left = prev  # Link the new node's left to the previous node
            prev = new_node
        
        # Final circular linking
        if prev:
            prev.right = self.head  # Last node points back to head
            self.head.left = prev   # Head's left points back to last node

    def create_frequency_map(self):
        # Example frequency map based on letter frequency distribution in English
        return {
            'a': 0.05, 'b': 0.10, 'c': 0.15, 'd': 0.20, 'e': 0.25,
            'f': 0.30, 'g': 0.35, 'h': 0.40, 'i': 0.45, 'j': 0.50,
            'k': 0.55, 'l': 0.60, 'm': 0.65, 'n': 0.70, 'o': 0.75,
            'p': 0.80, 'q': 0.85, 'r': 0.90, 's': 0.92, 't': 0.94,
            'u': 0.96, 'v': 0.97, 'w': 0.98, 'x': 0.99, 'y': 0.995, 'z': 1.0
        }

    def size(self):
        # Calculate the size of the linked list for position estimation
        if not self.head:
            return 0
        count = 1
        current = self.head
        while current.right != self.head:
            count += 1
            current = current.right
        return count

    def weighted_search(self, word):
        # Get first letter of the word to use frequency map
        first_letter = word[0].lower()
        position_ratio = self.frequency_map.get(first_letter, 0.5)  # Default to middle if not in map
        estimated_position = int(position_ratio * self.size())  # Approximate position based on ratio

        # Move to the estimated position
        current = self.head
        for _ in range(estimated_position):
            current = current.right

        # Refine search by moving forward or backward
        while current:
            if current.value == word:
                return current
            elif current.value < word:
                current = current.right  # Move forward in the sorted list
            else:
                current = current.left   # Move backward in the sorted list
            
            # Break loop if we circle back to the head
            if current == self.head:
                break

        return None  # If word is not found

def create_word_map_from_text(text):
    # Split text into segments outside of quotes
    outside_quotes_segments = re.split(r'["“”]', text)
    cleaned_words = []
    
    # Process only segments outside quotes
    for idx, segment in enumerate(outside_quotes_segments):
        if idx % 2 == 1:
            continue  # Skip segments inside quotes
        # Extract words outside of quotes
        words = re.findall(r'\b\w+\b', segment.lower())
        cleaned_words.extend(words)
    
    # Initialize the dancing links list for fast access
    dancing_links_list = DancingLinksList(cleaned_words)
    
    return dancing_links_list

def print_word_map(dancing_links_list):
    # Check if the dancing links list is empty
    if dancing_links_list.head is None:
        print("The word map is empty.")
        return
    
    # Start at the head of the list
    current_node = dancing_links_list.head
    printed_words = set()  # Track printed nodes to avoid infinite loops in the circular list
    
    while current_node:
        # Break if we've looped back to the start
        if current_node in printed_words:
            break
        printed_words.add(current_node)
        
        # Print the current word
        print(f"Word: {current_node.value}")
        
        # Collect context words
        context_words = []
        
        # Get the previous word
        prev_node = current_node.left
        if prev_node != current_node:  # Ensure prev_node is not self-looping
            context_words.append(f"Previous: {prev_node.value}")
        else:
            context_words.append("Previous: None")
        
        # Get the next word
        next_node = current_node.right
        if next_node != current_node:  # Ensure next_node is not self-looping
            context_words.append(f"Next: {next_node.value}")
        else:
            context_words.append("Next: None")
        
        # Print context
        print("  Context:", " | ".join(context_words))
        
        # Move to the next node
        current_node = current_node.right


text1 = "In the bustling heart of the city, amidst towering skyscrapers and the hum of endless traffic, lies a hidden gem known only to a few. This quiet little café, tucked away in a narrow alley, offers refuge to weary souls seeking solace from the chaotic world outside. The walls are adorned with vibrant paintings, each telling a story of its own. There is a faint aroma of freshly ground coffee and baked pastries lingering in the air, drawing passersby in with an irresistible pull. Here, time seems to stand still as visitors lose themselves in the comfort of plush armchairs and the warmth of soft, yellow lighting. In the corner, a musician strums a guitar softly, adding a gentle rhythm to the ambiance. People come and go, but the memories created here linger long after they've left. The café is more than just a place to drink coffee; it’s a sanctuary for artists, dreamers, and wanderers alike, all sharing a common desire for peace, creativity, and connection in an increasingly busy world."
text2 = "The café is more than just a place to drink coffee; it’s a sanctuary for artists, dreamers, and wanderers alike, all sharing a common desire for peace."
text3 = "From a technical perspective, exhibits strong financial health. The company has demonstrated resilience with a Piotroski F-Score of, indicating potential in business operations despite noted insider selling transactions. However, benefits from strong financial strength indicators, such as an Altman Z-Score of, implying a low risk of bankruptcy."
map3 = create_word_map_from_text(text3)
map1 = create_word_map_from_text(text1)
map2 = create_word_map_from_text(text2)
print_word_map(map3)
"""
#For this node: left and right will represent the input's immediate surroundings in the given phrase. This will be unsorted.add()
#up and down will represent the phrases that come before and after, assuming the list was alphabetically sorted. 
#up and down will primarily be a tool for searching, while left and right will be the business end of our program. This is the improtant data
class Node:
    def __init__(self, value=None):
        self.value = value
        self.left = None
        self.right = None

def generate_ngrams(text: str, n: int) -> list[str]:
    # Remove punctuation and split text into words
    words = [''.join(char for char in word if char not in string.punctuation) for word in text.lower().split()]
    if n == 1:
        return words  # Return individual words for unigrams
    else:
        return [' '.join(words[i:i + n]) for i in range(len(words) - n + 1)]
def generate_offset_ngrams(text: str, n: int) -> list[str]:
    words = text.lower().split()
    standard_ngrams = [' '.join(words[i:i + n]) for i in range(len(words) - n + 1)]
    offset_ngrams = [' '.join(words[i+1:i + n + 1]) for i in range(len(words) - n)]
    return standard_ngrams + offset_ngrams

class QuadMap:
    def __init__(self, original_text, n):
        self.nodes = []
        self.index = {}  # Dictionary to store nodes by value for quick lookup
        self.build_quadmap(original_text, n)

    def build_quadmap(self, original_text, n):
        ngrams = generate_ngrams(original_text, n)
        
        # Create nodes for each n-gram and link them sequentially
        prev = None
        for ngram in ngrams:
            curr = Node(ngram)
            self.nodes.append(curr)
            
            # Link nodes in text order
            if prev:
                prev.right = curr
                curr.left = prev
            prev = curr
            
            # Add to index for search, handling duplicates by storing a list
            if ngram in self.index:
                self.index[ngram].append(curr)
            else:
                self.index[ngram] = [curr]

    def search_ngram(self, phrase):
        # Return the first matching node from the index, or None if not found
        return self.index.get(phrase.lower(), None)

    def print_quadmap(self):
        # Print the linked nodes in sequential order for verification
        node = self.nodes[0] if self.nodes else None
        while node:
            left_val = node.left.value if node.left else None
            right_val = node.right.value if node.right else None
            print(f"Node: {node.value}, Left: {left_val}, Right: {right_val}")
            node = node.right

def compare_phrases_with_sample(file_path: str, sample_text: str, n: int):
    # Build the quadmap for the sample text with both standard and offset n-grams
    sample_quadmap = QuadMap(sample_text, n)

    # Open the file and read phrases line by line
    with open(file_path, 'r') as file:
        for line in file:
            phrase = line.strip()
            all_ngrams = generate_offset_ngrams(phrase, n)  # Generate standard and offset n-grams
            phrase_quadmap = QuadMap(phrase, n)  # Create a quadmap for the phrase

            match_count = 0
            for ngram in all_ngrams:
                if sample_quadmap.search_ngram(ngram):
                    print(f"Match found for n-gram '{ngram}' in sample text.")
                    match_count += 1

            if match_count == 0:
                print(f"No match found for phrase: '{phrase}'")
            else:
                print(f"{match_count} matches found for phrase: '{phrase}'")

# Example usage
sample_text = """
Three Tesla insiders, including Elon Musk’s own brother, are preparing to sell about $300 million worth of Tesla (TSLA) stocks.

In Tesla’s 10Q SEC filing, the automaker disclosed that three of its board members, including chairwoman Robyn Denholm and Kimball Musk, CEO Elon Musk’s brother, have signed new arrangements to sell a lot of shares last quarter:

    On July 25, 2024, Robyn Denholm, one of our directors, adopted a Rule 10b5-1 trading arrangement for the potential sale of up to 674,345 shares of our common stock (all resulting from stock options expiring in June 2025), subject to certain conditions. The arrangement’s expiration date is June 18, 2025.
    On July 31, 2024, Kimbal Musk, one of our directors, adopted a Rule 10b5-1 trading arrangement for the potential sale of up to 152,088 shares of our common stock, subject to certain conditions. The arrangement’s expiration date is May 30, 2025.
    On August 12, 2024, Kathleen Wilson-Thompson, one of our directors, adopted a Rule 10b5-1 trading arrangement for the potential sale of up to 300,000 shares of our common stock, subject to certain conditions. The arrangement’s expiration date is February 28, 2025.

At the current price of ~$260 per share, Denholm’s planned potential sale of Tesla’s stock would be worth $175 million.

Kimball Musk’s 152,000 shares would be worth just short of $40 million, while Wilson-Thompson’s arrangement would allow her to sell about $78 million.

Denholm held only 85,000 Tesla shares as of her last report, but as the disclosure specifies, she is exercising stock options.

Tesla’s board members have received excessive compensation from shareholders, according to a lawsuit.
Top comment by Mike Dolan
Liked by 12 people

What would you have them do? They have taxes due on non-cash compensation, they truly have no idea what the price is going to be 90 days after they set up the agreement (the market can do wild things on any given day).

They are taking "timing the market" out of the equation. The SEC set up the rule for exactly this purpose - allow a highly compensated officer or director to reduce their holdings without using inside information.

What would you have them do?
View all comments

Last year, Tesla’s board members settled the lawsuit by agreeing to return over $700 million in cash and stock.
Electrek’s Take

It’s wild that they had to return over $700 million, yet three of them can still sell about $300 million worth of stock.

It’s also important to note that this situation also plays into the ongoing legal battle over Elon’s CEO compensation. A judge find it unlawful because, amongst other reasons, he was in control of the board when the deal was “negotiated”.

At the same time that they gave Elon’s $44 billion package, they also gave themselves this excessive board compensation.
"""
# Convert the text to a single line
single_line_text = sample_text.replace("\n", " ")
# Build the QuadMap for bigrams (n=2)
#quad_map = QuadMap(single_line_text, n)
#quad_map.print_quadmap()

# Search for a specific bigram
#search_phrase = "last year"
#found_nodes = quad_map.search_ngram(search_phrase)
#if found_nodes:
#    for node in found_nodes:
#        print(f"Found n-gram: {node.value}")
#else:
#    print("N-gram not found")
n = 3
compare_phrases_with_sample("positive_example.txt", single_line_text, n)

#print(alpha_sort(text_list))
