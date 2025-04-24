def test_api_routes_should_only_accept_get_requests(client):
    for i in ['normal', 'exact', 'alias', 'substring', 'non_alpha']:
        right, wrong = client.get(f'/api/{i}/cesa'), client.post(f'/api/{i}/cesa')
        assert right.status_code == 200
        assert wrong.status_code == 405
    
    right, wrong = client.get('/api/author/Marek%20Mutwil'), client.post('/api/author/Marek%20Mutwil')
    assert right.status_code == 200
    assert wrong.status_code == 405

    right, wrong = client.get('/api/title/26503768'), client.post('/api/title/26503768')
    assert right.status_code == 200
    assert wrong.status_code == 405

def test_api_should_return_json(client):
    response = client.get('/api/normal/cesa')
    assert response.headers['Content-Type'] == 'application/json'
