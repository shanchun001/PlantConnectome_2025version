from flask import Flask, render_template, request, url_for, redirect, send_from_directory, jsonify, Response, session, request, render_template, redirect, url_for
import os
import time
from datetime import timedelta
from flask_compress import Compress
import openai
import logging
from pymongo import MongoClient
import json
import pandas as pd
# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Update with your actual MongoDB URI
db = client["PlantConnectome"]  # Replace with your DB name
scientific_chunks = db["scientific_chunks"]  # Collection reference


# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


# Importing Blueprints
from routes.preview_author_search import author_search
from routes.author_search import author_search_results

from routes.title_searches import title_searches
from routes.similarity_search import similarity_search
from routes.catalogue_search import catalogue_search
from routes.api import normal_search, substring_search, api
from routes.api import api
from routes.term_searches import (
    normal, exact, alias, substring, non_alpha, paired_entity,
    normal_results, exact_results, normal_results_multi,
    exact_results_multi, alias_results, alias_results_multi,
    substring_results, substring_results_multi,
    non_alpha_results, non_alpha_results_multi,
    paired_entity_results, paired_entity_results_multi
)


# Initialize Flask app
app = Flask(__name__)

# Secure session cookie settings
app.config.update(
    SESSION_COOKIE_SECURE=True,        # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY=True,      # Prevent JavaScript access to cookies
    SESSION_COOKIE_SAMESITE='Lax',     # CSRF protection
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),  # Session lifetime
)

# Disable debug mode in production
app.debug = True

# Initialize Flask-Compress
Compress(app)

# Register Blueprints
app.register_blueprint(author_search)
app.register_blueprint(author_search_results)
app.register_blueprint(title_searches)
app.register_blueprint(similarity_search)
app.register_blueprint(catalogue_search)
app.register_blueprint(api)
# Register dynamic routes within app context
with app.app_context():
    app.add_url_rule('/normal/<path:query>', 'normal', normal, methods=['GET'])
    app.add_url_rule('/exact/<path:query>', 'exact', exact, methods=['GET'])
    #app.add_url_rule('/alias/<path:query>', 'alias', alias, methods=['GET'])
    app.add_url_rule('/substring/<path:query>', 'substring', substring, methods=['GET'])
    #app.add_url_rule('/non_alpha/<path:query>', 'non_alpha', non_alpha, methods=['GET'])
    #app.add_url_rule('/paired_entity/<path:query>', 'paired_entity', paired_entity, methods=['GET'])
    app.add_url_rule('/api/normal/<path:query>', 'api_normal', normal_search, methods=['GET'])
    #app.add_url_rule('/api/exact/<path:query>', 'api_exact', exact_search, methods=['GET'])
    #app.add_url_rule('/api/alias/<path:query>', 'api_alias', alias_search, methods=['GET'])
    app.add_url_rule('/api/substring/<path:query>', 'api_substring', substring_search, methods=['GET'])
    #app.add_url_rule('/api/non_alpha/<path:query>', 'api_non_alpha', nonalpha_search, methods=['GET'])
    #app.add_url_rule('/api/paired_entity/<path:query>', 'api_paired_entity', paired_entity_search, methods=['GET'])

    app.add_url_rule('/normal/<path:query>/results/<entity_type>', 'normal_results', normal_results, methods=['GET'])
    app.add_url_rule('/exact/<path:query>/results/<entity_type>', 'exact_results', exact_results, methods=['GET'])
    app.add_url_rule('/alias/<path:query>/results/<entity_type>', 'alias_results', alias_results, methods=['GET'])
    app.add_url_rule('/substring/<path:query>/results/<entity_type>', 'substring_results', substring_results, methods=['GET'])
    app.add_url_rule('/non_alpha/<path:query>/results/<entity_type>', 'non_alpha_results', non_alpha_results, methods=['GET'])
    app.add_url_rule('/paired_entity/<path:query>/results', 'paired_entity_results', paired_entity_results, methods=['GET'])

    app.add_url_rule('/normal/<path:multi_query>/results', 'normal_results_multi', normal_results_multi, methods=['GET','POST'])
    app.add_url_rule('/exact/<path:multi_query>/results', 'exact_multi', exact_results_multi, methods=['GET','POST'])
    app.add_url_rule('/alias/<path:multi_query>/results', 'alias_multi', alias_results_multi, methods=['GET','POST'])
    app.add_url_rule('/substring/<path:multi_query>/results', 'substring_multi', substring_results_multi, methods=['GET','POST'])
    app.add_url_rule('/non_alpha/<path:multi_query>/results', 'non_alpha_results_multi', non_alpha_results_multi, methods=['GET','POST'])
    app.add_url_rule('/paired_entity/<path:multi_query>/results', 'paired_entity_results_multi', paired_entity_results_multi, methods=['GET'])

# Test route for session verification
@app.route('/test-session', methods=['GET'])
def test_session():
    if 'test_key' in session:
        test_value = session['test_key']
        return jsonify({
            'status': 'success',
            'message': 'Session is working correctly.',
            'test_key': test_value
        })
    else:
        session['test_key'] = 'Session Initialized'
        return jsonify({
            'status': 'initialized',
            'message': 'Session has been set for the first time.'
        })

# Existing routes
@app.route('/', methods=['GET'])

def index():
    try:
        # ------------ preview graph (hard-coded stub) ------------
        nodes = [
  {
    "data": {
      "id": "PLHCA4 [PROTEIN]",
      "type": "protein",
      "category": "GENE/PROTEIN",
      "originalid": "pLhca4",
      "originaltype": "protein",
      "originalcategory": "GENE/PROTEIN",
      "originalId": "pLhca4",
      "originalId_beforedisamb": "pLhca4",
      "type_beforedisamb": "protein"
    }
  },
  {
    "data": {
      "id": "A. THALIANA [ORGANISM]",
      "type": "organism",
      "category": "CELL/ORGAN/ORGANISM",
      "originalid": "A. thaliana",
      "originaltype": "organism",
      "originalcategory": "CELL/ORGAN/ORGANISM",
      "originalId": "A. thaliana",
      "originalId_beforedisamb": "A. thaliana",
      "type_beforedisamb": "organism"
    }
  },
  {
    "data": {
      "id": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
      "type": "gene identifier",
      "category": "GENE IDENTIFIER",
      "originalid": "psad1-1 mutants",
      "originaltype": "mutant",
      "originalcategory": "GENE/PROTEIN",
      "originalId": "(PSAD-1, PSAD1, AT4G02770)-1",
      "originalId_beforedisamb": "psad1-1 mutants",
      "type_beforedisamb": "mutant"
    }
  },
  {
    "data": {
      "id": "130 MOST STRONGLY ATTENUATED GENE(S) [GENE]",
      "type": "gene",
      "category": "GENE/PROTEIN",
      "originalid": "130 most strongly attenuated gene(s)",
      "originaltype": "gene",
      "originalcategory": "GENE/PROTEIN",
      "originalId": "130 most strongly attenuated gene(s)",
      "originalId_beforedisamb": "130 most strongly attenuated gene(s)",
      "type_beforedisamb": "gene"
    }
  },
  {
    "data": {
      "id": "OXIDATION OF PHOTOSYSTEM I (PSI) [PHENOTYPE]",
      "type": "phenotype",
      "category": "PHENOTYPE",
      "originalid": "Oxidation of photosystem I (PSI)",
      "originaltype": "phenotype",
      "originalcategory": "PHENOTYPE",
      "originalId": "Oxidation of photosystem I (PSI)",
      "originalId_beforedisamb": "Oxidation of photosystem I (PSI)",
      "type_beforedisamb": "phenotype"
    }
  },
  {
    "data": {
      "id": "LIGHT-GREEN LEAF COLORATION [PHENOTYPE]",
      "type": "phenotype",
      "category": "PHENOTYPE",
      "originalid": "light-green leaf coloration",
      "originaltype": "phenotype",
      "originalcategory": "PHENOTYPE",
      "originalId": "light-green leaf coloration",
      "originalId_beforedisamb": "light-green leaf coloration",
      "type_beforedisamb": "phenotype"
    }
  },
  {
    "data": {
      "id": "MRNA EXPRESSION OF MOST GENE(S) INVOLVED IN THE LIGHT PHASE OF PHOTOSYNTHESIS [GENE]",
      "type": "gene",
      "category": "GENE/PROTEIN",
      "originalid": "mRNA expression of most gene(s) involved in the light phase of photosynthesis",
      "originaltype": "gene",
      "originalcategory": "GENE/PROTEIN",
      "originalId": "mRNA expression of most gene(s) involved in the light phase of photosynthesis",
      "originalId_beforedisamb": "mRNA expression of most gene(s) involved in the light phase of photosynthesis",
      "type_beforedisamb": "gene"
    }
  },
  {
    "data": {
      "id": "PHOSPHORYLATION OF THYLAKOID PROTEIN(S) [TREATMENT]",
      "type": "treatment",
      "category": "TREATMENT",
      "originalid": "phosphorylation of thylakoid protein(s)",
      "originaltype": "treatment",
      "originalcategory": "TREATMENT",
      "originalId": "phosphorylation of thylakoid protein(s)",
      "originalId_beforedisamb": "phosphorylation of thylakoid protein(s)",
      "type_beforedisamb": "treatment"
    }
  },
  {
    "data": {
      "id": "INCREASED SENSITIVITY TO LIGHT STRESS [PHENOTYPE]",
      "type": "phenotype",
      "category": "PHENOTYPE",
      "originalid": "increased photosensitivity",
      "originaltype": "phenotype",
      "originalcategory": "PHENOTYPE",
      "originalId": "increased sensitivity to light stress",
      "originalId_beforedisamb": "increased photosensitivity",
      "type_beforedisamb": "phenotype"
    }
  },
  {
    "data": {
      "id": "PSI AND PSII POLYPEPTIDES [PROTEIN COMPLEX]",
      "type": "protein complex",
      "category": "GENE/PROTEIN",
      "originalid": "PSI and PSII polypeptides",
      "originaltype": "protein complex",
      "originalcategory": "GENE/PROTEIN",
      "originalId": "PSI and PSII polypeptides",
      "originalId_beforedisamb": "PSI and PSII polypeptides",
      "type_beforedisamb": "protein complex"
    }
  },
  {
    "data": {
      "id": "GROWTH RATE [PHENOTYPE]",
      "type": "phenotype",
      "category": "PHENOTYPE",
      "originalid": "Growth rate",
      "originaltype": "phenotype",
      "originalcategory": "PHENOTYPE",
      "originalId": "Growth rate",
      "originalId_beforedisamb": "Growth rate",
      "type_beforedisamb": "phenotype"
    }
  },
  {
    "data": {
      "id": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
      "type": "gene identifier",
      "category": "GENE IDENTIFIER",
      "originalid": "psad1-1",
      "originaltype": "mutant",
      "originalcategory": "GENE/PROTEIN",
      "originalId": "(PSAD-1, PSAD1, AT4G02770)-1",
      "originalId_beforedisamb": "psad1-1",
      "type_beforedisamb": "mutant"
    }
  },
  {
    "data": {
      "id": "PSAD MRNA AND PROTEIN(S) [GENE]",
      "type": "gene",
      "category": "GENE/PROTEIN",
      "originalid": "PsaD mRNA and protein(s)",
      "originaltype": "gene",
      "originalcategory": "GENE/PROTEIN",
      "originalId": "PsaD mRNA and protein(s)",
      "originalId_beforedisamb": "PsaD mRNA and protein(s)",
      "type_beforedisamb": "gene"
    }
  },
  {
    "data": {
      "id": "PQ POOL [METABOLITE]",
      "type": "metabolite",
      "category": "CHEMICAL",
      "originalid": "PQ pool",
      "originaltype": "metabolite",
      "originalcategory": "CHEMICAL",
      "originalId": "PQ pool",
      "originalId_beforedisamb": "PQ pool",
      "type_beforedisamb": "metabolite"
    }
  },
  {
    "data": {
      "id": "REDUCTION BY ABOUT 60% OF THE SUBUNITS OF THE STROMAL RIDGE OF PSI [PHENOTYPE]",
      "type": "phenotype",
      "category": "PHENOTYPE",
      "originalid": "reduction by about 60% of the subunits of the stromal ridge of PSI",
      "originaltype": "phenotype",
      "originalcategory": "PHENOTYPE",
      "originalId": "reduction by about 60% of the subunits of the stromal ridge of PSI",
      "originalId_beforedisamb": "reduction by about 60% of the subunits of the stromal ridge of PSI",
      "type_beforedisamb": "phenotype"
    }
  },
  {
    "data": {
      "id": "PHOTOSYNTHETIC ELECTRON TRANSPORT [PHENOTYPE, PROCESS]",
      "type": "phenotype, process",
      "category": "NA",
      "originalid": "photosynthetic electron flow",
      "originaltype": "process",
      "originalcategory": "BIOLOGICAL PROCESS",
      "originalId": "Photosynthetic electron transport",
      "originalId_beforedisamb": "photosynthetic electron flow",
      "type_beforedisamb": "process"
    }
  }
]

        edges = [
                {
                    "data": {
                    "id": "edge0",
                    "source": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
                    "sourcetype": "gene identifier",
                    "target": "REDUCTION BY ABOUT 60% OF THE SUBUNITS OF THE STROMAL RIDGE OF PSI [PHENOTYPE]",
                    "targettype": "phenotype",
                    "interaction": "show",
                    "category": "NA",
                    "p_source": "17968587",
                    "pmid": "17968587_results",
                    "species": "Arabidopsis thaliana",
                    "basis": "Literature references to psad1-1 mutant phenotype",
                    "source_extracted_definition": "A specific mutant of Arabidopsis thaliana with photosystem I defects.",
                    "source_generated_definition": "None",
                    "target_extracted_definition": "Significant decrease in specific PSI subunits, impacting its function.",
                    "target_generated_definition": "None",
                    "source2": "PSAD1-1 [MUTANT]",
                    "sourcetype2": "mutant",
                    "target2": "REDUCTION BY ABOUT 60% OF THE SUBUNITS OF THE STROMAL RIDGE OF PSI [PHENOTYPE]",
                    "targettype2": "phenotype",
                    "interaction2": "show",
                    "category2": "NA",
                    "originalsource": "(PSAD-1, PSAD1, AT4G02770)-1",
                    "originaltarget": "reduction by about 60% of the subunits of the stromal ridge of PSI",
                    "originalsource2": "psad1-1",
                    "originaltarget2": "reduction by about 60% of the subunits of the stromal ridge of PSI"
                    }
                },
                {
                    "data": {
                    "id": "edge1",
                    "source": "A. THALIANA [ORGANISM]",
                    "sourcetype": "organism",
                    "target": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
                    "targettype": "gene identifier",
                    "interaction": "mutant",
                    "category": "NA",
                    "p_source": "17968587",
                    "pmid": "17968587_abstract",
                    "species": "None",
                    "basis": "None",
                    "source_extracted_definition": "A flowering plant species commonly known as Arabidopsis thaliana, used in genetic studies.",
                    "source_generated_definition": "None",
                    "target_extracted_definition": "A specific mutant of Arabidopsis thaliana with photosystem I defects.",
                    "target_generated_definition": "None",
                    "source2": "A. THALIANA [ORGANISM]",
                    "sourcetype2": "organism",
                    "target2": "PSAD1-1 [MUTANT]",
                    "targettype2": "mutant",
                    "interaction2": "mutants",
                    "category2": "NA",
                    "originalsource": "A. thaliana",
                    "originaltarget": "(PSAD-1, PSAD1, AT4G02770)-1",
                    "originalsource2": "A. thaliana",
                    "originaltarget2": "psad1-1"
                    }
                },
                {
                    "data": {
                    "id": "edge2",
                    "source": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
                    "sourcetype": "gene identifier",
                    "target": "PSAD MRNA AND PROTEIN(S) [GENE]",
                    "targettype": "gene",
                    "interaction": "affect levels of",
                    "category": "NA",
                    "p_source": "14996217",
                    "pmid": "14996217_abstract",
                    "species": "Arabidopsis thaliana",
                    "basis": "Analysis of PsaD mRNA and protein levels in psad1-1 mutant",
                    "source_extracted_definition": "A mutant allele of the PSAD1 gene, impacting photosystem I stability.",
                    "source_generated_definition": "None",
                    "target_extracted_definition": "mRNA and proteins encoded by the PsaD gene, involved in photosystem I.",
                    "target_generated_definition": "None",
                    "source2": "PSAD1-1 [MUTANT]",
                    "sourcetype2": "mutant",
                    "target2": "PSAD MRNA AND PROTEIN(S) [GENE]",
                    "targettype2": "gene",
                    "interaction2": "affects accumulation of",
                    "category2": "NA",
                    "originalsource": "(PSAD-1, PSAD1, AT4G02770)-1",
                    "originaltarget": "PsaD mRNA and protein(s)",
                    "originalsource2": "psad1-1",
                    "originaltarget2": "PsaD mRNA and protein(s)"
                    }
                },
                {
                    "data": {
                    "id": "edge3",
                    "source": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
                    "sourcetype": "gene identifier",
                    "target": "MRNA EXPRESSION OF MOST GENE(S) INVOLVED IN THE LIGHT PHASE OF PHOTOSYNTHESIS [GENE]",
                    "targettype": "gene",
                    "interaction": "down-regulates",
                    "category": "REPRESSION/INHIBITION/DECREASE/NEGATIVE REGULATION",
                    "p_source": "14996217",
                    "pmid": "14996217_abstract",
                    "species": "Arabidopsis thaliana",
                    "basis": "Analysis of mRNA expression levels in psad1-1 mutant",
                    "source_extracted_definition": "A mutant allele of the PSAD1 gene, impacting photosystem I stability.",
                    "source_generated_definition": "None",
                    "target_extracted_definition": "The transcription levels of genes crucial for the light-dependent reactions of photosynthesis.",
                    "target_generated_definition": "None",
                    "source2": "PSAD1-1 [MUTANT]",
                    "sourcetype2": "mutant",
                    "target2": "MRNA EXPRESSION OF MOST GENE(S) INVOLVED IN THE LIGHT PHASE OF PHOTOSYNTHESIS [GENE]",
                    "targettype2": "gene",
                    "interaction2": "downregulates",
                    "category2": "REPRESSION/INHIBITION/DECREASE/NEGATIVE REGULATION",
                    "originalsource": "(PSAD-1, PSAD1, AT4G02770)-1",
                    "originaltarget": "mRNA expression of most gene(s) involved in the light phase of photosynthesis",
                    "originalsource2": "psad1-1",
                    "originaltarget2": "mRNA expression of most gene(s) involved in the light phase of photosynthesis"
                    }
                },
                {
                    "data": {
                    "id": "edge4",
                    "source": "OXIDATION OF PHOTOSYSTEM I (PSI) [PHENOTYPE]",
                    "sourcetype": "phenotype",
                    "target": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
                    "targettype": "gene identifier",
                    "interaction": "impaired in",
                    "category": "REPRESSION/INHIBITION/DECREASE/NEGATIVE REGULATION",
                    "p_source": "17968587",
                    "pmid": "17968587_abstract",
                    "species": "Arabidopsis thaliana",
                    "basis": "Literature references to PSI oxidation in psad1-1 mutants",
                    "source_extracted_definition": "The process of electron loss in photosystem I, crucial for photosynthesis.",
                    "source_generated_definition": "None",
                    "target_extracted_definition": "A specific mutant of Arabidopsis thaliana with photosystem I defects.",
                    "target_generated_definition": "None",
                    "source2": "OXIDATION OF PHOTOSYSTEM I (PSI) [PHENOTYPE]",
                    "sourcetype2": "phenotype",
                    "target2": "PSAD1-1 [MUTANT]",
                    "targettype2": "mutant",
                    "interaction2": "is impaired in",
                    "category2": "NA",
                    "originalsource": "Oxidation of photosystem I (PSI)",
                    "originaltarget": "(PSAD-1, PSAD1, AT4G02770)-1",
                    "originalsource2": "Oxidation of photosystem I (PSI)",
                    "originaltarget2": "psad1-1"
                    }
                },
                {
                    "data": {
                    "id": "edge5",
                    "source": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
                    "sourcetype": "gene identifier",
                    "target": "INCREASED SENSITIVITY TO LIGHT STRESS [PHENOTYPE]",
                    "targettype": "phenotype",
                    "interaction": "show",
                    "category": "NA",
                    "p_source": "14996217",
                    "pmid": "14996217_abstract",
                    "species": "Arabidopsis thaliana",
                    "basis": "Photosensitivity tests on psad1-1 mutant",
                    "source_extracted_definition": "A mutant allele of the PSAD1 gene, impacting photosystem I stability.",
                    "source_generated_definition": "None",
                    "target_extracted_definition": "A phenotype showing heightened sensitivity to light conditions.",
                    "target_generated_definition": "None",
                    "source2": "PSAD1-1 [MUTANT]",
                    "sourcetype2": "mutant",
                    "target2": "INCREASED PHOTOSENSITIVITY [PHENOTYPE]",
                    "targettype2": "phenotype",
                    "interaction2": "show",
                    "category2": "NA",
                    "originalsource": "(PSAD-1, PSAD1, AT4G02770)-1",
                    "originaltarget": "increased sensitivity to light stress",
                    "originalsource2": "psad1-1",
                    "originaltarget2": "increased photosensitivity"
                    }
                },
                {
                    "data": {
                    "id": "edge6",
                    "source": "PQ POOL [METABOLITE]",
                    "sourcetype": "metabolite",
                    "target": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
                    "targettype": "gene identifier",
                    "interaction": "is over-reduced in",
                    "category": "NA",
                    "p_source": "17968587",
                    "pmid": "17968587_abstract",
                    "species": "Arabidopsis thaliana",
                    "basis": "Literature references to PQ pool reduction in psad1-1 mutants",
                    "source_extracted_definition": "The plastoquinone pool, involved in electron transport in photosynthesis.",
                    "source_generated_definition": "None",
                    "target_extracted_definition": "A specific mutant of Arabidopsis thaliana with photosystem I defects.",
                    "target_generated_definition": "None",
                    "source2": "PQ POOL [METABOLITE]",
                    "sourcetype2": "metabolite",
                    "target2": "PSAD1-1 [MUTANT]",
                    "targettype2": "mutant",
                    "interaction2": "is over-reduced in",
                    "category2": "NA",
                    "originalsource": "PQ pool",
                    "originaltarget": "(PSAD-1, PSAD1, AT4G02770)-1",
                    "originalsource2": "PQ pool",
                    "originaltarget2": "psad1-1"
                    }
                },
                {
                    "data": {
                    "id": "edge7",
                    "source": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
                    "sourcetype": "gene identifier",
                    "target": "PHOSPHORYLATION OF THYLAKOID PROTEIN(S) [TREATMENT]",
                    "targettype": "treatment",
                    "interaction": "analyzed for",
                    "category": "EXPRESSION/DETECTION/IDENTIFICATION",
                    "p_source": "17968587",
                    "pmid": "17968587_intro",
                    "species": "Arabidopsis thaliana",
                    "basis": "Western analysis with pThr-specific antibodies",
                    "source_extracted_definition": "A specific mutant of Arabidopsis thaliana with photosystem I defects.",
                    "source_generated_definition": "None",
                    "target_extracted_definition": "The process of adding phosphate groups to thylakoid proteins.",
                    "target_generated_definition": "None",
                    "source2": "PSAD1-1 [MUTANT]",
                    "sourcetype2": "mutant",
                    "target2": "PHOSPHORYLATION OF THYLAKOID PROTEIN(S) [TREATMENT]",
                    "targettype2": "treatment",
                    "interaction2": "analysed for",
                    "category2": "EXPRESSION/DETECTION/IDENTIFICATION",
                    "originalsource": "(PSAD-1, PSAD1, AT4G02770)-1",
                    "originaltarget": "phosphorylation of thylakoid protein(s)",
                    "originalsource2": "psad1-1",
                    "originaltarget2": "phosphorylation of thylakoid protein(s)"
                    }
                },
                {
                    "data": {
                    "id": "edge8",
                    "source": "PLHCA4 [PROTEIN]",
                    "sourcetype": "protein",
                    "target": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
                    "targettype": "gene identifier",
                    "interaction": "accumulates in",
                    "category": "LOCALIZATION/CONTAINMENT/COMPOSITION",
                    "p_source": "17968587",
                    "pmid": "17968587_results",
                    "species": "Arabidopsis thaliana",
                    "basis": "Western analysis with pThr-specific antibodies",
                    "source_extracted_definition": "Phosphorylated form of Lhca4 protein, involved in light harvesting.",
                    "source_generated_definition": "None",
                    "target_extracted_definition": "Various mutants of Arabidopsis thaliana with the psad1-1 phenotype.",
                    "target_generated_definition": "None",
                    "source2": "PLHCA4 [PROTEIN]",
                    "sourcetype2": "protein",
                    "target2": "PSAD1-1 MUTANTS [MUTANT]",
                    "targettype2": "mutant",
                    "interaction2": "accumulates in",
                    "category2": "LOCALIZATION/CONTAINMENT/COMPOSITION",
                    "originalsource": "pLhca4",
                    "originaltarget": "(PSAD-1, PSAD1, AT4G02770)-1",
                    "originalsource2": "pLhca4",
                    "originaltarget2": "psad1-1 mutants"
                    }
                },
                {
                    "data": {
                    "id": "edge9",
                    "source": "130 MOST STRONGLY ATTENUATED GENE(S) [GENE]",
                    "sourcetype": "gene",
                    "target": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
                    "targettype": "gene identifier",
                    "interaction": "downregulated in",
                    "category": "REPRESSION/INHIBITION/DECREASE/NEGATIVE REGULATION",
                    "p_source": "28808104",
                    "pmid": "28808104_results2",
                    "species": "None",
                    "basis": "None",
                    "source_extracted_definition": "Genes significantly downregulated in pgr5 mutant under high light stress.",
                    "source_generated_definition": "None",
                    "target_extracted_definition": "Arabidopsis mutant with a mutation affecting photosystem I function.",
                    "target_generated_definition": "None",
                    "source2": "130 MOST STRONGLY ATTENUATED GENE(S) [GENE]",
                    "sourcetype2": "gene",
                    "target2": "PSAD1-1 [MUTANT]",
                    "targettype2": "mutant",
                    "interaction2": "downregulated in",
                    "category2": "REPRESSION/INHIBITION/DECREASE/NEGATIVE REGULATION",
                    "originalsource": "130 most strongly attenuated gene(s)",
                    "originaltarget": "(PSAD-1, PSAD1, AT4G02770)-1",
                    "originalsource2": "130 most strongly attenuated gene(s)",
                    "originaltarget2": "psad1-1"
                    }
                },
                {
                    "data": {
                    "id": "edge10",
                    "source": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
                    "sourcetype": "gene identifier",
                    "target": "GROWTH RATE [PHENOTYPE]",
                    "targettype": "phenotype",
                    "interaction": "decreases",
                    "category": "REPRESSION/INHIBITION/DECREASE/NEGATIVE REGULATION",
                    "p_source": "14996217",
                    "pmid": "14996217_abstract",
                    "species": "Arabidopsis thaliana",
                    "basis": "Growth rate measurement under greenhouse conditions",
                    "source_extracted_definition": "A mutant allele of the PSAD1 gene, impacting photosystem I stability.",
                    "source_generated_definition": "None",
                    "target_extracted_definition": "The rate of increase in size or biomass of an organism.",
                    "target_generated_definition": "None",
                    "source2": "PSAD1-1 [MUTANT]",
                    "sourcetype2": "mutant",
                    "target2": "GROWTH RATE [PHENOTYPE]",
                    "targettype2": "phenotype",
                    "interaction2": "decreases",
                    "category2": "REPRESSION/INHIBITION/DECREASE/NEGATIVE REGULATION",
                    "originalsource": "(PSAD-1, PSAD1, AT4G02770)-1",
                    "originaltarget": "Growth rate",
                    "originalsource2": "psad1-1",
                    "originaltarget2": "Growth rate"
                    }
                },
                {
                    "data": {
                    "id": "edge11",
                    "source": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
                    "sourcetype": "gene identifier",
                    "target": "PHOTOSYNTHETIC ELECTRON TRANSPORT [PHENOTYPE, PROCESS]",
                    "targettype": "phenotype, process",
                    "interaction": "affect",
                    "category": "ACTIVATION/INDUCTION/PROMOTION/CAUSATION/RESULT",
                    "p_source": "14996217",
                    "pmid": "14996217_abstract",
                    "species": "Arabidopsis thaliana",
                    "basis": "Measurement of photosynthetic electron flow in psad1-1 mutant",
                    "source_extracted_definition": "A mutant allele of the PSAD1 gene, impacting photosystem I stability.",
                    "source_generated_definition": "None",
                    "target_extracted_definition": "The movement of electrons through the photosynthetic electron transport chain.",
                    "target_generated_definition": "None",
                    "source2": "PSAD1-1 [MUTANT]",
                    "sourcetype2": "mutant",
                    "target2": "PHOTOSYNTHETIC ELECTRON FLOW [PROCESS]",
                    "targettype2": "process",
                    "interaction2": "affect",
                    "category2": "ACTIVATION/INDUCTION/PROMOTION/CAUSATION/RESULT",
                    "originalsource": "(PSAD-1, PSAD1, AT4G02770)-1",
                    "originaltarget": "Photosynthetic electron transport",
                    "originalsource2": "psad1-1",
                    "originaltarget2": "photosynthetic electron flow"
                    }
                },
                {
                    "data": {
                    "id": "edge12",
                    "source": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
                    "sourcetype": "gene identifier",
                    "target": "PSI AND PSII POLYPEPTIDES [PROTEIN COMPLEX]",
                    "targettype": "protein complex",
                    "interaction": "diminished",
                    "category": "NA",
                    "p_source": "14996217",
                    "pmid": "14996217_abstract",
                    "species": "Arabidopsis thaliana",
                    "basis": "Protein level analysis in psad1-1 mutant",
                    "source_extracted_definition": "A mutant allele of the PSAD1 gene, impacting photosystem I stability.",
                    "source_generated_definition": "None",
                    "target_extracted_definition": "Protein complexes involved in the light reactions of photosynthesis.",
                    "target_generated_definition": "None",
                    "source2": "PSAD1-1 [MUTANT]",
                    "sourcetype2": "mutant",
                    "target2": "PSI AND PSII POLYPEPTIDES [PROTEIN COMPLEX]",
                    "targettype2": "protein complex",
                    "interaction2": "decreases levels of",
                    "category2": "NA",
                    "originalsource": "(PSAD-1, PSAD1, AT4G02770)-1",
                    "originaltarget": "PSI and PSII polypeptides",
                    "originalsource2": "psad1-1",
                    "originaltarget2": "PSI and PSII polypeptides"
                    }
                },
                {
                    "data": {
                    "id": "edge13",
                    "source": "(PSAD-1, PSAD1, AT4G02770)-1 [GENE IDENTIFIER]",
                    "sourcetype": "gene identifier",
                    "target": "LIGHT-GREEN LEAF COLORATION [PHENOTYPE]",
                    "targettype": "phenotype",
                    "interaction": "show",
                    "category": "NA",
                    "p_source": "14996217",
                    "pmid": "14996217_abstract",
                    "species": "Arabidopsis thaliana",
                    "basis": "Phenotypic observation of leaf coloration in psad1-1 mutant",
                    "source_extracted_definition": "A mutant allele of the PSAD1 gene, impacting photosystem I stability.",
                    "source_generated_definition": "None",
                    "target_extracted_definition": "A phenotype where leaves exhibit a lighter green color, often due to chlorophyll deficiency.",
                    "target_generated_definition": "None",
                    "source2": "PSAD1-1 [MUTANT]",
                    "sourcetype2": "mutant",
                    "target2": "LIGHT-GREEN LEAF COLORATION [PHENOTYPE]",
                    "targettype2": "phenotype",
                    "interaction2": "show",
                    "category2": "NA",
                    "originalsource": "(PSAD-1, PSAD1, AT4G02770)-1",
                    "originaltarget": "light-green leaf coloration",
                    "originalsource2": "psad1-1",
                    "originaltarget2": "light-green leaf coloration"
                    }
                }
                ]

        preview = {"nodes": nodes, "edges": edges}

        # 👉 pass the *object*, not a pre-dumped string
        return render_template("index.html", preview=preview)

    except Exception as exc:
        logger.exception("Error building index view")
        return "Internal Server Error", 500
    
@app.route('/help', methods=['GET'])
def help():
    '''
    Returns the help page.
    '''
    return render_template('help.html')

@app.route('/features', methods=['GET'])
def features():
    '''
    Renders the features page.
    '''
    try:
        with open('journal_statistics.txt', 'r') as f:
            journals, numbers = f.read().splitlines()
        with open('piechart.txt', 'r') as f:
            piechart = f.read().replace('JOURNALS', journals).replace('NUMBERS', numbers)
        return render_template('features.html', piechart_code=piechart)
    except Exception as e:
        logger.error(f"Error reading statistics files: {str(e)}")
        return "Error loading features.", 500

@app.route("/download")
@app.route("/download.html")
def download_page():
    # Directory where your 10‑row preview CSVs live
    preview_dir = "connectome_files/previews"
    print(f"[DEBUG] Download route called. preview_dir = {preview_dir}")

    def load_preview(filename):
        # Build the .preview.csv filename
        preview_path = os.path.join(preview_dir, filename + ".preview.csv")
        exists = os.path.exists(preview_path)
        print(f"[DEBUG] Looking for preview file: {preview_path}, exists: {exists}")
        if exists:
            # Read only the first 10 rows
            df = pd.read_csv(preview_path, nrows=10)
            print(f"[DEBUG] Loaded preview for {filename}, rows read: {len(df)}")
            return df.to_html(index=False, classes="preview-table")
        else:
            return None

    # Map exactly the keys your template is using
    previews = {
        "KG_PlantConnectome_20250421.csv":
            load_preview("KG_PlantConnectome_20250421.csv"),
        "connectome_agi_pairs_pmid_edge_all_columns_TF.csv":
            load_preview("connectome_agi_pairs_pmid_edge_all_columns_TF.csv"),
    }
    print(f"[DEBUG] previews dict keys: {list(previews.keys())}")

    return render_template("download.html", previews=previews)
@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Process summary route (ensure API keys are loaded securely)
@app.route('/process-summary', methods=['POST'])
def process_summary():
    data = request.json
    summary = data.get('summary')
    user_input = data.get('user_input')
    temperature_input = data.get('temperature', 0.7)
    max_tokens_input = data.get('max_tokens', 512)
    top_p_input = data.get('top_p', 1.0)
    models = data.get('models')

    if not summary:
        return jsonify({"error": "Summary not provided"}), 400

    search_term = data.get('search_term')
    logger.info(f"Search Term: {search_term}")
    logger.info(f"Model used: {models}")

    # Determine which API to use
    if "gpt" in models:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("OpenAI API key not set.")
            return jsonify({"error": "API key not configured."}), 500
        client = openai.OpenAI(api_key=openai_api_key)
    else:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            logger.error("Groq API key not set.")
            return jsonify({"error": "API key not configured."}), 500
        client = openai.OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=groq_api_key,
        )

    def generate_stream():
        try:
            completion = client.chat.completions.create(
                model=models,
                messages=[
                    {"role": "system", "content": (
                        "You are an expert scientific assistant that generates detailed, "
                        "structured scientific reviews based on provided input and PMIDs. "
                        "Your output must follow a multi-section format, ensuring citations "
                        "for every fact are included. Use clear, precise paragraphs, and "
                        "scientific terminology appropriate for publication. Do not summarize "
                        "the information—include all details exactly as provided. "
                        "Be accurate and thorough in your response."
                    )},
                    {"role": "user", "content": summary},
                    {"role": "user", "content": user_input + " If the prompt before this is not related to the input, please ignore it and reply please give a relevant prompt."}
                ],
                temperature=float(temperature_input),
                max_tokens=int(max_tokens_input),
                top_p=float(top_p_input),
                stream=True  # Streaming enabled
            )

            for chunk in completion:
                delta_content = getattr(chunk.choices[0].delta, "content", "")
                if delta_content:
                    yield f"{delta_content}"
                    logger.info(f"Streaming chunk: {delta_content}")
        except Exception as api_error:
            error_message = f"Error occurred during API completion: {str(api_error)}"
            logger.error(error_message)
            yield f"data: {json.dumps({'error': error_message})}\n\n"

    return Response(generate_stream(), content_type='text/event-stream')
# Route to send summary
@app.route('/send-summary', methods=['POST'])
def send_summary():
    data = request.json  # Ensure the request sends JSON
    summary = data.get('summary')
    if not summary:
        return jsonify({'status': 'error', 'message': 'Summary not provided'}), 400

    return jsonify({'status': 'success', 'message': 'Summary received', 'summary': summary})

# Route for form submissions
@app.route('/form/<form_type>/<search_type>', methods=['POST'])
def form(form_type, search_type):
    query = request.form.get(form_type)
    selected_categories = request.form.getlist('category')  # Get selected categories from the query string
    if selected_categories:
        categories = {f'category_{i}': category for i, category in enumerate(selected_categories)}
        return redirect(url_for(search_type, query=query, **categories))
    return redirect(url_for(search_type, query=query))

def get_scientific_chunk(p_source):
    """
    Searches for p_source in the 'scientific_chunks' collection by matching 'custom_id' 
    and retrieves the 'user_content' field.
    
    :param p_source: The ID to search for in 'custom_id'.
    :return: The 'user_content' field if found, else None.
    """
    result = scientific_chunks.find_one({"custom_id": p_source}, {"_id": 0, "user_content": 1})
    return result["user_content"] if result else None

@app.route('/process-text-withoutapi', methods=['POST'])
def process_text_withoutapi():
    data = request.get_json()
    p_source=data.get('p_source')
    text_input = get_scientific_chunk(p_source)
    return jsonify({"text_input": text_input})
@app.route('/process-text', methods=['POST'])
def process_text():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON received"}), 400
    p_source=data.get('p_source')
    text_input = get_scientific_chunk(p_source)
    source = data.get('source', '')
    interaction = data.get('interaction', '')
    target = data.get('target', '')

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OpenAI API key missing!")  # Debugging
        return jsonify({"error": "OpenAI API key is missing"}), 500

    try:
        client = openai.OpenAI(api_key=openai_api_key)

        def generate_stream():
            try:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a scientific expert in molecular biology and bioinformatics. "
                            "Your role is to validate whether a given source-target interaction is correctly derived from the provided scientific text. "
                            "Use logical reasoning, scientific knowledge, and textual evidence to assess the accuracy of the claimed relationship. "
                            "If the relationship is correct, confirm it with an explanation. If incorrect or uncertain, explain why and suggest improvements. "
                            "Always extract and explicitly quote relevant phrases from the scientific text to support your analysis."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"**Scientific Text:**\n\"\"\"\n{text_input}\n\"\"\"\n\n"
                                f"**Proposed Relationship:**\n"
                                f"- **Source:** {source}\n"
                                f"- **Interaction:** {interaction}\n"
                                f"- **Target:** {target}\n\n"
                                "### Task:\n"
                                "- Validate whether the provided interaction correctly reflects the relationship described in the text.\n"
                                "- Quote the **exact statements** from the text that support or contradict the relationship.\n"
                                "- If the relationship is incorrect or ambiguous, explain why and suggest a more accurate interpretation."
                    },
                    {
                        "role": "user",
                        "content": (
                            "Respond in the following structured format:\n"
                            "- **Validation Status**: (✅ Correct / ❓ Uncertain / ❌ Incorrect)\n"
                            "- **Supporting Evidence**: Quote exact sentences from the scientific text that support or contradict the relationship.\n"
                            "- **Explanation**: Justify the assessment based on the quoted evidence.\n"
                            "- **Suggested Correction** (if applicable)\n"
                            "Ensure your response is clear, structured, and scientifically rigorous."
                        )
                    }
                ],
                    temperature=0,
                    max_tokens=1000,
                    top_p=0,
                    stream=True  # ✅ Enable streaming response
                )

                for chunk in completion:
                    delta_content = chunk.choices[0].delta.content if hasattr(chunk.choices[0].delta, 'content') else ''
                    if delta_content:
                        yield f"{delta_content}"
            except Exception as api_error:
                yield f"Error: {str(api_error)}"

        return Response(generate_stream(), content_type='text/event-stream')

    except openai.error.OpenAIError as api_error:
        print(f"❌ OpenAI API error: {api_error}")  # Debugging
        return jsonify({"error": "OpenAI API error", "details": str(api_error)}), 500

    except Exception as e:
        print(f"❌ Unexpected error: {e}")  # Debugging
        return jsonify({"error": "Unexpected error", "details": str(e)}), 500
@app.route('/send-text', methods=['POST'])
def send_text():
    data = request.json  # Ensure the request sends JSON
    text = data.get('text')
    if not text:
        return jsonify({'status': 'error', 'message': 'Text not provided'}), 400

    return jsonify({'status': 'success', 'message': 'Text received', 'text': text})
@app.route('/openai-edge-synonyms', methods=['POST'])
def openai_edge_synonyms():#changed to semantics
    data = request.get_json(force=True)
    print("Received data:", data)

    # 1) Parse the incoming data
    selected_groups = data.get('selectedGroups', [])
    edge_counts = data.get('edgeCounts', {})  # e.g. { "mapped to": 7, "activate": 3, ... }
    print("Selected Groups:", selected_groups)
    print("Edge Counts:", edge_counts)

    # 2) Build your prompt referencing 'selected_groups' AND 'edge_counts'
    prompt_text = f"""
    The user has selected the following group: {selected_groups}.

    The dataset contains the following interaction types with their respective counts:
    {json.dumps(edge_counts, indent=2)}

    Your task is to find interactions from the list above that best fit the selected group and map the most relevant interaction types based on **semantic similarity**.

    Only return **valid JSON** with this exact structure:
    {{
    "semantic_mappings": {{
        "group_name": ["matching_interaction1", "matching_interaction2", ...]
    }}
    }}

    Make sure that:
    - Each selected group is included in the JSON response.
    - The mapped interactions should **only** come from the provided interaction list.
    - Do **not** invent new interaction types that are not present in the list.
    - Do **not** assign mappings that you are unsure about.
    - There should be no down-regulation for Activation/Induction/Causation/Result.
    """

    try:
        # 3) Call OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        client = openai.OpenAI(api_key=openai_api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_text}],
            temperature=0.0,
            max_tokens=500,
            top_p=0
        )

        # 4) Extract raw GPT text
        model_message = response.model_dump()['choices'][0]['message']['content']
        model_message = model_message.strip()

        # If it starts with ``` then remove them
        if model_message.startswith("```"):
            model_message = model_message.replace("```json", "").replace("```", "").strip()

        synonyms_json = json.loads(model_message)  # ✅ Correct parsing
        print("Parsed synonyms:", synonyms_json)

        # 6) Return synonyms
        return jsonify(synonyms_json)

    except json.JSONDecodeError as e:
        print("JSON decoding error:", e)
        return jsonify({"error": "GPT response was not valid JSON"}), 500
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)