
'''
This module contains the routes for searching.
'''
from flask import Blueprint
import sys 

# -- Setting up the utils path module -- 
sys.path.append('utils')

# -- Importing custom utilities --
from utils.search import generate_search_route,generate_search_route2,generate_multi_search_route,generate_search_route3

term_searches = Blueprint('term_searches', __name__)
# -- Creating a new Blueprint for results --
term_results = Blueprint('term_results', __name__)
# -- Constants --
#DATABASE = pickle.load(open('allDic2', 'rb'))
#ABBREVIATIONS = pickle.load(open('abbreviations', 'rb'))
#FUNCANNOTATE = pickle.load(open('fa', 'rb'))

# -- Generating the routes via function factories:
normal = generate_search_route('normal')
exact = generate_search_route('exact')
alias = generate_search_route('alias')
substring = generate_search_route('substring')
non_alpha = generate_search_route('non-alphanumeric')
paired_entity = generate_search_route3('paired_entity')

# -- Adding the routes --
term_searches.add_url_rule('/normal', endpoint = 'normal', view_func = normal, methods = ['POST'])
term_searches.add_url_rule('/exact', endpoint = 'exact', view_func = exact, methods = ['POST'])
term_searches.add_url_rule('/alias', endpoint = 'alias', view_func = alias, methods = ['POST'])
term_searches.add_url_rule('/substring', endpoint = 'substring', view_func = substring, methods = ['POST'])
term_searches.add_url_rule('/non_alpha', endpoint = 'non_alpha', view_func = non_alpha, methods = ['POST'])

# -- Generating the routes via function factories:
normal_results = generate_search_route2('normal')
exact_results = generate_search_route2('exact')
alias_results = generate_search_route2('alias')
substring_results = generate_search_route2('substring')
non_alpha_results = generate_search_route2('non-alphanumeric')
paired_entity_results = generate_search_route3('paired_entity')

normal_results_multi = generate_multi_search_route('normal')
exact_results_multi = generate_multi_search_route('exact')  
alias_results_multi = generate_multi_search_route('alias')
substring_results_multi = generate_multi_search_route('substring')
non_alpha_results_multi = generate_multi_search_route('non-alphanumeric')
paired_entity_results_multi = generate_multi_search_route('paired_entity')



# -- Adding the routes --
term_results.add_url_rule('/normal/<query>/results/<entity_type>', endpoint='normal_results', view_func=normal_results, methods=['POST'])
term_results.add_url_rule('/exact/<query>/results/<entity_type>', endpoint='exact_results', view_func=exact_results, methods=['POST'])
term_results.add_url_rule('/alias/<query>/results/<entity_type>', endpoint='alias_results', view_func=alias_results, methods=['POST'])
term_results.add_url_rule('/substring/<query>/results/<entity_type>', endpoint='substring_results', view_func=substring_results, methods=['POST'])
term_results.add_url_rule('/non_alpha/<query>/results/<entity_type>', endpoint='non_alpha_results', view_func=non_alpha_results, methods=['POST'])
term_results.add_url_rule('/paired_entity/<query>/results', endpoint='paired_entity_results', view_func=paired_entity_results, methods=['POST'])


term_results.add_url_rule(
    '/normal/<path:multi_query>/results',
    endpoint='normal_results_multi',
    view_func=normal_results_multi,
    methods=['GET', 'POST']
)

term_results.add_url_rule(
    '/exact/<path:multi_query>/results',
    endpoint='exact_results_multi',
    view_func=exact_results_multi,
    methods=['POST']
)

term_results.add_url_rule(
    '/alias/<path:multi_query>/results',
    endpoint='alias_results_multi',
    view_func=alias_results_multi,
    methods=['POST']
)

term_results.add_url_rule(
    '/substring/<path:multi_query>/results',
    endpoint='substring_results_multi',
    view_func=substring_results_multi,
    methods=['POST']
)

term_results.add_url_rule(
    '/non_alpha/<path:multi_query>/results',
    endpoint='non_alpha_results_multi',
    view_func=non_alpha_results_multi,
    methods=['POST']
)

term_results.add_url_rule(
    '/paired_entity/<path:multi_query>/results',
    endpoint='paired_entity_results_multi',
    view_func=paired_entity_results_multi,
    methods=['POST']
)