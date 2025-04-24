'''
This module contains the route(s) needed to search based on an author's name.
'''
from flask import Blueprint, request, render_template
import sys
sys.path.append('utils')
from utils.search import Gene
from utils.cytoscape import process_network, generate_cytoscape_js
from utils.text import make_text
from utils.mongo import db
from Bio import Entrez, Medline

title_searches = Blueprint('title_searches', __name__)

@title_searches.route('/title/<query>', methods=['GET'])
def title_search(query):
    try:
        my_search = query
    except:
        my_search = '24051094'
    pmids = []
    for part in my_search.split(';'):
        for token in part.split():
            try:
                pmids.append(int(token))
            except ValueError:
                continue
    try:
        Entrez.email = "mutwil@gmail.com"  # ✅ replace with your real email
        handle = Entrez.efetch(db="pubmed",
                               id=",".join(map(str, pmids)),
                               rettype="medline",
                               retmode="text")
        records = Medline.parse(handle)
        title_map = {int(rec.get("PMID")): rec.get("TI", "No title found")
                     for rec in records}
        handle.close()
    except Exception as e:
        # on failure, fall back to empty titles
        title_map = {pmid: "Title fetch error" for pmid in pmids}
        app.logger.warning(f"Entrez title fetch failed: {e}")
    all_dic_collection = db["all_dic"]
    forSending = []
    elements = []
    elementsAb = {}
    elementsFa = {}
    if pmids:
        hits = []
        result = all_dic_collection.find({"pubmedID": {"$in": pmids}})
        for doc in result:
            e1, e1t = doc["entity1_disamb"], doc["entity1type_disamb"]
            e2, e2t = doc["entity2_disamb"], doc["entity2type_disamb"]
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
            hits.append(doc.get("pubmedID"))

        updatedElements = process_network(elements)
        cytoscape_js_code = generate_cytoscape_js(updatedElements, elementsAb, elementsFa)
        summaryText = make_text(forSending)
        title=[]
        for pmid in pmids:
            title.append( title_map.get(pmid, "Unknown title"))
        titles_str = '; '.join(title)
        return render_template('paper.html', genes=forSending, cytoscape_js_code=cytoscape_js_code,
                               number_papers=len(set(hits)), search_term=query, summary=summaryText, is_node=False, paper_title= titles_str
)
    else:
        return render_template('not_found.html', search_term=query)
