"""
This module contains the route(s) needed to display a preview of available authors and their publication counts,
filtered by a query. Each author entry includes the author's full name as stored in the database.
Clicking the full name directs the user to the detailed author page.
"""
from flask import Blueprint, render_template
from utils.mongo import db
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

author_search = Blueprint('author_search', __name__)

# Preview route that uses only database data.
# It aggregates author names from the "authors" array and sums all occurrences as the DB publication count.
# The result is a list of authors, each with:
#   - full_name: the name stored in the database,
#   - publication_count: the total number of matching records.
# Clicking the full name directs to the detailed author page.
@author_search.route('/preview_author_search/<query>', methods=['GET'])
def preview_author_search(query):
    start_time = time.time()
    logging.info(f"Received preview author search query: '{query}'")
    authors_collection = db["authors"]

    pipeline = [
        # First, discard entire documents that have no chance to match
        {"$match": {"authors": {"$regex": query, "$options": "i"}}},
        
        # Then, replace the authors array with only the matching elements
        {"$set": {
            "authors": {
                "$filter": {
                    "input": "$authors",
                    "as": "author",
                    "cond": {
                        "$regexMatch": {
                            "input": "$$author",
                            "regex": query,
                            "options": "i"
                        }
                    }
                }
            }
        }},
        
        # Remove documents that, after filtering, have an empty authors array
        {"$match": {"authors.0": {"$exists": True}}},
        
        # Now unwind the already filtered authors array
        {"$unwind": "$authors"},
        
        {"$group": {
            "_id": "$authors",
            "publication_count": {"$sum": 1}
        }},
        
        {"$sort": {"_id": 1}}
    ]

    authors_list = []
    try:
        authors_cursor = authors_collection.aggregate(pipeline)
        for doc in authors_cursor:
            full_name = doc["_id"]
            count = doc.get("publication_count", 0)
            authors_list.append({
                "full_name": full_name,
                "publication_count": count
            })
        logging.info(f"DB returned {len(authors_list)} authors matching the query '{query}'")
    except Exception as e:
        logging.error(f"Error during aggregation of authors: {e}")
        authors_list = []

    end_time = time.time()
    logging.info(f"Preview author search processed in {end_time - start_time:.2f} seconds")
    if not authors_list:
        return render_template('not_found_authors.html', search_term=query)
    return render_template(
        'preview_authorsearch.html',
        authors=authors_list,
        search_term=query
    )