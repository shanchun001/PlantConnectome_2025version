"""
search.py - Demonstrating how to use normalized fields for 'exact'/'alias', 
plus your original logic for 'normal', 'substring', 'non-alphanumeric', etc.
"""
import unicodedata
import json

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
    Represents a relationship between two disambiguated biological entities,
    along with supporting metadata.

    Parameters:
    - id, idtype: Disambiguated source entity (entity1_disamb, entity1type_disamb)
    - target, targettype: Disambiguated target entity (entity2_disamb, entity2type_disamb)
    - edge_disamb: Disambiguated interaction
    - publication, p_source, species, basis: metadata
    - source_extracted_definition, source_generated_definition
    - target_extracted_definition, target_generated_definition
    - entity1, entity2, entity1type, entity2type: original (non-disambiguated)
    - inter_type: original edge type
    """

    def __init__(
        self,
        disamb_id,
        disamb_idtype,
        disamb_target,
        disamb_targettype,
        edge_disamb,
        publication,
        p_source,
        species,
        basis,
        source_extracted_definition,
        source_generated_definition,
        target_extracted_definition,
        target_generated_definition,
        entity1,
        entity2,
        entity1type,
        entity2type,
        inter_type
    ):
        # Disambiguated fields
        self.id = disamb_id
        self.idtype = disamb_idtype
        self.target = disamb_target
        self.targettype = disamb_targettype

        # Disambiguated edge
        self.edge_disamb = edge_disamb

        # Original interaction
        self.inter_type = inter_type

        # Metadata
        self.publication = publication
        self.p_source = p_source
        self.species = species
        self.basis = basis

        # Definitions
        self.source_extracted_definition = source_extracted_definition
        self.source_generated_definition = source_generated_definition
        self.target_extracted_definition = target_extracted_definition
        self.target_generated_definition = target_generated_definition

        # Original names before disambiguation
        self.entity1 = entity1
        self.entity2 = entity2
        self.entity1type = entity1type
        self.entity2type = entity2type

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def getElements(self):
        """Return a tuple of disambiguated edge information."""
        return (self.id, self.idtype, self.target, self.targettype, self.edge_disamb or self.inter_type)
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
        search_term = my_search[0]
        print(search_term)

        # Detect special chars or multi-word
        special_characters = r"[!@#$%^&*()_+={}[\]:;\"'<>,.?/~`\\|-]"
        contains_special = bool(re.search(special_characters, search_term))
        multiple_words = len(my_search) > 1

        # 1️⃣ Build the Mongo query
        if contains_special or multiple_words:
            print("Using regex search.")
            escaped = re.escape(search_term)
            pattern = re.compile(f".*{escaped}.*", re.IGNORECASE)
            query = {
                "$or": [
                    {"entity1_disamb": {"$regex": pattern}},
                    {"entity2_disamb": {"$regex": pattern}}
                ]
            }
        else:
            print("Using full-text search.")
            quoted = f'"{search_term}"'
            query = {"$text": {"$search": quoted}}

        result_list = list(genes.find(query))
        print("Number of hits:", len(result_list))

        # —— 2️⃣ First pass: collect all observed types per entity name —— #
        name_to_types = defaultdict(set)
        for doc in result_list:
            name_to_types[doc["entity1_disamb"]].add(doc["entity1type_disamb"].lower())
            name_to_types[doc["entity2_disamb"]].add(doc["entity2type_disamb"].lower())

        # —— 3️⃣ Build merged‐type map: merge all names having multiple types —— #
        name_to_merged = {}

        for name, typeset in name_to_types.items():
            if len(typeset) > 1:
                # sort types alphabetically (or any order you like)
                ordered = sorted(typeset)
                name_to_merged[name.lower()] = ", ".join(ordered)
                #print(f"Merged types for {name}: {ordered}")
            else:
                # only one type → just use it
                name_to_merged[name.lower()] = next(iter(typeset))

        

        # —— 4️⃣ Second pass: process each document using merged types —— #
        for doc in result_list:
            e1 = doc["entity1_disamb"]
            e2 = doc["entity2_disamb"]

            # raw type lowercased for fallback
            raw1 = doc["entity1type_disamb"].lower()
            raw2 = doc["entity2type_disamb"].lower()

            # lookup merged by lowercase name, else fallback
            e1t = name_to_merged.get(e1.lower(), raw1)
            e2t = name_to_merged.get(e2.lower(), raw2)

            # update counts & connections
            entity_counts[(e1, e1t)] += 1
            entity_counts[(e2, e2t)] += 1
            entity_connections[(e1, e1t)].add((e2, e2t))
            entity_connections[(e2, e2t)].add((e1, e1t))

            # build Gene objects
            forSending.append(Gene(
                e1, e1t, e2, e2t,
                doc.get("edge_disamb"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"),
                doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"),
                doc.get("target_generated_definition"),
                doc.get("entity1"), doc.get("entity2"),
                doc.get("entity1type"), doc.get("entity2type"),
                doc.get("edge")
            ))

            # collect raw elements
            elements.append((
                e1, e1t, e2, e2t,
                doc.get("edge_disamb"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"),
                doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"),
                doc.get("target_generated_definition"),
                doc.get("entity1"), doc.get("entity2"),
                doc.get("entity1type"), doc.get("entity2type"),
                doc.get("edge")
            ))

            # 5️⃣ Build preview entries
            for word in my_search:
                wl = word.lower()
                escaped = re.escape(wl)
                e1_clean = e1.lower()
                e2_clean = e2.lower()
                
                pat1 = re.compile(rf"\b{(wl)}\b", re.IGNORECASE)
                if pat1.search(e1_clean):
                    uniq = len(entity_connections[(e1, e1t)]) + 1
                    cur = preview_dict.get((e1, e1t))
                    if not cur or entity_counts[(e1, e1t)] > cur[2]:
                        preview_dict[(e1, e1t)] = (e1, e1t,
                                                entity_counts[(e1, e1t)],
                                                uniq)

                if pat1.search(e2_clean):
                    uniq = len(entity_connections[(e2, e2t)]) + 1
                    cur = preview_dict.get((e2, e2t))
                    if not cur or entity_counts[(e2, e2t)] > cur[2]:
                        preview_dict[(e2, e2t)] = (e2, e2t,
                                                entity_counts[(e2, e2t)],
                                                uniq)

    # -----------------------------
    # 2) 'exact' => direct equality on entity1Upper, entity2Upper
    # -----------------------------
    
    elif search_type == 'exact':
        print("Exact search:", my_search)
        search_term = my_search[0]

        # Decide whether to use regex or text search
        if len(search_term.split()) > 1 or contains_special_characters(search_term):
            use_regex = True
        else:
            use_regex = False

        # 1️⃣ Execute the query and collect result_list
        if not use_regex:
            text_search_str = f'"{search_term}"'
            print("Final text search query:", text_search_str)
            results = genes.find({"$text": {"$search": text_search_str}})
        else:
            regex_pattern = re.escape(search_term)
            print("Escaped Regex search query:", regex_pattern)
            results = genes.find({
                "$or": [
                    {"entity1_disamb": {"$regex": regex_pattern, "$options": "i"}},
                    {"entity2_disamb": {"$regex": regex_pattern, "$options": "i"}}
                ]
            })
        result_list = list(results)
        print("Exact search results count:", len(result_list))

        # —— 2️⃣ First pass: collect all observed types per entity name —— #
        name_to_types = defaultdict(set)
        for doc in result_list:
            name_to_types[doc["entity1_disamb"]].add(doc["entity1type_disamb"].lower())
            name_to_types[doc["entity2_disamb"]].add(doc["entity2type_disamb"].lower())

        # —— 3️⃣ Build merged‐type map: merge names having multiple types —— #
        name_to_merged = {}
        for name, typeset in name_to_types.items():
            if len(typeset) > 1:
                ordered = sorted(typeset)
                name_to_merged[name.lower()] = ", ".join(ordered)
                #print(f"Merged types for {name}: {ordered}")
            else:
                name_to_merged[name.lower()] = next(iter(typeset))

        # —— 4️⃣ Second pass: process each document using merged types —— #
        for doc in result_list:
            e1, e2 = doc["entity1_disamb"], doc["entity2_disamb"]
            raw1 = doc["entity1type_disamb"].lower()
            raw2 = doc["entity2type_disamb"].lower()

            # lookup merged type (fallback to raw if name not in map)
            e1t = name_to_merged.get(e1.lower(), raw1)
            e2t = name_to_merged.get(e2.lower(), raw2)

            # update counts & connections
            entity_counts[(e1, e1t)] += 1
            entity_counts[(e2, e2t)] += 1
            entity_connections[(e1, e1t)].add((e2, e2t))
            entity_connections[(e2, e2t)].add((e1, e1t))

            # build Gene objects and raw elements list
            forSending.append(Gene(
                e1, e1t, e2, e2t,
                doc.get("edge_disamb"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"),
                doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"),
                doc.get("target_generated_definition"),
                doc.get("entity1"), doc.get("entity2"),
                doc.get("entity1type"), doc.get("entity2type"),
                doc.get("edge")
            ))
            elements.append((
                e1, e1t, e2, e2t,
                doc.get("edge_disamb"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"),
                doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"),
                doc.get("target_generated_definition"),
                doc.get("entity1"), doc.get("entity2"),
                doc.get("entity1type"), doc.get("entity2type"),
                doc.get("edge")
            ))

            # —— 5️⃣ Build preview entries using merged types & strict exact match —— #
            e1_norm = normalize_text(e1)
            e2_norm = normalize_text(e2)
            for word in my_search:
                word_norm = normalize_text(word)
                if e1_norm == word_norm:
                    uniq = len(entity_connections[(e1, e1t)]) + 1
                    cur = preview_dict.get((e1, e1t))
                    if not cur or entity_counts[(e1, e1t)] > cur[2]:
                        preview_dict[(e1, e1t)] = (e1, e1t,
                                                entity_counts[(e1, e1t)],
                                                uniq)
                if e2_norm == word_norm:
                    uniq = len(entity_connections[(e2, e2t)]) + 1
                    cur = preview_dict.get((e2, e2t))
                    if not cur or entity_counts[(e2, e2t)] > cur[2]:
                        preview_dict[(e2, e2t)] = (e2, e2t,
                                                entity_counts[(e2, e2t)],
                                                uniq)         
    # -----------------------------
    # 3) 'alias' => gather aliases, do $in on entity1Upper/entity2Upper NOT WORKING
    # -----------------------------
    elif search_type == 'alias':
        print("Alias search:", my_search)
        geneAlias_collection = db["gene_alias"]

        # Query to get aliases
        gas = geneAlias_collection.find({
            "$or": [
                {"gene": {"$in": my_search}},
                {"aliases": {"$in": my_search}}
            ]
        })
        patterns = set()

        # Create patterns from aliases
        for ga in gas:
            patterns.add(ga['gene'].upper())
            for a in ga.get('aliases', []):
                patterns.add(a.upper())
        if not patterns and my_search:
            patterns.add(my_search[0].upper())

        print("Alias patterns:", patterns)

        # Create a text search query
        search_terms = " ".join(patterns)  # Combine patterns into a single string
        print("search_terms:", search_terms)
        query = {"$text": {"$search": search_terms}}

        # Perform the text search on genes collection
        results = genes.find(query)
        loop_start_time = time.time()

        # Instead of using a specific regex filter, build the canonical alias by joining all words
        canonical_gene_alias = " ".join(sorted(patterns))
        print("Canonical gene alias from patterns:", canonical_gene_alias)

        # Build a unified regex pattern that matches any alias in the patterns set.
        # This pattern uses a named group "alias" for the alias portion, and "tail" for any following non-alphabetical characters.
        pattern_str = r"(?P<alias>" + "|".join(re.escape(word) for word in patterns) + r")(?P<tail>[^A-Za-z]+)?"
        unified_pattern = re.compile(pattern_str, re.IGNORECASE)
        print("Unified substitution pattern:", unified_pattern.pattern)

        # Define a replacement function
        def replacement(match):
            tail = match.group("tail") or ""
            if tail and not tail.startswith(" "):
                tail = " " + tail
            return canonical_gene_alias + tail

        for doc in results:
            # Get the original values for entity1 and entity2
            e1, e1t = doc["entity1_disamb"], doc["entity1type_disamb"]
            e2, e2t = doc["entity2_disamb"], doc["entity2type_disamb"]

            # --- Process entity1 ---
            new_e1 = unified_pattern.sub(replacement, e1)

            # --- Process entity2 ---
            new_e2 = unified_pattern.sub(replacement, e2)

            # Update entity counts and connections using the new entity names.
            entity_counts[(new_e1, e1t)] += 1
            entity_counts[(new_e2, e2t)] += 1
            entity_connections[(new_e1, e1t)].add((new_e2, e2t))
            entity_connections[(new_e2, e2t)].add((new_e1, e1t))

            # Append to output lists (forSending and elements) using the new entity names.
            forSending.append(Gene(
                new_e1, e1t, new_e2, e2t,
                doc.get("edge_disamb"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"), doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"), doc.get("target_generated_definition"),
                doc.get("entity1"), doc.get("entity2"),
                doc.get("entity1type"), doc.get("entity2type"), doc.get("edge")
            ))

            elements.append((
                new_e1, e1t, new_e2, e2t,
                doc.get("edge_disamb"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"), doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"), doc.get("target_generated_definition"),
                doc.get("entity1"), doc.get("entity2"),
                doc.get("entity1type"), doc.get("entity2type"), doc.get("edge")
            ))

            # Preview update using the new entity names.
            for word in patterns:
                preview_pattern = re.compile(rf"\b{re.escape(word)}(?:[^A-Za-z]+)?", re.IGNORECASE)
                if preview_pattern.search(new_e1):
                    unique_node_count = len(entity_connections[(new_e1, e1t)]) + 1
                    if ((new_e1, e1t) not in preview_dict or 
                        entity_counts[(new_e1, e1t)] > preview_dict[(new_e1, e1t)][2]):
                        preview_dict[(new_e1, e1t)] = (new_e1, e1t, entity_counts[(new_e1, e1t)], unique_node_count)
                if preview_pattern.search(new_e2):
                    unique_node_count = len(entity_connections[(new_e2, e2t)]) + 1
                    if ((new_e2, e2t) not in preview_dict or 
                        entity_counts[(new_e2, e2t)] > preview_dict[(new_e2, e2t)][2]):
                        preview_dict[(new_e2, e2t)] = (new_e2, e2t, entity_counts[(new_e2, e2t)], unique_node_count)

    # -----------------------------
    # 4) 'substring' =>  (regex)
    # -----------------------------
    elif search_type == 'substring':
        print("Substring search:", my_search)
        function_start_time = time.time()


        # Create individual regex conditions for each term
        regex_conditions = []
        for word in my_search:
            escaped_word = re.escape(word)  # Escape special characters
            regex_conditions.append({"entity1_disamb": {"$regex": escaped_word, "$options": "i"}})
            regex_conditions.append({"entity2_disamb": {"$regex": escaped_word, "$options": "i"}})

        # Final query: match if any field contains any of the substrings
        query = {
            "$or": regex_conditions
        }
        
        '''
        query = {
            "$and": [
                {   # any field contains one of the terms
                    "$or": [
                        {"entity1_disamb": {"$regex": combined_or_regex, "$options": "i"}},
                        {"entity2_disamb": {"$regex": combined_or_regex, "$options": "i"}}
                    ]
                },
                {   # but neither field is an exact match
                    "$nor": [
                        {"entity1_disamb": {"$regex": rf"^{combined_nor_regex}$", "$options": "i"}},
                        {"entity2_disamb": {"$regex": rf"^{combined_nor_regex}$", "$options": "i"}}
                    ]
                }
            ]
        }
        '''
        # Pull all matching docs at once
        result_list = list(genes.find(query))
        print("Number of hits:", len(result_list))

        # —— 2️⃣ First pass: collect all observed types per entity name —— #
        name_to_types = defaultdict(set)
        for doc in result_list:
            name_to_types[doc["entity1_disamb"]].add(doc["entity1type_disamb"].lower())
            name_to_types[doc["entity2_disamb"]].add(doc["entity2type_disamb"].lower())

        # —— 3️⃣ Build merged‑type map: merge names having multiple types —— #
        name_to_merged = {}
        for name, typeset in name_to_types.items():
            if len(typeset) > 1:
                ordered = sorted(typeset)
                name_to_merged[name.lower()] = ", ".join(ordered)
                #print(f"Merged types for {name}: {ordered}")
            else:
                name_to_merged[name.lower()] = next(iter(typeset))


        # —— 4️⃣ Second pass: process each document using merged types —— #
        for doc in result_list:
            e1 = doc["entity1_disamb"]
            e2 = doc["entity2_disamb"]

            # ➊ Lookup merged types (fallback to raw if not merged)
            raw1 = doc["entity1type_disamb"].lower()
            raw2 = doc["entity2type_disamb"].lower()
            e1t  = name_to_merged.get(e1.lower(), raw1)
            e2t  = name_to_merged.get(e2.lower(), raw2)

            # ➋ Update counts & connections (as before)
            entity_counts[(e1, e1t)] += 1
            entity_counts[(e2, e2t)] += 1
            entity_connections[(e1, e1t)].add((e2, e2t))
            entity_connections[(e2, e2t)].add((e1, e1t))

            # build your Gene objects and flat element tuples
            forSending.append(Gene(
                e1, e1t, e2, e2t,
                doc.get("edge_disamb"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"),
                doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"),
                doc.get("target_generated_definition"),
                doc.get("entity1"), doc.get("entity2"),
                doc.get("entity1type"), doc.get("entity2type"),
                doc.get("edge")
            ))
            elements.append((
                e1, e1t, e2, e2t,
                doc.get("edge_disamb"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"),
                doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"),
                doc.get("target_generated_definition"),
                doc.get("entity1"), doc.get("entity2"),
                doc.get("entity1type"), doc.get("entity2type"),
                doc.get("edge")
            ))
            # —— 5️⃣ Build preview entries using the original substring pattern —— #
            for word in my_search:
                #pattern = re.compile(rf"(?<![\w\s]){re.escape(word)}(?![\s])", re.IGNORECASE)
                pattern = re.compile(re.escape(word), re.IGNORECASE)


                # match raw string, but store under merged‐type key
                if pattern.search(e1):
                    uniq = len(entity_connections[(e1, e1t)]) + 1
                    cur = preview_dict.get((e1, e1t))
                    if not cur or entity_counts[(e1, e1t)] > cur[2]:
                        preview_dict[(e1, e1t)] = (e1, e1t,
                                                entity_counts[(e1, e1t)],
                                                uniq)

                if pattern.search(e2):
                    uniq = len(entity_connections[(e2, e2t)]) + 1
                    cur = preview_dict.get((e2, e2t))
                    if not cur or entity_counts[(e2, e2t)] > cur[2]:
                        preview_dict[(e2, e2t)] = (e2, e2t,
                                                entity_counts[(e2, e2t)],
                                                uniq)
                        
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
                {"entity1_disamb": {"$regex": compiled_regex}},
                {"entity2_disamb": {"$regex": compiled_regex}}
            ]
        }
        
        results = genes.find(query)
        loop_start_time = time.time()

        for doc in results:
            e1, e1t = doc["entity1_disamb"], doc["entity1type_disamb"]
            e2, e2t = doc["entity2_disamb"], doc["entity2type_disamb"]

            entity_counts[(e1, e1t)] += 1
            entity_counts[(e2, e2t)] += 1
            entity_connections[(e1, e1t)].add((e2, e2t))
            entity_connections[(e2, e2t)].add((e1, e1t))

            forSending.append(Gene(
                e1, e1t, e2, e2t,
                doc.get("edge_disamb"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"), doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"), doc.get("target_generated_definition"), 
                doc.get("entity1"), doc.get("entity2"),
                doc.get("entity1type"), doc.get("entity2type"), doc.get("edge")
            ))

            elements.append((
                e1, e1t, e2, e2t,
                doc.get("edge_disamb"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"), doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"), doc.get("target_generated_definition"), 
                doc.get("entity1"), doc.get("entity2"),
                doc.get("entity1type"), doc.get("entity2type"), doc.get("edge")
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
            e1, e1t = doc["entity1_disamb"], doc["entity1type_disamb"]
            e2, e2t = doc["entity2_disamb"], doc["entity2type_disamb"]

            entity_counts[(e1, e1t)] += 1
            entity_counts[(e2, e2t)] += 1
            entity_connections[(e1, e1t)].add((e2, e2t))
            entity_connections[(e2, e2t)].add((e1, e1t))

            forSending.append(Gene(
                e1, e1t, e2, e2t,
                doc.get("edge_disamb"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"), doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"), doc.get("target_generated_definition"), 
                doc.get("entity1"), doc.get("entity2"),
                doc.get("entity1type"), doc.get("entity2type"), doc.get("edge")
            ))

            elements.append((
                e1, e1t, e2, e2t,
                doc.get("edge_disamb"), doc.get("pubmedID"), doc.get("p_source"),
                doc.get("species"), doc.get("basis"),
                doc.get("source_extracted_definition"), doc.get("source_generated_definition"),
                doc.get("target_extracted_definition"), doc.get("target_generated_definition"), 
                doc.get("entity1"), doc.get("entity2"),
                doc.get("entity1type"), doc.get("entity2type"), doc.get("edge")
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
            #print("[DEBUG] Empty query received. Redirecting to 'not_found.html'")
            return render_template('not_found.html', search_term='DEFAULT')

        if len(query) > 0:
            my_search = query.upper().split(';')
            trimmed_search = [keyword.strip() for keyword in my_search if keyword.strip()]

            #print(f"[DEBUG] Raw query: '{query}' | Parsed search terms: {trimmed_search}")
            #print(f"[DEBUG] Search type: {search_type}")

            # Profile MongoDB query
            query_start = time.time()
            collection = db["all_dic"]
            elements, forSending, elementsAb, node_fa, preview = find_terms(
                trimmed_search, collection, search_type
            )
            #print(f"[DEBUG] find_terms execution time: {time.time() - query_start:.2f} seconds")
            #print(f"[DEBUG] Results - elements: {len(elements)}, forSending: {len(forSending)}, preview: {len(preview)}")

            if forSending:
                # Profile data processing
                process_start = time.time()
                updatedElements = process_network(elements)
                #cytoscape_js_code = generate_cytoscape_js(updatedElements, elementsAb, node_fa,my_search[0])

                summaryText = make_text(forSending)
                print(f"[DEBUG] Data processing time: {time.time() - process_start:.2f} seconds")

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
                    #cytoscape_js_code=cytoscape_js_code,
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
                #print(f"[DEBUG] Rendering time: {time.time() - render_start:.2f} seconds")
                #print(f"[DEBUG] Total execution time: {time.time() - start_time:.2f} seconds")
                return response
            else:
                #print(f"[DEBUG] No results found for query: '{query}' with search_type: '{search_type}'")
                #print(f"[DEBUG] Elements: {len(elements)}, forSending: {len(forSending)}, Preview: {len(preview)}")
                return render_template('not_found.html', search_term=query)

        #print(f"[DEBUG] Query length zero or invalid input: '{query}'")
        return render_template('not_found.html', search_term=query)

    return search_route


def generate_search_route2(search_type):
    """
    Grabs 'uid' from request.args, loads from cache, 
    displays 'gene.html' or 'not_found.html' accordingly.
    """
    def search_route(query, entity_type):
        #print(f"[DEBUG] Search triggered for query: '{query}', entity_type: '{entity_type}', search_type: '{search_type}'")

        categories = [value for key, value in request.args.items() if key.startswith('category_')]
        uid = request.args.get('uid')

        if not uid:
            #print("[DEBUG] Missing 'uid' in request.")
            return "Error: No unique_id provided in ?uid=."
        if uid not in cache:
            #print(f"[DEBUG] 'uid' {uid} not found in cache.")
            return "Error: This search data is not available or may have expired."

        stored_data = cache[uid]
        elements = stored_data["elements"]
        forSending = stored_data["forSending"]
        elementsAb = stored_data["elementsAb"]
        node_fa = stored_data["node_fa"]
        preview = stored_data["preview"]
        summaryText = stored_data["summaryText"]

        #print(f"[DEBUG] Cache hit for UID: {uid}")
        #print(f"[DEBUG] Cached element count: {len(elements)}, forSending: {len(forSending)}")

        # Filter
        filtered_forSending = [
            g for g in forSending
            if ((g.id.upper() == query.upper() and g.idtype.upper() == entity_type.upper()) or
                (g.target.upper() == query.upper() and g.targettype.upper() == entity_type.upper()))
        ]

        #print(f"[DEBUG] Filtered forSending count: {len(filtered_forSending)}")

        filtered_elements = []
        for e in elements:
            #print(e[0:])
            if ((e[0] == query and e[1] == entity_type) or
                (e[2] == query and e[3] == entity_type)):
                filtered_elements.append(e)

        #print(f"[DEBUG] Filtered elements count: {len(filtered_elements)}")

        updatedElements = process_network(filtered_elements)
        cytoscape_js_code = generate_cytoscape_js(updatedElements, elementsAb, node_fa)
        patterns_title = f"{query.upper()} [{entity_type.upper()}]" if entity_type else query.upper()

        if filtered_forSending:
            #print(f"[DEBUG] Rendering gene.html for: {patterns_title}")
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
            #print(f"[DEBUG] No matching entities found for query: '{query}' with type: '{entity_type}'")
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
            cytoscape_js_code = generate_cytoscape_js(updatedElements, elementsAb, node_fa, my_search[0])
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
    