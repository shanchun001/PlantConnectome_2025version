NUM_QUESTIONS = 6

def test_help_page_should_be_accessible(client):
    response = client.get('/help')
    assert response.status_code == 200

def test_help_page_title_and_text_should_render(client):
    response = client.get('/help')
    assert b'Help / FAQs' in response.data
    assert b'General Questions & Answers' in response.data

def test_question_accordions_should_load(client):
    '''
    We have a total of 6 questions on this page.  Do change the constant when necessary!
    '''
    response = client.get('/help')
    assert response.data.count(b'<li class = "accordion-item" data-accordion-item>') == NUM_QUESTIONS
    assert response.data.count(b'<div class = "accordion-content" data-tab-content>') == NUM_QUESTIONS



