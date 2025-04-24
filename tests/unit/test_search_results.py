def test_search_results_should_return_all_results(client):
    response = client.get('/normal/cesa')
    assert b'Node summary of cesa' in response.data
    assert b'Text summary of the network:' in response.data
    assert b'Table summary of the network:' in response.data

def test_cytoscape_layout_options_button_should_render(client):
    response = client.get('/normal/cesa')
    assert b'<button class="open-button button secondary"' in response.data

def test_cytoscape_graph_search_form_should_render(client):
    response = client.get('/normal/cesa')
    assert b'<form id="node-search-form">' in response.data

def test_interaction_table_and_pagination_should_render(client):
    response = client.get('/normal/cesa')
    assert b"table_results" in response.data
    assert b'<ul class="pagination text-center">' in response.data

def test_author_search_should_show_number_of_publications(client):
    response = client.get('/author/Marek%20Mutwil')
    assert b'paper(s) on the NCBI' in response.data
    assert b'paper(s) on our database' in response.data