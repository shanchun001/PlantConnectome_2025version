import re
from flask import Blueprint, render_template
import sys
import logging
import time
from pymongo import DESCENDING
from collections import defaultdict

sys.path.append('utils')

from utils.mongo import db
from utils.text import make_text
from utils.search import Gene
from utils.cytoscape import process_network, generate_cytoscape_js

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[logging.FileHandler("author_search.log"), logging.StreamHandler()]
)

author_search_results = Blueprint('author_search_results', __name__)

def standardize_author_name(query):
    replacements = {
        "ä": "ae", "ö": "oe", "ü": "ue",
        "ß": "ss", "é": "e", "ô": "o",
        "î": "i", "ç": "c"
    }
    query = ''.join(replacements.get(c.lower(), c) for c in query).upper()

    parts = query.strip().split()
    if not parts:
        return ''

    suffixes = {'JR', 'SR', 'II', 'III', 'IV'}
    last_part = parts[-1]

    if last_part in suffixes and len(parts) >= 3:
        last_name = ' '.join(parts[:-2])
        initials = parts[-2]
    elif len(last_part) <= 3 and last_part.isalpha():
        last_name = ' '.join(parts[:-1])
        initials = last_part.replace('.', '')
    else:
        first_names = parts[:-1]
        last_name = parts[-1]
        initials = ''.join(name[0] for name in first_names).replace('.', '')

    return f"{last_name} {initials}".strip()
from flask import Blueprint, render_template, request
import logging
import time
import re
from pymongo import DESCENDING

from utils.mongo import db
from utils.text import make_text
from utils.search import Gene
from utils.cytoscape import process_network, generate_cytoscape_js

author_search_results = Blueprint('author_search_results', __name__)

@author_search_results.route('/author/<query>', methods=['GET'])
def author(query):
    start_time = time.time()
    forSending = []
    elements = []
    elementsAb = {}
    elementsFa = {}
    print("🔍 REACHED AUTHOR ROUTE")
    print(f"🔍 QUERY FROM URL: '{query}'")

    my_search = query.strip()
    print(f"🔍 Search term to be used in MongoDB: '{my_search}'")

    if not my_search:
        print("⚠️ Empty search term. Returning not_found.html")
        return render_template('not_found.html', search_term=query)

    authors_collection = db["authors"]
    all_dic_collection = db["all_dic"]

    try:
        # 🔍 Preview match directly from MongoDB
        docs = list(authors_collection.find(
            {"authors": {"$regex": re.escape(my_search), "$options": "i"}},
            {"pubmedID": 1, "_id": 0}
        ))
        print(f"📄 Matched docs from authors collection: {docs}")

        pm_list = [int(doc.get("pubmedID")) for doc in docs if "pubmedID" in doc]
        print(f"📚 Extracted PubMed IDs: {pm_list}")

        num_hits = len(pm_list)
        print(f"✅ Total PubMed hits: {num_hits}")

        if not num_hits:
            print("⚠️ No PMIDs found. Showing empty author.html")
            return render_template('author.html', genes=[], cytoscape_js_code="",
                                   author=query, connectome_count=0,
                                   warning='No publications found.', summary='', search_term=query)

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
        result_cursor = all_dic_collection.find({"pubmedID": {"$in": pm_list}}, projection)
        result = list(result_cursor)
        #print(f"📦 Records found in all_dic: {len(result)}")  
        name_to_types = defaultdict(set)
        for doc in result:
            name_to_types[doc["entity1_disamb"]].add(doc["entity1type_disamb"].lower())
            name_to_types[doc["entity2_disamb"]].add(doc["entity2type_disamb"].lower())

        # —— 3️⃣ Build merged‐type map: merge all names having multiple types —— #
        name_to_merged = {}

        for name, typeset in name_to_types.items():
            if len(typeset) > 1:
                # sort types alphabetically (or any order you like)
                ordered = sorted(typeset)
                name_to_merged[name.lower()] = ", ".join(ordered)
                print(f"Merged types for {name}: {ordered}")
            else:
                # only one type → just use it
                name_to_merged[name.lower()] = next(iter(typeset))


        for doc in result:
            e1 = doc["entity1_disamb"]
            e2 = doc["entity2_disamb"]
            # raw type lowercased for fallback
            raw1 = doc["entity1type_disamb"].lower()
            raw2 = doc["entity2type_disamb"].lower()

            # lookup merged by lowercase name, else fallback
            e1t = name_to_merged.get(e1.lower(), raw1)
            e2t = name_to_merged.get(e2.lower(), raw2)

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


        #forSending = [Gene(*element) for element in elements]
        updatedElements = process_network(elements)
        cytoscape_js_code = generate_cytoscape_js(updatedElements, {}, {})
        summaryText = make_text(forSending)

        end_time = time.time()
        print(f"✅ Author page successfully generated in {end_time - start_time:.2f} seconds")

        return render_template(
            'author.html',
            genes=forSending,
            cytoscape_js_code=cytoscape_js_code,
            author=query,
            connectome_count=num_hits,
            warning='',
            summary=summaryText,
            search_term=query
        )

    except Exception as e:
        print(f"❌ ERROR during author search: {e}")
        return render_template('error.html', message='An unexpected error occurred. Please try again later.', search_term=query)
