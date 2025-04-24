import pickle
from utils.search import find_terms

def test_entity_page_button_catalogue_should_render(client):
    response = client.get('/catalogue')
    assert b'<div class=\'button-group hollow\' style="padding-top: 10px; padding-bottom: 10px;">' in response.data

def test_entity_page_table_and_pagination_should_render(client):
    response = client.get('/catalogue')
    assert b'<table>' in response.data
    assert b'<ul class="pagination text-center">' in response.data

def test_all_catalogue_entities_should_be_searchable(client):
    cata_dict, all_dic = pickle.load(open('cata2', 'rb'))[1], pickle.load(open('allDic2', 'rb'))
    entities = []
    for i in cata_dict:
        entities.extend(cata_dict[i])
    diff = set(entities).difference(set(list(all_dic.keys())))

    assert len(diff) == 0