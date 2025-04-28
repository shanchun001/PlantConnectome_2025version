from flask import Blueprint, jsonify
from Bio import Entrez
import sys
import pickle
import json
sys.path.append('utils')
from utils.api import generate_term_api_route, REPLACEMENTS
from utils.search import Gene, make_abbreviations, make_functional_annotations
from utils.cytoscape import process_network
from utils.mongo import db
from collections import defaultdict
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os
import pandas as pd

api = Blueprint('api', __name__)

# Add these routes in at app.py:
normal_search = generate_term_api_route('normal')
#exact_search = generate_term_api_route('exact')
substring_search = generate_term_api_route('substring')
#alias_search = generate_term_api_route('alias')
#nonalpha_search = generate_term_api_route('non-alphanumeric')
#paired_entity_search = generate_term_api_route('paired_entity')

# Load relationship categories
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

        edges.append({"data": {"id": f"edge{i}", "source": escape_js_string(edge["source"]), "sourcetype": escape_js_string(edge["sourcetype"]), "target": escape_js_string(edge["target"]), "targettype": escape_js_string(edge["targettype"]), "interaction": escape_js_string(edge["interaction"]), "category": escape_js_string(get_relationship_category(edge["interaction"])), "p_source": escape_js_string(edge["pmid"]), "pmid": escape_js_string(edge["p_source"]), "species": escape_js_string(edge["species"]), "basis": escape_js_string(edge["basis"]), "source_extracted_definition": escape_js_string(edge["source_extracted_definition"]), "source_generated_definition": escape_js_string(edge["source_generated_definition"]), "target_extracted_definition": escape_js_string(edge["target_extracted_definition"]), "target_generated_definition": escape_js_string(edge["target_generated_definition"]), "originalsource": escape_js_string(edge["source2"]), "originalsourcetype": escape_js_string(edge["sourcetype2"]), "originaltarget": escape_js_string(edge["target2"]), "originaltargettype": escape_js_string(edge["targettype2"]), "originalinteraction": escape_js_string(edge["interaction2"]), "originalcategory": escape_js_string(get_relationship_category(edge["interaction2"]))}})
    return edges



class Gene:
    def __init__(
        self, disamb_id, disamb_idtype, disamb_target, disamb_targettype,
        edge_disamb, publication, p_source, species, basis,
        source_extracted_definition, source_generated_definition,
        target_extracted_definition, target_generated_definition,
        entity1, entity2, entity1type, entity2type, inter_type
    ):
        self.id = disamb_id
        self.idtype = disamb_idtype
        self.target = disamb_target
        self.targettype = disamb_targettype
        self.edge_disamb = edge_disamb
        self.inter_type = inter_type
        self.publication = publication
        self.p_source = p_source
        self.species = species
        self.basis = basis
        self.source_extracted_definition = source_extracted_definition
        self.source_generated_definition = source_generated_definition
        self.target_extracted_definition = target_extracted_definition
        self.target_generated_definition = target_generated_definition
        self.entity1 = entity1
        self.entity2 = entity2
        self.entity1type = entity1type
        self.entity2type = entity2type

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def getElements(self):
        return (
            self.id, self.idtype, self.target, self.targettype,
            self.edge_disamb or self.inter_type
        )


def make_text(elements):
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
                sentence = (
                    f"{node} {relation} {target} (PMID: {pubmed_id})."
                )
                save.append(sentence)

    return ' '.join(save)


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

    if search_type == 'normal':
        # ... original normal search logic ...
        pass
    elif search_type == 'substring':
        # ... original substring search logic ...
        pass
    else:
        raise Exception(f"Invalid search_type: {search_type}")

    end_time = time.time()
    print(f"Function Elapsed: {end_time - function_start_time:.4f}s")
    print(f"Loop Elapsed: {end_time - loop_start_time:.4f}s")

    return list(set(elements)), forSending


@api.route('/api/author/<query>', methods=['GET'])
def api_author(query):
    try:
        start_time = time.time()

        # Initialize containers
        forSending = []
        elements = []

        # MongoDB collections
        authors_collection = db['authors']
        all_dic_collection = db['all_dic']

        # 🔍 Preview match directly from MongoDB
        docs = list(
            authors_collection.find(
                {"authors": {"$regex": re.escape(query), "$options": "i"}},
                {"pubmedID": 1, "_id": 0}
            )
        )
        print(f"📄 Matched docs from authors collection: {docs}")

        # Extract PubMed IDs
        pm_list = [int(doc.get("pubmedID")) for doc in docs if "pubmedID" in doc]
        print(f"📚 Extracted PubMed IDs: {pm_list}")

        num_hits = len(pm_list)
        print(f"✅ Total PubMed hits: {num_hits}")

        # Projection fields for all_dic
        projection = {
            "entity1": 1, "entity1type": 1, "entity2": 1, "entity2type": 1,
            "edge": 1, "pubmedID": 1, "p_source": 1, "species": 1, "basis": 1,
            "source_extracted_definition": 1, "source_generated_definition": 1,
            "target_extracted_definition": 1, "target_generated_definition": 1,
            "entity1_disamb": 1, "entity2_disamb": 1,
            "entity1type_disamb": 1, "entity2type_disamb": 1,
            "edge_disamb": 1,
            "_id": 0
        }

        # Fetch detailed records
        result_cursor = all_dic_collection.find({"pubmedID": {"$in": pm_list}}, projection)
        result = list(result_cursor)

        # Build name→types map
        name_to_types = defaultdict(set)
        for doc in result:
            name_to_types[doc["entity1_disamb"]].add(doc["entity1type_disamb"].lower())
            name_to_types[doc["entity2_disamb"]].add(doc["entity2type_disamb"].lower())

        # Merge multiple types
        name_to_merged = {}
        for name, typeset in name_to_types.items():
            if len(typeset) > 1:
                ordered = sorted(typeset)
                name_to_merged[name.lower()] = ", ".join(ordered)
                print(f"Merged types for {name}: {ordered}")
            else:
                name_to_merged[name.lower()] = next(iter(typeset))

        # Build Gene objects and raw elements list
        for doc in result:
            e1 = doc["entity1_disamb"]
            e2 = doc["entity2_disamb"]
            raw1 = doc["entity1type_disamb"].lower()
            raw2 = doc["entity2type_disamb"].lower()

            e1t = name_to_merged.get(e1.lower(), raw1)
            e2t = name_to_merged.get(e2.lower(), raw2)

            gene = Gene(
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
            )
            forSending.append(gene)

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

        # Process network and generate outputs
        updatedElements = process_network(elements)
        elements, papers, summary = (
            list(set(elements)),
            list({ i.publication for i in forSending }),
            make_text(forSending)
        )

        cytoscape_js_code = generate_cytoscape_js(updatedElements)
        summaryText = make_text(forSending)

        end_time = time.time()
        print(f"✅ Author page successfully generated in {end_time - start_time:.2f} seconds")

        return jsonify({
            'paper_counts': num_hits,
            'publications': papers,
            'cytoscape_entity_relationship_data': cytoscape_js_code,
            'text_summary': summaryText
        })

    except Exception as e:
        print(f"❌ Error in api_author: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/api/title/<query>', methods=['GET'])
def title_search(query):
    try:
        print('▶ Entered title_search()')
        pmids = [tok for part in query.split(';') for tok in part.split()]
        int_pmids = []
        for pm in pmids:
            try:
                int_pmids.append(int(pm))
            except ValueError:
                print(f"Warning: invalid PMID: {pm}")

        all_dic_collection = db['all_dic']
        docs = []
        forSending = []
        elements   = []         # ← now indented with 8 spaces, same as forSending

        if int_pmids:
            result_list = list(all_dic_collection.find({'pubmedID': {'$in': int_pmids}}))
        else:
            result_list = []

        name_to_types = defaultdict(set)

        for doc in result_list:
            name_to_types[doc["entity1_disamb"]].add(doc["entity1type_disamb"].lower())
            name_to_types[doc["entity2_disamb"]].add(doc["entity2type_disamb"].lower())

        # —— 3️⃣ Build merged-type map: merge all names having multiple types —— #
        name_to_merged = {}
        entity_counts = defaultdict(int)
        entity_connections = defaultdict(set)

        for name, typeset in name_to_types.items():
            if len(typeset) > 1:
                ordered = sorted(typeset)
                name_to_merged[name.lower()] = ", ".join(ordered)
            else:
                name_to_merged[name.lower()] = next(iter(typeset))

        # —— 4️⃣ Second pass: process each document using merged types —— #
        for doc in result_list:
            e1 = doc["entity1_disamb"]
            e2 = doc["entity2_disamb"]

            raw1 = doc["entity1type_disamb"].lower()
            raw2 = doc["entity2type_disamb"].lower()

            e1t = name_to_merged.get(e1.lower(), raw1)
            e2t = name_to_merged.get(e2.lower(), raw2)

            entity_counts[(e1, e1t)] += 1
            entity_counts[(e2, e2t)] += 1
            entity_connections[(e1, e1t)].add((e2, e2t))
            entity_connections[(e2, e2t)].add((e1, e1t))

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

        elements, papers, summary = list(set(elements)),list({ i.publication for i in forSending }), make_text(forSending)

        cytoscape_data = generate_cytoscape_js(process_network(elements))

        return jsonify({
            'cytoscape_entity_relationship_data': cytoscape_data,
            'text_summary': summary,
            'publications' : papers
        })
    except Exception as e:
        print('Error in title_search:', e)
        return jsonify({'error': 'Internal server error'}), 500