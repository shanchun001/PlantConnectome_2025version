NUM_FORMS = 3

def test_home_page_should_be_accessible(client):
    response = client.get('/')
    assert response.status_code == 200

def test_right_help_panel_should_render(client):
    '''
    Blank for now - fill out when changes are merged!
    '''
    pass 

def test_search_forms_should_render(client):
    response = client.get('/')
    assert response.data.count(b'<form') == NUM_FORMS
