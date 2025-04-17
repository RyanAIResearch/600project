# Search Engine Implementation

## Overview

This project implements a simplified search engine as described in Section 23.6 of the textbook. The search engine processes a collection of web pages, builds an inverted index, and allows users to search for pages containing specific keywords.

## Approach

### Data Structures Used

1. **Inverted Index** : The core data structure is an inverted index that maps words to their occurrence lists (documents containing the word).

* Implemented as a dictionary where keys are words and values are lists of document references
* Each entry in the dictionary represents a key-value pair (w, L) where:
  * w is a word (index term)
  * L is a collection of references to pages containing w

1. **Compressed Trie** : Used for efficient storage and lookup of index terms

* External nodes store indices to the occurrence lists
* Helps keep the core data structure small enough to fit in memory

1. **Occurrence Lists** : Stored in an array outside the trie

* Each list is sorted by document identifier to facilitate intersection operations

### Algorithms Implemented

1. **Web Crawler** :

* Parses HTML documents
* Extracts text content and links
* Follows links to other documents in the collection

1. **Indexing Process** :

* Tokenizes text into words
* Removes stop words (articles, prepositions, pronouns)
* Builds the inverted index and trie structure

1. **Query Processing** :

* For single keyword queries: retrieves the occurrence list directly
* For multiple keywords: computes the intersection of occurrence lists
* Sorts results by relevance ranking

1. **Ranking Algorithm** :

* Basic ranking based on term frequency (how many times query terms appear in document)
* Documents with higher frequency of query terms are ranked higher

## Complexity Analysis

* Time complexity for query processing: O(|Σ|m) where:
  * |Σ| is the size of the alphabet
  * m is the length of the pattern/query
* Space complexity: O(n) where n is the total text size

## Boundary Conditions Tested

1. Empty queries
2. Queries with only stop words
3. Queries with no matching documents
4. Case sensitivity handling
5. Partial word matches
6. Very large documents
7. Documents with no indexable content
