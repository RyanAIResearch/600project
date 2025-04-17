# Search Engine Implementation

## Overview

This project implements the simplified search engine described in Section 23.6 of the textbook. It processes a small site’s HTML pages, builds an inverted index backed by a compressed trie, and lets users issue single‑ or multi‑keyword queries to retrieve and rank matching pages.

## Data Structures Used

1. **Inverted Index**

   - A `dict[str, list[str]]` mapping each index term to the list of document URLs that contain it.
2. **Compressed Trie**

   - A character‐by‐character trie whose external (terminal) nodes store an integer pointer into the occurrence‑list array.
   - Enables O(m) lookup of any m‑character keyword.
3. **Occurrence Lists**

   - An array of posting lists (`List[List[str]]`), one per unique term.
   - Each list is sorted by URL to support fast intersection.

## Algorithms Implemented

1. **Web Crawler**

   - Reads all `.html` files from a directory.
   - Uses BeautifulSoup to extract `<title>`, text content, and hyperlinks.
2. **Indexing Process**

   - Tokenizes page text to lowercase words, strips punctuation, filters out stop words and very short tokens.
   - Records term frequencies per page and appends each page’s URL to that term’s posting list.
3. **Build Phase**

   - Sorts all unique terms, moves each posting list into the occurrence‑lists array, and inserts the term into the trie with its list index.
4. **Query Processing**

   - Tokenizes a user query identically to page text.
   - For each term, looks up its posting‑list index via the trie in O(m).
   - If multiple terms, computes the intersection of their sorted posting lists.
5. **Ranking Algorithm**

   - Scores each result by summing term frequencies in the page.
   - Awards a small bonus if the term appears in the page’s `<title>`.
   - Returns results sorted by descending score.

## Complexity Analysis

- **Query Time**

  - Trie lookup for one m‑character term: O(m)
  - Intersection of k posting lists of lengths L₁,…,Lₖ: O(∑₁ᵏ |Lᵢ|)
  - **Total**: O(m + ∑|Lᵢ|)
- **Space**

  - Scanning and tokenizing all pages (total text length n): O(n)
  - Storing all posting‑list entries and trie nodes: O(n)

## Boundary Conditions Tested

- Empty queries
- Queries consisting only of stop words
- Queries with no matching documents
- Case‑insensitive matching (e.g. “Apple” vs. “apple”)
- Partial‑word edge cases (ensuring exact‑term lookup)
- Very large documents (multi‑MB HTML)
- Documents containing no indexable content
