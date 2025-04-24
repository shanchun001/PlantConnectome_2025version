"""
search.py - Demonstrating how to use normalized fields for 'exact'/'alias', 
plus your original logic for 'normal', 'substring', 'non-alphanumeric', etc.
"""
import unicodedata

import re
import time
import uuid
from collections import defaultdict

from flask import request, render_template, redirect, url_for

# Mongo integration
from mongo import db

# Custom utilities
from my_cache import cache
from cytoscape import generate_cytoscape_js, process_network
from text import make_text

cache = {}
def clean_search_term(term):
    """Remove special characters while keeping meaningful spaces."""
    return re.sub(r"[^\w\s]", "", term)  # Keep only letters, numbers, and spaces
def normalize_text(text):
    return unicodedata.normalize("NFKC", text.strip().upper())


def contains_special_characters(text):
    """Check if a string contains special characters."""
    return bool(re.search(r"[!@#$%^&*()_+={}[\]:;\"'<>,.?/~`\\|-]", text))
# Example helpers
def contains_special_characters(text):
    # Customize to match your definition of "special characters".
    # As an example, we'll say anything non-alphanumeric or underscore
    # might be treated as 'special'.
    return bool(re.search(r'[^a-zA-Z0-9_ ]', text))

def clean_word(word):
    # Removes *all* non-alphanumeric/underscore chars from a given word
    # while preserving spaces (though for a "word" typically no spaces remain).
    # Adjust to your needs.
    return re.sub(r'[^a-zA-Z0-9_]', '', word)

def make_abbreviations(abbreviations, elements):
    """
    Example stub function returning an empty dict.
    """
    ab = {}
    # ... or any logic you need ...
    return ab

def make_functional_annotations(gopredict, elements):
    """
    Another stub function returning an empty dict.
    """
    fa = {}
    return fa
class Gene:
    """
    A lightweight class to store entity pairs (source/target) with metadata.
    """
    def __init__(
        self,
        id,
        idtype,
        description,
        descriptiontype,
        inter_type=None,
        publication=None,
        p_source=None,
        species=None,
        basis=None,
        source_extracted_definition=None,
        source_generated_definition=None,
        target_extracted_definition=None,
        target_generated_definition=None
    ):
        self.id = id
        self.idtype = idtype
        self.target = description
        self.targettype = descriptiontype
        self.inter_type = inter_type
        self.publication = publication
        self.p_source = p_source
        self.species = species
        self.basis = basis
        self.source_extracted_definition = source_extracted_definition
        self.source_generated_definition = source_generated_definition
        self.target_extracted_definition = target_extracted_definition
        self.target_generated_definition = target_generated_definition

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def getElements(self):
        return (self.id, self.idtype, self.target, self.targettype, self.inter_type)


def find_terms(my_search, genes, search_type):
    """
    KEY function for searching 'all_dic'. 
    We assume you have these fields in each doc:
      - entity1, entity2 (original)
      - entity1Upper, entity2Upper (uppercase copies)
    
    And you've created indexes on entity1Upper, entity2Upper 
    (and possibly compound with entity1type, entity2type if needed).

    search_type handling:
      - 'normal': same as before -> text index on entity1, entity1type, entity2, entity2type
      - 'exact': uses direct equality on entity1Upper, entity2Upper
      - 'alias': gather aliases, do $in on entity1Upper / entity2Upper
      - 'substring': your old approach with regex
      - 'non-alphanumeric': your old approach
      - 'paired_entity': your old approach
    """

    if not my_search:
        return [], [], {}, [], []

    function_start_time = time.time()
    loop_start_time = function_start_time

    forSending = []
    elements = []
    entity_counts = defaultdict(int)
    entity_connections = defaultdict(set)
    preview_dict = {}

    # -----------------------------
    # 1) 'normal' => text index
    # -----------------------------
    if search_type == 'normal':
        print("Normal search:", my_search)

        search_term = my_search[0]  # `my_search` contains only 1 item
        # Check if search term contains special characters or multiple words
        special_characters = r"[!@#$%^&*()_+={}[\]:;\"'<>,.?/~`\\|-]"
        contains_special = bool(re.search(special_characters, search_term))
        multiple_words = len(my_search) > 1
        
        # 1️⃣ Process search term to remove special characters (like in "exact" search)
        if contains_special or multiple_words:
            print("Using regex search due to special characters or multiple words.")

            # Escape special characters correctly for MongoDB find() regex
            escaped_term = re.escape(search_term)

            # Create a regex pattern for whole-word matching
            regex_pattern = re.compile(f".*{escaped_term}.*", re.IGNORECASE)

            # Normal MongoDB `$regex` query (NOT `$search`)
            query = {
                "$or": [
                    {"entity1": {"$regex": regex_pattern}},
                    {"entity2": {"$regex": regex_pattern}}
                ]
            }
            results = genes.find(query)
            result_list = list(results)  # Convert cursor to list
            print("Regex search results:", len(result_list))
            
        else:
            print("Using full-text search.")
            text_search_str = f'"{search_term}"'  # Add quotes for phrase search
            print("Final text search query:", text_search_str)
        
            # 2️⃣ Execute the text search
            query = {"$text": {"$search": text_search_str}}
            results = genes.find(query)
            result_list = list(results)  # Convert cursor to list

            print("Result's length:", len(result_list))


        # 4️⃣ Process the results (same logic as "exact" search)
        for doc in result_list:
            e1, e1t = doc["entity1"], doc["entity1type"]
            e2, e2t = doc["entity2"], doc["entity2type"]

            entity_counts[(e1, e1t)] += 1
            entity_counts[(e2, e2t)] += 1
            entity_connections[(e1, e1t)].add((e2, e2t))
            entity_connections[(e2, e2t)].add((e1, e1t))

            forSending.append(Gene(
                e1, e1t, e2, e2t,
                doc.get("edge"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"), doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"), doc.get("target_generated_definition")
            ))

            elements.append((
                e1, e1t, e2, e2t,
                doc.get("edge"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"), doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"), doc.get("target_generated_definition")
            ))

            # 5️⃣ Build preview (same logic as "exact" search)
            # Update preview dictionary for nodes with an exact match
            for word in my_search:
                word_lower = clean_search_term(word.lower())  # Normalize and clean search term
                pattern = re.compile(rf"\b{re.escape(word_lower)}\b", re.IGNORECASE)  # Whole-word match

                e1_lower, e2_lower = clean_search_term(e1.lower()), clean_search_term(e2.lower())  # Normalize entities

                if pattern.search(e1_lower):
                    unique_node_count = len(entity_connections[(e1, e1t)]) + 1
                    if ((e1, e1t) not in preview_dict or
                        entity_counts[(e1, e1t)] > preview_dict[(e1, e1t)][2]):
                        preview_dict[(e1, e1t)] = (e1, e1t, entity_counts[(e1, e1t)], unique_node_count)

                if pattern.search(e2_lower):
                    unique_node_count = len(entity_connections[(e2, e2t)]) + 1
                    if ((e2, e2t) not in preview_dict or
                        entity_counts[(e2, e2t)] > preview_dict[(e2, e2t)][2]):
                        preview_dict[(e2, e2t)] = (e2, e2t, entity_counts[(e2, e2t)], unique_node_count)
    # -----------------------------
    # 2) 'exact' => direct equality on entity1Upper, entity2Upper
    # -----------------------------

    elif search_type == 'exact':
        print("Exact search:", my_search)
        search_term = my_search[0]  # my_search contains only one item

        # Determine if we should use regex:
        # Apply regex if the search term contains special characters or if it is more than one word.
        if len(search_term.split()) > 1 or contains_special_characters(search_term):
            use_regex = True
        else:
            use_regex = False

        if not use_regex:
            # Use a text search when the search term is a single word and has no special characters.
            text_search_str = f'"{search_term}"'
            print("Final text search query:", text_search_str)
            query = {"$text": {"$search": text_search_str}}
            results = genes.find(query)
            result_list = list(results)
            print("Exact search results count:", len(result_list))
        else:
            # Escape special characters in the search term for regex
            regex_pattern = re.escape(search_term)
            print("Escaped Regex search query:", regex_pattern)

            query = {
                "$or": [
                    {"entity1": {"$regex": regex_pattern, "$options": "i"}},
                    {"entity2": {"$regex": regex_pattern, "$options": "i"}}
                ]
            }
            results = genes.find(query)
            result_list = list(results)
            print("Regex search results count:", len(result_list))
            
        # Process the results (same as before)
        for doc in result_list:
            e1, e1t = doc["entity1"], doc.get("entity1type")
            e2, e2t = doc["entity2"], doc.get("entity2type")

            # Normalize for consistent matching.
            e1_norm, e2_norm = normalize_text(e1), normalize_text(e2)

            entity_counts[(e1, e1t)] += 1
            entity_counts[(e2, e2t)] += 1
            entity_connections[(e1, e1t)].add((e2, e2t))
            entity_connections[(e2, e2t)].add((e1, e1t))

            forSending.append(Gene(
                e1, e1t, e2, e2t,
                doc.get("edge"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"), doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"), doc.get("target_generated_definition")
            ))
            elements.append((
                e1, e1t, e2, e2t,
                doc.get("edge"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"), doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"), doc.get("target_generated_definition")
            ))

            # Update preview dictionary for nodes with an exact match.
            for word in my_search:
                word_norm = normalize_text(word)
                if e1_norm == word_norm:  # Strict exact match
                    unique_node_count = len(entity_connections[(e1, e1t)]) + 1
                    if ((e1, e1t) not in preview_dict or
                        entity_counts[(e1, e1t)] > preview_dict[(e1, e1t)][2]):
                        preview_dict[(e1, e1t)] = (e1, e1t, entity_counts[(e1, e1t)], unique_node_count)

                if e2_norm == word_norm:  # Strict exact match
                    unique_node_count = len(entity_connections[(e2, e2t)]) + 1
                    if ((e2, e2t) not in preview_dict or
                        entity_counts[(e2, e2t)] > preview_dict[(e2, e2t)][2]):
                        preview_dict[(e2, e2t)] = (e2, e2t, entity_counts[(e2, e2t)], unique_node_count)     
                        
    # -----------------------------
    # 3) 'alias' => gather aliases, do $in on entity1Upper/entity2Upper
    # -----------------------------
    elif search_type == 'alias':
        print("Alias search:", my_search)
        geneAlias_collection = db["gene_alias"]

        # Query to get aliases
        gas = geneAlias_collection.find(
            {
                "$or": [
                    {"gene": {"$in": my_search}},
                    {"aliases": {"$in": my_search}}
                ]
            }
        )
        patterns = set()

        # Create patterns from aliases
        for ga in gas:
            patterns.add(ga['gene'].upper())
            for a in ga.get('aliases', []):
                patterns.add(a.upper())
        if not patterns and my_search:
            patterns.add(my_search[0].upper())

        print(patterns)

        # Create a text search query
        search_terms = " ".join(patterns)  # Combine patterns into a single string
        print("search_terms:", search_terms)
        query = {"$text": {"$search": search_terms}}

        # Perform the text search on genes collection
        results = genes.find(query)
        loop_start_time = time.time()

        for doc in results:
            e1, e1t = doc["entity1"], doc["entity1type"]
            e2, e2t = doc["entity2"], doc["entity2type"]

            entity_counts[(e1, e1t)] += 1
            entity_counts[(e2, e2t)] += 1
            entity_connections[(e1, e1t)].add((e2, e2t))
            entity_connections[(e2, e2t)].add((e1, e1t))

            forSending.append(Gene(
                e1, e1t, e2, e2t,
                doc.get("edge"), doc.get("pubmedID"), doc.get("p_source"), doc.get("species"),
                doc.get("basis"), doc.get("source_extracted_definition"), doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"), doc.get("target_generated_definition")
            ))
            elements.append((
                e1, e1t, e2, e2t,
                doc.get("edge"), doc.get("pubmedID"), doc.get("p_source"), doc.get("species"),
                doc.get("basis"), doc.get("source_extracted_definition"), doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"), doc.get("target_generated_definition")
            ))

            # preview
            for word in patterns:
                pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
                if pattern.search(e1):
                    unique_node_count = len(entity_connections[(e1, e1t)]) + 1
                    if ((e1, e1t) not in preview_dict or 
                        entity_counts[(e1, e1t)] > preview_dict[(e1, e1t)][2]):
                        preview_dict[(e1, e1t)] = (e1, e1t, entity_counts[(e1, e1t)], unique_node_count)
                if pattern.search(e2):
                    unique_node_count = len(entity_connections[(e2, e2t)]) + 1
                    if ((e2, e2t) not in preview_dict or 
                        entity_counts[(e2, e2t)] > preview_dict[(e2, e2t)][2]):
                        preview_dict[(e2, e2t)] = (e2, e2t, entity_counts[(e2, e2t)], unique_node_count)

    # -----------------------------
    # 4) 'substring' =>  (regex)
    # -----------------------------
    elif search_type == 'substring':
        print("Substring search:", my_search)
        
        # Start the overall function timer
        function_start_time = time.time()
        
        # Escape all patterns to prevent regex injection and handle special characters
        escaped_patterns = [re.escape(word) for word in my_search]
        
        # Combine all escaped patterns into a single regex using alternation
        combined_or_regex = "(" + "|".join(escaped_patterns) + ")"
        
        # Combine patterns for exact matches using word boundaries
        combined_nor_regex = "(" + "|".join(escaped_patterns) + ")"
        
        # Construct the optimized query
        query = {
            "$and": [
                {
                    "$or": [
                        {"entity1": {"$regex": combined_or_regex, "$options": "i"}},
                        {"entity2": {"$regex": combined_or_regex, "$options": "i"}}
                    ]
                },
                {
                    "$nor": [
                        {"entity1": {"$regex": rf"^{combined_nor_regex}$", "$options": "i"}},
                        {"entity2": {"$regex": rf"^{combined_nor_regex}$", "$options": "i"}}
                    ]
                }
            ]
        }
        results = genes.find(query)
        loop_start_time = time.time()

        for doc in results:
            e1, e1t = doc["entity1"], doc["entity1type"]
            e2, e2t = doc["entity2"], doc["entity2type"]

            entity_counts[(e1, e1t)] += 1
            entity_counts[(e2, e2t)] += 1
            entity_connections[(e1, e1t)].add((e2, e2t))
            entity_connections[(e2, e2t)].add((e1, e1t))

            forSending.append(Gene(
                e1, e1t, e2, e2t,
                doc["edge"], doc["pubmedID"], doc["p_source"], doc["species"],
                doc["basis"], doc["source_extracted_definition"], doc["source_generated_definition"],
                doc["target_extracted_definition"], doc["target_generated_definition"]
            ))
            elements.append((
                e1, e1t, e2, e2t,
                doc["edge"], doc["pubmedID"], doc["p_source"], doc["species"],
                doc["basis"], doc["source_extracted_definition"], doc["source_generated_definition"],
                doc["target_extracted_definition"], doc["target_generated_definition"]
            ))

            for word in my_search:
                pattern = re.compile(rf"{re.escape(word)}", re.IGNORECASE)
                if pattern.search(e1):
                    unique_node_count = len(entity_connections[(e1, e1t)]) + 1
                    if ((e1, e1t) not in preview_dict or 
                        entity_counts[(e1, e1t)] > preview_dict[(e1, e1t)][2]):
                        preview_dict[(e1, e1t)] = (e1, e1t, entity_counts[(e1, e1t)], unique_node_count)
                if pattern.search(e2):
                    unique_node_count = len(entity_connections[(e2, e2t)]) + 1
                    if ((e2, e2t) not in preview_dict or 
                        entity_counts[(e2, e2t)] > preview_dict[(e2, e2t)][2]):
                        preview_dict[(e2, e2t)] = (e2, e2t, entity_counts[(e2, e2t)], unique_node_count)

    # -----------------------------
    # 5) 'non-alphanumeric' => regex
    # -----------------------------
    elif search_type == 'non-alphanumeric':
        print("Non-alphanumeric search:", my_search)
        
        # Start the overall function timer
        function_start_time = time.time()
        
        # Escape all patterns to prevent regex injection and handle special characters
        escaped_patterns = [re.escape(word) for word in my_search]
        
        # Combine all escaped patterns into a single regex using alternation
        # Example: ^pattern1[^a-zA-Z0-9 ]|^pattern2[^a-zA-Z0-9 ]
        combined_regex = "|".join([f'^{pat}[^a-zA-Z0-9 ]' for pat in escaped_patterns])

        # Compile the combined regex pattern for efficiency
        compiled_regex = re.compile(combined_regex, re.IGNORECASE)

        # Construct the optimized query
        query = {
            "$or": [
                {"entity1": {"$regex": compiled_regex}},
                {"entity2": {"$regex": compiled_regex}}
            ]
        }
        
        results = genes.find(query)
        loop_start_time = time.time()

        for doc in results:
            e1, e1t = doc["entity1"], doc["entity1type"]
            e2, e2t = doc["entity2"], doc["entity2type"]

            entity_counts[(e1, e1t)] += 1
            entity_counts[(e2, e2t)] += 1
            entity_connections[(e1, e1t)].add((e2, e2t))
            entity_connections[(e2, e2t)].add((e1, e1t))

            forSending.append(Gene(
                e1, e1t, e2, e2t,
                doc["edge"], doc["pubmedID"], doc["p_source"], doc["species"],
                doc["basis"], doc["source_extracted_definition"], doc["source_generated_definition"],
                doc["target_extracted_definition"], doc["target_generated_definition"]
            ))
            elements.append((
                e1, e1t, e2, e2t,
                doc["edge"], doc["pubmedID"], doc["p_source"], doc["species"],
                doc["basis"], doc["source_extracted_definition"], doc["source_generated_definition"],
                doc["target_extracted_definition"], doc["target_generated_definition"]
            ))

            for word in my_search:
                pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
                if pattern.search(e1):
                    unique_node_count = len(entity_connections[(e1, e1t)]) + 1
                    if ((e1, e1t) not in preview_dict or 
                        entity_counts[(e1, e1t)] > preview_dict[(e1, e1t)][2]):
                        preview_dict[(e1, e1t)] = (e1, e1t, entity_counts[(e1, e1t)], unique_node_count)
                if pattern.search(e2):
                    unique_node_count = len(entity_connections[(e2, e2t)]) + 1
                    if ((e2, e2t) not in preview_dict or 
                        entity_counts[(e2, e2t)] > preview_dict[(e2, e2t)][2]):
                        preview_dict[(e2, e2t)] = (e2, e2t, entity_counts[(e2, e2t)], unique_node_count)

    # -----------------------------
    # 6) 'paired_entity' => old approach
    # -----------------------------
    elif search_type == 'paired_entity':
        print("Paired entity search:", my_search)
        patterns = [word for key in my_search for word in key.split('$')]
        escaped_patterns = [re.escape(word) for word in patterns]

        if len(escaped_patterns) == 2:
            p1, p2 = escaped_patterns
            condition1 = [{
                "$and": [
                    {"entity1": {"$regex": rf"\b{p1}\b", "$options": "i"}},
                    {"entity2": {"$regex": rf"\b{p2}\b", "$options": "i"}}
                ]
            }]
            condition2 = [{
                "$and": [
                    {"entity1": {"$regex": rf"\b{p2}\b", "$options": "i"}},
                    {"entity2": {"$regex": rf"\b{p1}\b", "$options": "i"}}
                ]
            }]
            query = {"$or": condition1 + condition2}
            results = genes.find(query)
            loop_start_time = time.time()
        else:
            results = []
            loop_start_time = time.time()

        for doc in results:
            e1, e1t = doc["entity1"], doc["entity1type"]
            e2, e2t = doc["entity2"], doc["entity2type"]

            entity_counts[(e1, e1t)] += 1
            entity_counts[(e2, e2t)] += 1
            entity_connections[(e1, e1t)].add((e2, e2t))
            entity_connections[(e2, e2t)].add((e1, e1t))

            forSending.append(Gene(
                e1, e1t, e2, e2t,
                doc["edge"], doc["pubmedID"], doc["p_source"], doc["species"],
                doc["basis"], doc["source_extracted_definition"], doc["source_generated_definition"],
                doc["target_extracted_definition"], doc["target_generated_definition"]
            ))
            elements.append((
                e1, e1t, e2, e2t,
                doc["edge"], doc["pubmedID"], doc["p_source"], doc["species"],
                doc["basis"], doc["source_extracted_definition"], doc["source_generated_definition"],
                doc["target_extracted_definition"], doc["target_generated_definition"]
            ))

            for word in escaped_patterns:
                pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
                if pattern.search(e1):
                    unique_node_count = len(entity_connections[(e1, e1t)]) + 1
                    if ((e1, e1t) not in preview_dict or 
                        entity_counts[(e1, e1t)] > preview_dict[(e1, e1t)][2]):
                        preview_dict[(e1, e1t)] = (e1, e1t, entity_counts[(e1, e1t)], unique_node_count)
                if pattern.search(e2):
                    unique_node_count = len(entity_connections[(e2, e2t)]) + 1
                    if ((e2, e2t) not in preview_dict or 
                        entity_counts[(e2, e2t)] > preview_dict[(e2, e2t)][2]):
                        preview_dict[(e2, e2t)] = (e2, e2t, entity_counts[(e2, e2t)], unique_node_count)

    else:
        raise Exception(f"Invalid search_type: {search_type}")

    # done building
    preview = sorted(preview_dict.values(), key=lambda x: (x[2], x[3]), reverse=True)

    end_time = time.time()
    function_elapsed_time = end_time - function_start_time
    loop_elapsed_time = end_time - loop_start_time
    print(f"Function Elapsed time: {function_elapsed_time:.4f} seconds")
    print(f"Loop Elapsed time: {loop_elapsed_time:.4f} seconds")

    return list(set(elements)), forSending, {}, [], preview


#
# The rest of your route code remains basically the same,
# using these newly updated queries in find_terms().
#


def generate_search_route(search_type):
    """
    1) Queries MongoDB with find_terms().
    2) Caches results in memory, returns 'preview_search.html' or 'not_found.html'.
    """
    def search_route(query):
        start_time = time.time()
        
        categories = [value for key, value in request.args.items() if key.startswith('category_')]

        if not query:
            query = 'DEFAULT'

        if len(query) > 0:
            my_search = query.upper().split(';')
            trimmed_search = [keyword.strip() for keyword in my_search if keyword.strip()]

            # Profile MongoDB query
            query_start = time.time()
            collection = db["all_dic"]
            elements, forSending, elementsAb, node_fa, preview = find_terms(
                trimmed_search, collection, search_type
            )
            print(f"find_terms execution time: {time.time() - query_start:.2f} seconds")

            if forSending:
                # Profile data processing
                process_start = time.time()
                updatedElements = process_network(elements)
                cytoscape_js_code = generate_cytoscape_js(updatedElements, elementsAb, node_fa)

                summaryText = make_text(forSending)
                print(f"Data processing time: {time.time() - process_start:.2f} seconds")

                # Cache results
                unique_id = str(uuid.uuid4())
                cache[unique_id] = {
                    "elements": elements,
                    "forSending": forSending,
                    "elementsAb": elementsAb,
                    "node_fa": node_fa,
                    "preview": preview,
                    "summaryText": summaryText,
                }

                patterns_title = query.upper()

                # Profile rendering
                render_start = time.time()
                response = render_template(
                    'preview_search.html',
                    genes=forSending,
                    selected_categories=categories,
                    cytoscape_js_code=cytoscape_js_code,
                    search_term=patterns_title,
                    warning="",
                    summary=summaryText,
                    node_ab=[],
                    node_fa=node_fa,
                    is_node=True,
                    search_type=search_type,
                    preview_results=preview,
                    unique_id=unique_id
                )
                print(f"Rendering time: {time.time() - render_start:.2f} seconds")
                print(f"Total execution time: {time.time() - start_time:.2f} seconds")
                return response
            else:
                return render_template('not_found.html', search_term=query)

        return render_template('not_found.html', search_term=query)
    return search_route


def generate_search_route2(search_type):
    """
    Grabs 'uid' from request.args, loads from cache, 
    displays 'gene.html' or 'not_found.html' accordingly.
    """
    def search_route(query, entity_type):
        categories = [value for key, value in request.args.items() if key.startswith('category_')]
        uid = request.args.get('uid')

        if not uid:
            return "Error: No unique_id provided in ?uid=."
        if uid not in cache:
            return "Error: This search data is not available or may have expired."

        stored_data = cache[uid]
        elements = stored_data["elements"]
        forSending = stored_data["forSending"]
        elementsAb = stored_data["elementsAb"]
        node_fa = stored_data["node_fa"]
        preview = stored_data["preview"]
        summaryText = stored_data["summaryText"]

        # Filter
        filtered_forSending = [
            g for g in forSending
            if ((g.id == query and g.idtype == entity_type) or
                (g.target == query and g.targettype == entity_type))
        ]

        filtered_elements = []
        for e in elements:
            if ((e[0] == query and e[1] == entity_type) or
                (e[2] == query and e[3] == entity_type)):
                filtered_elements.append(e)

        updatedElements = process_network(filtered_elements)
        cytoscape_js_code = generate_cytoscape_js(updatedElements, elementsAb, node_fa)
        patterns_title = f"{query.upper()} [{entity_type.upper()}]" if entity_type else query.upper()

        if filtered_forSending:
            return render_template(
                'gene.html',
                genes=filtered_forSending,
                selected_categories=categories,
                cytoscape_js_code=cytoscape_js_code,
                search_term=patterns_title,
                warning="",
                summary=summaryText,
                node_ab=[],
                node_fa=node_fa,
                is_node=True,
                search_type=search_type,
                preview_results=preview
            )
        else:
            return render_template('not_found.html', search_term=query)

    return search_route


def generate_multi_search_route(search_type):
    """
    Same multi-entity logic as your original code, 
    combining partial results from the cached data.
    """
    bracket_pattern = re.compile(r"^(.*)\[(.*)\]$")

    def search_route(multi_query):
        if request.method == 'POST':
            data = request.get_json(silent=True) or {}
            selected_list = data.get("selected_entities", [])
            search_term = data.get("search_term", "")

            uid = request.args.get("uid")
            if not uid:
                return render_template('error.html', message="No uid provided in ?uid=..."), 400
            if uid not in cache:
                return render_template('error.html', message="Session ended or not in cache."), 400

            cache[uid]["multi_selected_entities"] = selected_list

            if not search_term:
                search_term = "placeholder"

            return redirect(url_for(
                request.endpoint,
                multi_query=f"{search_term}_multi",
                uid=uid
            ))

        uid = request.args.get("uid")
        if not uid:
            return render_template('error.html', message="Session ended. Please re-run the search.")
        if uid not in cache:
            return render_template('error.html', message="Session ended or not in cache.")

        stored_data = cache[uid]
        elements    = stored_data.get("elements", [])
        forSending  = stored_data.get("forSending", [])
        elementsAb  = stored_data.get("elementsAb", {})
        node_fa     = stored_data.get("node_fa", [])
        preview     = stored_data.get("preview", [])
        summaryText = stored_data.get("summaryText", "")

        raw_pairs = stored_data.get("multi_selected_entities", [])
        pairs = []
        for item in raw_pairs:
            if '|' in item:
                entityName, entityType = item.split('|', 1)
                pairs.append(f"{entityName} [{entityType}]")
            else:
                pairs.append(item)

        if not pairs:
            return render_template('not_found.html', search_term=multi_query)

        combined_elements = set()
        combined_forSending = []
        combined_preview = []
        display_labels = []

        for pair in pairs:
            match = bracket_pattern.match(pair)
            if match:
                entityName = match.group(1).strip()
                entityType = match.group(2).strip()
                display_label = f"{entityName} [{entityType}]"
            else:
                entityName = pair
                entityType = "UNKNOWN"
                display_label = f"{entityName} [UNKNOWN]"

            display_labels.append(display_label)

            partial_forSending = [
                g for g in forSending
                if ((g.id.upper() == entityName.upper() and g.idtype.upper() == entityType.upper())
                    or (g.target.upper() == entityName.upper() and g.targettype.upper() == entityType.upper()))
            ]

            partial_elements = [
                e for e in elements
                if ((e[0].upper() == entityName.upper() and e[1].upper() == entityType.upper())
                    or (e[2].upper() == entityName.upper() and e[3].upper() == entityType.upper()))
            ]

            combined_forSending.extend(partial_forSending)
            combined_elements.update(partial_elements)

        if not combined_forSending:
            return render_template('not_found.html', search_term=multi_query)

        updatedElements = process_network(list(combined_elements))
        cytoscape_js_code = generate_cytoscape_js(updatedElements, {}, node_fa)
        warning = ""
        finalSummaryText = make_text(combined_forSending)
        all_pairs_label = ", ".join(label.upper() for label in display_labels)

        return render_template(
            'gene.html',
            genes=combined_forSending,
            cytoscape_js_code=cytoscape_js_code,
            search_term=all_pairs_label,
            warning=warning,
            summary=finalSummaryText,
            node_ab=[],
            node_fa=node_fa,
            is_node=True,
            search_type=search_type,
            preview_results=combined_preview
        )

    return search_route


def generate_search_route3(search_type):
    """
    Another route that calls find_terms() with the chosen search_type 
    to keep logic the same as your original design.
    """
    def search_route(query):
        categories = [value for key, value in request.args.items() if key.startswith('category_')]

        try:
            my_search = query.strip()
            print("my_search:", my_search)
        except Exception as e:
            print(f"Error processing query: {e}")
            my_search = 'DEFAULT'

        forSending, preview = [], []
        cytoscape_js_code = ""
        warning = ""
        summaryText = ""
        node_ab = []
        node_fa = []

        if my_search:
            # e.g. "abc;def"
            split_search = my_search.upper().split(';')
            trimmed_search = [keyword.strip() for keyword in split_search if keyword.strip()]

            all_dic_collection = db["all_dic"]

            elements, forSending, elementsAb, node_fa, preview = find_terms(
                trimmed_search, all_dic_collection, search_type
            )

            updatedElements = process_network(elements)
            cytoscape_js_code = generate_cytoscape_js(updatedElements, elementsAb, node_fa)
            summaryText = make_text(forSending)

        if forSending:
            display_search_term = my_search.upper()
            return render_template(
                'gene.html',
                genes=forSending,
                selected_categories=categories,
                cytoscape_js_code=cytoscape_js_code,
                search_term=display_search_term,
                warning=warning,
                summary=summaryText,
                node_ab=node_ab,
                node_fa=node_fa,
                is_node=True,
                search_type=search_type,
                preview_results=preview
            )
        else:
            return render_template('not_found.html', search_term=my_search)

    return search_route

def get_scientific_chunk(p_source):
    """
    Searches for p_source in the 'scientific_chunks' collection by matching 'custom_id' 
    and retrieves the 'user_content' field.
    
    :param p_source: The ID to search for in 'custom_id'.
    :return: The 'user_content' field if found, else None.
    """
    result = scientific_chunks.find_one({"custom_id": p_source}, {"_id": 0, "user_content": 1})

    # Return user_content if found, else return None
    return result["user_content"] if result else None
    