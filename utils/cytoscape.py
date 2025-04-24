'''
This module contains helper functions needed to generate the CytoscapeJS graph.
'''
#import networkx as nx
import json
import pandas as pd

def edgeConverter(elements): #Convert Edges to default dictionary format 
    updatedElements = []
    for i in elements:
        updatedElements.append({"source": str(i[0]).replace("'", "").replace('"', '').replace('\n', ''),
                                "sourcetype": str(i[1]).replace("'", "").replace('"', '').replace('\n', ''), 
                                "target": str(i[2]).replace("'", "").replace('"', '').replace('\n', ''), 
                                "targettype": str(i[3]).replace("'", "").replace('"', '').replace('\n', ''), 
                                "interaction": str(i[4]).replace("'", "").replace('"', '').replace('\n', ''),
                                "p_source":str(i[5]).replace("'", "").replace('"', '').replace('\n', ''), 
                                "pmid":str(i[6]).replace("'", "").replace('"', '').replace('\n', ''),
                                "species":str(i[7]).replace("'", "").replace('"', '').replace('\n', ''), #newly added
                                "basis":str(i[8]).replace("'", "").replace('"', '').replace('\n', ''), #newly added
                                "source_extracted_definition":str(i[9]).replace("'", "").replace('"', '').replace('\n', ''), #newly added
                                "source_generated_definition":str(i[10]).replace("'", "").replace('"', '').replace('\n', ''), #newly added
                                "target_extracted_definition":str(i[11]).replace("'", "").replace('"', '').replace('\n', ''), #newly added
                                "target_generated_definition":str(i[12]).replace("'", "").replace('"', '').replace('\n', ''), #newly added
                                "source2":str(i[13]).replace("'", "").replace('"', '').replace('\n', ''), #newly added
                                "target2":str(i[14]).replace("'", "").replace('"', '').replace('\n', ''), #newly added
                                "sourcetype2":str(i[15]).replace("'", "").replace('"', '').replace('\n', ''), #newly added
                                "targettype2":str(i[16]).replace("'", "").replace('"', '').replace('\n', ''), #newly added
                                "interaction2":str(i[17]).replace("'", "").replace('"', '').replace('\n', '') #newly added
                                })
    return updatedElements 

def process_network(elements):
    """
    Optimized processing of elements to generate nodes and edges.
    """

    # Deduplicate elements using a set
    elements = list({tuple(e) for e in elements})

    # If the dataset is manageable, skip complex graph operations
    if len(elements) <= 100000:
        return edgeConverter(elements)  # Directly convert elements to CytoscapeJS format

    # For large datasets, process using a graph
    G = nx.MultiDiGraph()

    # Add edges in bulk
    for e in elements:
        G.add_edge(
            e[0], e[2],  # disamb source and target
            sourcetype=e[1],
            targettype=e[3],
            relation=e[4],  # disamb interaction
            p_source=e[5],
            pmid=e[6],
            species=e[7],
            basis=e[8],
            source_extracted_definition=e[9],
            source_generated_definition=e[10],
            target_extracted_definition=e[11],
            target_generated_definition=e[12],
            
            # Add original values too
            source2=e[13],
            target2=e[14],
            sourcetype2=e[15],
            targettype2=e[16],
            interaction2=e[17]
        )

    # Filter the graph to keep only relevant nodes
    G, ref = nodeDegreeFilter(G)

    # Convert filtered graph to CytoscapeJS or desired format
    return graphConverter(G, ref)



with open('utils/relationships_by_category_final.json', 'r') as file:
    RELATIONSHIP_CATEGORIES = json.load(file)

def generate_cytoscape_js(elements, ab, fa):
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

        edges.append(f"""{{
            data: {{
                id: 'edge{i}',
                source: '{escape_js_string(edge["source"])}',
                sourcetype: '{escape_js_string(edge["sourcetype"])}',
                target: '{escape_js_string(edge["target"])}',
                targettype: '{escape_js_string(edge["targettype"])}',
                interaction: '{escape_js_string(edge["interaction"])}',
                category: '{escape_js_string(get_relationship_category(edge["interaction"]))}',
                p_source: '{escape_js_string(edge["p_source"])}',
                pmid: '{escape_js_string(edge["pmid"])}',
                species: '{escape_js_string(edge["species"])}',
                basis: '{escape_js_string(edge["basis"])}',
                source_extracted_definition: '{escape_js_string(edge["source_extracted_definition"])}',
                source_generated_definition: '{escape_js_string(edge["source_generated_definition"])}',
                target_extracted_definition: '{escape_js_string(edge["target_extracted_definition"])}',
                target_generated_definition: '{escape_js_string(edge["target_generated_definition"])}',
                source2: '{escape_js_string(edge["source2"])}',
                sourcetype2: '{escape_js_string(edge["sourcetype2"])}',
                target2: '{escape_js_string(edge["target2"])}',
                targettype2: '{escape_js_string(edge["targettype2"])}',
                interaction2: '{escape_js_string(edge["interaction2"])}',
                category2: '{escape_js_string(get_relationship_category(edge["interaction2"]))}'
            }}
        }}""")

    # Load JS template and fill placeholders
    with open('network.js', 'r') as template_file:
        template = template_file.read()

    return template.replace(
        '_INSERT_NODES_HERE_',
        ', '.join([
            f"{{ data: {{ id: '{node.split('|')[0]}', type: '{node.split('|')[1]}', category: '{node.split('|')[2]}', originalid: '{node.split('|')[3]}', originaltype: '{node.split('|')[4]}', originalcategory: '{node.split('|')[5]}' }} }}"
            for node in nodes
        ])
    ).replace(
        '_INSERT_EDGES_HERE_',
        ', '.join(edges)
    ).replace('REPLACE_AB', json.dumps(ab)).replace('REPLACE_FA', json.dumps(fa))