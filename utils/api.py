
#Contains API-related information that the api route use...
import json

from flask import jsonify
#from search import find_terms
from mongo import db
from cytoscape import process_network, generate_cytoscape_js
from collections import defaultdict
with open('utils/relationships_by_category_final.json', 'r') as file:
    RELATIONSHIP_CATEGORIES = json.load(file)

def generate_cytoscape_js(elements):
    """
    Optimized CytoscapeJS generation with preloaded categories.
    """
    nodes = set()
    edges = []

    def escape_js_string(value):
        if not value:
            return ''
        return str(value).replace("'", "").replace('"', '').replace('\n', '')
    # 1) Your category map
    category_map = {
        'biological process': [
            'metabolic pathway', 'function', 'pathway', 'signaling pathway',
            'metabolic process', 'cell process', 'biochemical process', 'cellular process',
            'molecular function', 'signalling pathway', 'genetic process', 'biological pathway', 'process'
        ],
        'cell/organ/organism': [
            'organism', 'organ', 'subcellular compartment', 'tissue', 'cell type',
            'organelle', 'virus', 'organelles', 'cell structure', 'plant', 'organism part'
        ],
        'chemical': [
            'metabolite', 'molecule', 'compound', 'chemical', 'hormone', 'phytohormone',
            'polysaccharide', 'material', 'polymer', 'chemical structure', 'biopolymer',
            'chemical compound', 'plant hormone', 'chemical group'
        ],
        'gene identifier': ['gene identifier'],
        'gene/protein': [
            'gene', 'protein', 'mutant', 'protein complex', 'enzyme', 'protein domain',
            'genetic element', 'gene family', 'protein family', 'protein structure', 'peptide',
            'protein motif', 'enzyme activity', 'protein region', 'gene feature', 'gene region',
            'gene structure', 'protein feature', 'transcription factor', 'gene cluster',
            'gene group', 'promoter', 'subunit', 'transcript', 'gene element', 'allele',
            'protein sequence', 'protein modification', 'post-translational modification',
            'genetic locus', 'protein subunit', 'genes', 'qtl', 'protein function',
            'amino acid residue', 'histone modification', 'protein fragment', 'receptor',
            'genetic event', 'protein kinase', 'protein class', 'protein group',
            'gene product', 'antibody', 'proteins', 'protein interaction', 'gene module'
        ],
        'genomic/transcriptomic feature': [
            'genomic region', 'genome', 'amino acid', 'genomic feature', 'dna sequence',
            'rna', 'sequence', 'mutation', 'chromosome', 'gene expression', 'genetic material',
            'genotype', 'genomic element', 'genetic marker', 'epigenetic mark',
            'genetic variation', 'regulatory element', 'epigenetic modification',
            'dna element', 'mirna', 'genomic location', 'subfamily', 'dna', 'activity',
            'genetic feature', 'sequence motif', 'genetic variant', 'motif', 'mrna',
            'residue', 'region', 'genomic sequence', 'cis-element', 'clade', 'accession',
            'plasmid', 'genomic data', 'cultivar', 'genomic event', 'genomic resource',
            'ecotype', 'marker', 'lncrna', 'genetic construct', 'sequence feature',
            'genus', 'genetic concept'
        ],
        'method': [
            'method', 'technique', 'tool', 'database', 'software', 'dataset', 'concept',
            'study', 'description', 'model', 'modification', 'location', 'author',
            'measurement', 'experiment', 'researcher', 'mechanism', 'system', 'feature',
            'parameter', 'algorithm', 'event', 'reaction', 'resource', 'interaction',
            'device', 'metric', 'technology', 'network', 'construct', 'vector', 'category',
            'data', 'research', 'geographical location', 'document', 'analysis', 'person',
            'project', 'research field', 'researchers', 'gene network', 'relationship'
        ],
        'phenotype': ['phenotype'],
        'treatment': [
            'treatment', 'environment', 'condition', 'time', 'environmental factor',
            'disease', 'developmental stage', 'time point', 'stress', 'geographic location',
            'abiotic stress', 'time period'
        ],
    }    
    # 2) Invert to alias → category
    alias_to_category = {
        alias.lower(): category
        for category, aliases in category_map.items()
        for alias in aliases
    }

    # 3) Lookup helper
    def get_category(type_str: str) -> str:
        if not type_str:
            return 'NA'

        # Split the string by comma and normalize each item
        types = [t.strip().lower() for t in type_str.split(',') if t.strip()]
        if not types:
            return 'NA'

        # Get categories for each item
        categories = {alias_to_category.get(t, 'NA') for t in types}

        # If there's more than one unique category or any are 'NA', return 'NA'
        if len(categories) > 1 or 'NA' in categories:
            return 'NA'

        return categories.pop()

    # 4) Revised format_node
    def format_node(disamb_name, disamb_type, original_name, original_type):
        category_disamb   = get_category(disamb_type.lower())
        category_original = get_category(original_type.lower())
        return (
            f"{escape_js_string(disamb_name)}|"
            f"{escape_js_string(disamb_type)}|{category_disamb.upper()}|"
            f"{escape_js_string(original_name)}|"
            f"{escape_js_string(original_type)}|{category_original.upper()}"
        )

    def get_relationship_category(interaction):
        interaction_upper = interaction.upper()
        for category, relationships in RELATIONSHIP_CATEGORIES.items():
            if interaction_upper in relationships:
                return category
        return "NA"

    for i, edge in enumerate(elements):
        # Add nodes with disamb and original types
        #print(format_node(edge["source"], edge["sourcetype"], edge["source2"], edge["sourcetype2"]))
        nodes.add(format_node(edge["source"], edge["sourcetype"], edge["source2"], edge["sourcetype2"]))
        nodes.add(format_node(edge["target"], edge["targettype"], edge["target2"], edge["targettype2"]))

        edges.append(f"{{data:{{id: 'edge{i}', source: '{escape_js_string(edge['source'])}', sourcetype: '{escape_js_string(edge['sourcetype'])}', target: '{escape_js_string(edge['target'])}', targettype: '{escape_js_string(edge['targettype'])}', interaction: '{escape_js_string(edge['interaction'])}', category: '{escape_js_string(get_relationship_category(edge['interaction']))}', p_source: '{escape_js_string(edge['p_source'])}', pmid: '{escape_js_string(edge['pmid'])}', species: '{escape_js_string(edge['species'])}', basis: '{escape_js_string(edge['basis'])}', source_extracted_definition: '{escape_js_string(edge['source_extracted_definition'])}', source_generated_definition: '{escape_js_string(edge['source_generated_definition'])}', target_extracted_definition: '{escape_js_string(edge['target_extracted_definition'])}', target_generated_definition: '{escape_js_string(edge['target_generated_definition'])}', originalsource: '{escape_js_string(edge['source2'])}', originalsourcetype: '{escape_js_string(edge['sourcetype2'])}', originaltarget: '{escape_js_string(edge['target2'])}', originaltargettype: '{escape_js_string(edge['targettype2'])}', originalinteraction: '{escape_js_string(edge['interaction2'])}', originalcategory: '{escape_js_string(get_relationship_category(edge['interaction2']))}'}}")    
    return edges


class Gene:
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


######################
import time
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os
import pandas as pd
genes = db["all_dic"]

REPLACEMENTS = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "é": "e", "ô": "o", "î": "i", "ç": "c"}
def make_text(elements):
    """
    Optimized text generation for summary display.
    """
    pubmedLink = '<span class="pubmed-link" data-pubmed-id="%s">%s</span>'
    topicDic = defaultdict(lambda: defaultdict(list))
    nodeSentenceDegree = defaultdict(lambda: defaultdict(int))
    nodeDegree = defaultdict(int)

    for i in elements:
        node_id = f"{i.id} [{i.idtype}]"
        target = f"{i.target} [{i.targettype}]"
        topicDic[node_id][i.inter_type].append((target, i.p_source))
        nodeSentenceDegree[node_id][i.inter_type] += 1
        nodeDegree[node_id] += 1

    sorted_nodes = sorted(nodeDegree, key=nodeDegree.get, reverse=True)
    save = []

    for node in sorted_nodes:
        for relation in sorted(nodeSentenceDegree[node], key=nodeSentenceDegree[node].get, reverse=True):
            for target, pubmed_id in topicDic[node][relation]:
                pubmed_ref = pubmed_id
                sentence = (
                    f"{node} "
                    f"{relation} "
                    f"{target} "
                    f"(PMID: {pubmed_ref})."
                )
                save.append(f"{sentence}")

    return ''.join(save)
def find_terms(my_search, genes, search_type):


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
    # 4) 'substring' =>  (regex)
    # -----------------------------
    elif search_type == 'substring':
        print("Substring search:", my_search)
        function_start_time = time.time()

        # 1️⃣ Build the MongoDB substring‑excluding‑exact query
        escaped_patterns = [re.escape(word) for word in my_search]
        combined_or_regex  = "(" + "|".join(escaped_patterns) + ")"
        combined_nor_regex = "(" + "|".join(escaped_patterns) + ")"

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
                pattern = re.compile(rf"(?<![\w\s]){re.escape(word)}(?![\s])", re.IGNORECASE)
                

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
                        

    else:
        raise Exception(f"Invalid search_type: {search_type}")

    end_time = time.time()
    function_elapsed_time = end_time - function_start_time
    loop_elapsed_time = end_time - loop_start_time
    print(f"Function Elapsed time: {function_elapsed_time:.4f} seconds")
    print(f"Loop Elapsed time: {loop_elapsed_time:.4f} seconds")

    return list(set(elements)), forSending

def generate_term_api_route(query_type):    
    #Returns a function meant to be used a view handler in the APIs.
    def api_route(query):
        if len(query)>2:
            forSending, elements, summary = [], [], ''
            all_dic_collection = db["all_dic"]    
            results = find_terms([query], all_dic_collection, query_type)
            elements.extend(results[0]) ; forSending.extend(results[1])
            elements, papers, summary = list(set(elements)), list({ i.publication for i in forSending }), make_text(forSending)
            cytoscape_elements = generate_cytoscape_js(process_network(elements))#generate_cytoscape_elements(process_network(elements))        
        return jsonify({
            #'extracted_definitions' : elementsFa,
            #'generated_definitions' : elementsAb,
            'cytoscape_entity_relationship_data' : cytoscape_elements,
            #'cytoscape_relationships_basis_definitions': cytoscape_elements[1],
            'text_summary' : summary,
            'publications' : papers
        })
    
    return api_route


gene_list= []
summary_file = []
search_type = 'alias'
genes = db["all_dic"]

'''
def main():
    data_list = []
    max_workers = os.cpu_count()
    print(f"Using {max_workers} workers")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_gene, gene) for gene in gene_list[0:100]]

        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing genes"):
            result = future.result()
            if result:  # Only add the result if it was successful
                data_list.append(result)

    with open('summary_file_everything.json', 'w') as json_file:
        json.dump(data_list, json_file, indent=4)
    print(f"Processed {len(data_list)} genes successfully")

if __name__ == "__main__":
    main()
'''