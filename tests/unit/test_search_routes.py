ROUTE_SEARCHES = {'normal' : 'cesa', 'exact' : 'cesa', 'alias' : 'cesa1', 
                 'substring' : 'cesa', 'non_alpha' : 'cesa', 'author' : 'Marek%20Mutwil', 
                 'title' : '26503768'}

def test_search_routes_should_only_accept_get_requests(client):
    for i in ROUTE_SEARCHES:
        search_url = f'/{i}/{ROUTE_SEARCHES[i]}'
        req_post, req_put, req_get = client.post(search_url), client.put(search_url), client.get(search_url)
        req_patch, req_del = client.patch(search_url), client.delete(search_url)
        
        assert req_post.status_code == 405
        assert req_put.status_code == 405
        assert req_patch.status_code == 405
        assert req_del.status_code == 405
        assert req_get.status_code == 200

def test_search_routes_should_not_be_accessible_by_themselves(client):
    for i in ROUTE_SEARCHES:
        request = client.get(f'/{i}/')
        assert request.status_code == 404

def test_form_actions_should_accept_post_requests(client):
    '''
    400 is okay - we need to know that this route is accessible.
    '''
    response = client.post('/form/author/author')
    assert response.status_code == 400

