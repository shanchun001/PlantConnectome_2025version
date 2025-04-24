from utils.search import find_terms

# == TESTING VARIABLES ==
TEST_DICT = {'cheesecake'.upper() : [('cheesecake', 'is', 'good', '1'), ('cheesecake', 'is', 'cheesy', '2'), ('cheesecake', 'is', 'great', '3')],
             'burger'.upper() : [('burger', 'contains', 'meat', '4'), ('burger', 'complements', 'soda', '5'), ('burger', 'causes', 'obesity', '6')],
             'chocolate'.upper() : [('chocolate', 'has', 'polyphenols', '7')],
             'cesa1'.upper() : [('cesa1', 'is an alias of', 'cesa', '8')],
             'chocolate1'.upper() : [('hey', 'hey', 'hey', '9')],
             'chocolate sauce'.upper() : [('chocolate sauce', 'begets', 'ice cream', '10')]}

def test_exact_search_should_return_exact_matches():
    right, wrong = list(TEST_DICT.keys()), ['ches', 'burg', 'choco']
    for i in right:
        elements, forSending = find_terms(i, TEST_DICT, 'exact')
        assert len(elements) and len(forSending)

    for i in wrong:
        elements, forSending = find_terms(i, TEST_DICT, 'exact')
        assert not len(elements) and not len(forSending)

def test_alias_search_should_return_aliases():
    right, wrong = 'cesa1', 'blahblahblah'
    elements, forSending = find_terms(right, TEST_DICT, 'alias')
    assert len(elements) and len(forSending)

    elements, forSending = find_terms(wrong, TEST_DICT, 'alias')
    assert not len(elements) and not len(forSending)

def test_substring_search_should_find_substrings():
    right, wrong = ['chees', 'choco', 'bu'], ['laet', 'sehc', 'ub']
    for i in right:
        elements, forSending = find_terms(i, TEST_DICT, 'substring')
        assert len(elements) and len(forSending)
    
    for i in wrong:
        elements, forSending = find_terms(i, TEST_DICT, 'substring')
        assert not len(elements) and not len(forSending)

def test_nonalpha_search_should_return_nonalpha_results():
    elements, _ = find_terms('chocolate', TEST_DICT, 'non-alphanumeric')
    assert 'chocolate1' not in [i[0] for i in elements]

def test_default_search_should_return_terms_containing_query():
    elements, forSending = find_terms('chocolate', TEST_DICT, 'default')
    assert len(elements) and len(forSending)


