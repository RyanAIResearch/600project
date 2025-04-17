import os
import re
import string
from bs4 import BeautifulSoup
from collections import defaultdict, Counter
import heapq

class TrieNode:
    """Node in a compressed trie data structure"""
    def __init__(self):
        self.children = {}  # Dictionary of child nodes
        self.is_end_of_word = False  # Flag to mark end of a word
        self.occurrence_list_index = -1  # Index to the occurrence list array

class Trie:
    """Compressed trie for storing index terms"""
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word, occurrence_list_index):
        """Insert a word into the trie with its occurrence list index"""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.occurrence_list_index = occurrence_list_index
    
    def search(self, word):
        """Search for a word in the trie, return its occurrence list index"""
        node = self.root
        for char in word:
            if char not in node.children:
                return -1  # Word not found
            node = node.children[char]
        
        # Check if we found a complete word
        if node.is_end_of_word:
            return node.occurrence_list_index
        return -1  # Word not found

class SearchEngine:
    """Search engine implementation based on inverted index and trie"""
    def __init__(self):
        # Store page content and metadata
        self.pages = {}  # {url: content}
        self.page_titles = {}  # {url: title}
        
        # Inverted index components
        self.inverted_index = defaultdict(list)  # Temporary structure during building
        self.trie = Trie()  # For efficient term lookup
        self.occurrence_lists = []  # Array storing occurrence lists
        
        # Term frequency data for ranking
        self.word_frequencies = {}  # {url: {word: frequency}}
        
        # Stop words to exclude from indexing
        self.stop_words = self.load_stop_words()
        
        # Statistics
        self.stats = {
            "total_pages": 0,
            "total_words": 0,
            "unique_words": 0
        }
    
    def load_stop_words(self):
        """Load a list of common stop words to exclude from the index"""
        # Common English stop words
        stop_words = set([
            "a", "an", "the", "and", "or", "but", "is", "are", "was", "were",
            "in", "on", "at", "to", "for", "with", "by", "about", "against",
            "between", "into", "through", "during", "before", "after", "above",
            "below", "from", "up", "down", "of", "off", "over", "under", "again",
            "further", "then", "once", "here", "there", "when", "where", "why",
            "how", "all", "any", "both", "each", "few", "more", "most", "other",
            "some", "such", "no", "nor", "not", "only", "own", "same", "so",
            "than", "too", "very", "s", "t", "can", "will", "just", "don",
            "should", "now", "he", "she", "it", "they", "we", "you", "i", "me", "my"
        ])
        return stop_words
    
    def crawl_directory(self, directory):
        """Process all HTML files in the given directory"""
        print(f"Crawling directory: {directory}")
        for filename in os.listdir(directory):
            if filename.endswith('.html'):
                filepath = os.path.join(directory, filename)
                url = f"file://{filepath}"
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                self.pages[url] = content
                self.process_page(url, content)
                self.stats["total_pages"] += 1
        
        # After processing all pages, build the final index structures
        self.build_index()
        
        # Update statistics
        self.stats["unique_words"] = len(self.occurrence_lists)
        print(f"Indexed {self.stats['total_pages']} pages with {self.stats['unique_words']} unique terms")
    
    def process_page(self, url, content):
        """Extract text, links, and update inverted index for a page"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract page title
        title_tag = soup.find('title')
        if title_tag:
            self.page_titles[url] = title_tag.text.strip()
        else:
            self.page_titles[url] = url.split('/')[-1]
        
        # Extract text content
        text = soup.get_text()
        
        # Tokenize and count word frequencies
        words = self.tokenize(text)
        word_counts = Counter(words)
        self.word_frequencies[url] = word_counts
        
        # Update inverted index
        for word in set(words):  # Use set to process each unique word once
            if word not in self.stop_words and len(word) > 1:
                self.inverted_index[word].append(url)
                self.stats["total_words"] += 1
    
    def tokenize(self, text):
        """Convert text to lowercase, remove punctuation, and split into words"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        translator = str.maketrans('', '', string.punctuation)
        text = text.translate(translator)
        
        # Split into words and filter out stop words and short terms
        words = [word for word in text.split() if word not in self.stop_words and len(word) > 1]
        
        return words
    
    def build_index(self):
        """Build compressed trie and organized occurrence lists"""
        print("Building index structures...")
        
        # Sort words for consistent indexing
        sorted_words = sorted(self.inverted_index.keys())
        
        # Build occurrence lists array and trie
        for i, word in enumerate(sorted_words):
            # Sort the occurrence list for efficient intersection
            occurrence_list = sorted(self.inverted_index[word])
            self.occurrence_lists.append(occurrence_list)
            
            # Add word to trie with index to its occurrence list
            self.trie.insert(word, i)
    
    def search(self, query):
        """Search for pages containing all query terms"""
        # Tokenize and filter the query
        query_terms = [term for term in self.tokenize(query) if term not in self.stop_words]
        
        if not query_terms:
            return []  # Empty query or only stop words
        
        # For single term query
        if len(query_terms) == 1:
            word = query_terms[0]
            list_index = self.trie.search(word)
            if list_index == -1:
                return []  # Term not found
            return self.occurrence_lists[list_index]
        
        # For multiple term query, find intersection
        result_lists = []
        for word in query_terms:
            list_index = self.trie.search(word)
            if list_index == -1:
                return []  # One term not found, no results
            result_lists.append(self.occurrence_lists[list_index])
        
        # Compute intersection of all occurrence lists
        intersection = set(result_lists[0])
        for result_list in result_lists[1:]:
            intersection &= set(result_list)
        
        return list(intersection)
    
    def rank_results(self, query, results):
        """Rank search results by relevance"""
        query_terms = [term for term in self.tokenize(query) if term not in self.stop_words]
        scores = {}
        
        for url in results:
            score = 0
            page_word_counts = self.word_frequencies[url]
            
            for term in query_terms:
                # Add score based on term frequency
                term_freq = page_word_counts.get(term, 0)
                score += term_freq
                
                # Bonus for terms in title (if available)
                if url in self.page_titles and term in self.page_titles[url].lower():
                    score += 2  # Bonus for term in title
            
            scores[url] = score
        
        # Sort by score in descending order
        ranked_results = [url for url, score in 
                         sorted(scores.items(), key=lambda x: x[1], reverse=True)]
        
        return ranked_results
    
    def query(self, query_string):
        """Process a query and return ranked results"""
        print(f"Processing query: '{query_string}'")
        
        # Find pages containing all query terms
        results = self.search(query_string)
        
        if not results:
            return []
        
        # Rank results by relevance
        ranked_results = self.rank_results(query_string, results)
        
        return ranked_results
    
    def display_results(self, query, results):
        """Format and display search results"""
        if not results:
            print("No results found.")
            return
        
        print(f"Found {len(results)} results:")
        for i, url in enumerate(results, 1):
            # Display page title or filename
            title = self.page_titles.get(url, url.split('/')[-1])
            print(f"{i}. {title}")
            
            # Show relevance information (term frequencies)
            page_frequencies = self.word_frequencies[url]
            query_terms = [term for term in self.tokenize(query) if term not in self.stop_words]
            
            for term in query_terms:
                if term in page_frequencies:
                    print(f"   '{term}' appears {page_frequencies[term]} times")
            print()

# Main execution
if __name__ == "__main__":
    search_engine = SearchEngine()
    
    # Configure the directory containing HTML files
    pages_dir = "input_pages"
    
    # Check if directory exists
    if not os.path.exists(pages_dir):
        os.makedirs(pages_dir)
        print(f"Created directory '{pages_dir}'. Please add HTML files before running again.")
        exit(1)
    
    # Crawl pages directory
    search_engine.crawl_directory(pages_dir)
    
    # Interactive query loop
    print("\nSearch engine initialized. Enter queries (or 'exit' to quit):")
    while True:
        query = input("\nSearch: ")
        if query.lower() == 'exit':
            break
        
        results = search_engine.query(query)
        search_engine.display_results(query, results)