class Link:
    def __init__(self, window_size, is_string, adjacent_words=None):
        if not is_string:
            self.__adjacent_words = adjacent_words if adjacent_words is not None else {}
        else:
            self.__adjacent_words = {word: 1 for word in (adjacent_words.split() if adjacent_words else [])}

        # Ensure window size is even for balanced traversal
        if window_size % 2 != 0:
            window_size += 1
        self.__window_size = window_size

    def add_adjacent_words(self, word, weight=1):
        """Increase the frequency count of a word in the adjacent words dictionary."""
        if word in self.__adjacent_words:
            self.__adjacent_words[word] += weight
        else:
            self.__adjacent_words[word] = weight
        
    def set_window_size(self, window_size):
        """Sets the window size and ensures it's even."""
        self.__window_size = window_size if window_size % 2 == 0 else window_size + 1

    def get_window_size(self):
        """Returns the window size."""
        return self.__window_size

    def get_adjacent_words(self):
        """Returns a copy of the adjacent words dictionary to prevent accidental modification."""
        return self.__adjacent_words.copy()

    def window_check(self, key):
        """Retrieves the words within the window around the given key."""
        keys_list = list(self.__adjacent_words.keys())  # Convert dict keys to a list for indexing

        if key not in keys_list:
            return []  # Key not found, return empty list

        idx = keys_list.index(key)
        half_window = self.__window_size // 2

        # Define window range
        start = max(0, idx - half_window)
        end = min(len(keys_list), idx + half_window + 1)

        # Ensure window size is correct by expanding if necessary
        while (end - start) < self.__window_size and start > 0:
            start -= 1
        while (end - start) < self.__window_size and end < len(keys_list):
            end += 1

        return keys_list[start:end]