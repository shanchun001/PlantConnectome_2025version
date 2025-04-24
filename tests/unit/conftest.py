import pytest, os, sys

root_path = os.path.dirname(os.path.abspath(__file__))
sub_path = os.path.abspath(os.path.join(root_path, "../../"))
sys.path.insert(0, sub_path)

from app import app

# Set up the fixture for unit testing here - import this in subsequent tests!
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
