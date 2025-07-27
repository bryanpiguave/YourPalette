import pytest
import os
import tempfile
from app.views import app, allowed_file, get_palette, rgb_to_hex, get_color_details
from sklearn.cluster import KMeans
import numpy as np

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test that the index route returns 200."""
    response = client.get('/')
    assert response.status_code == 200

def test_allowed_file():
    """Test file extension validation."""
    assert allowed_file('test.jpg') == True
    assert allowed_file('test.png') == True
    assert allowed_file('test.jpeg') == True
    assert allowed_file('test.gif') == True
    assert allowed_file('test.txt') == False
    assert allowed_file('test.pdf') == False

def test_rgb_to_hex():
    """Test RGB to hex conversion."""
    assert rgb_to_hex(1.0, 0.0, 0.0) == '#ff0000'  # Red
    assert rgb_to_hex(0.0, 1.0, 0.0) == '#00ff00'  # Green
    assert rgb_to_hex(0.0, 0.0, 1.0) == '#0000ff'  # Blue
    assert rgb_to_hex(0.0, 0.0, 0.0) == '#000000'  # Black
    assert rgb_to_hex(1.0, 1.0, 1.0) == '#ffffff'  # White

def test_get_color_details():
    """Test color details generation."""
    palette = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
    details = get_color_details(palette)
    
    assert len(details) == 3
    assert details[0]['hex'] == '#ff0000'
    assert details[0]['rgb'] == 'rgb(255, 0, 0)'
    assert details[0]['r'] == 255
    assert details[0]['g'] == 0
    assert details[0]['b'] == 0

def test_get_palette():
    """Test palette extraction from clustering results."""
    # Create mock clustering results
    mock_clusters = KMeans(n_clusters=3, random_state=42)
    mock_clusters.cluster_centers_ = np.array([
        [255, 0, 0],    # Red
        [0, 255, 0],    # Green
        [0, 0, 255]     # Blue
    ])
    
    palette = get_palette(mock_clusters)
    assert len(palette) == 3
    assert palette[0] == (1.0, 0.0, 0.0)  # Red
    assert palette[1] == (0.0, 1.0, 0.0)  # Green
    assert palette[2] == (0.0, 0.0, 1.0)  # Blue

def test_api_endpoints_exist(client):
    """Test that API endpoints exist."""
    # Test that the API endpoints are accessible (even if they return errors for missing data)
    response = client.post('/api/process-image')
    assert response.status_code in [400, 500]  # Should fail without file
    
    response = client.post('/api/export-palette', json={'palette': [], 'format': 'css'})
    assert response.status_code in [200, 400, 500]  # Should handle the request

def test_display_image_route(client):
    """Test the display image route."""
    response = client.get('/display/test.jpg')
    assert response.status_code == 301  # Redirect status

def test_upload_folder_creation():
    """Test that upload folder is created."""
    # The app should create the upload folder if it doesn't exist
    upload_folder = app.config['UPLOAD_FOLDER']
    assert os.path.exists(upload_folder) or os.access(os.path.dirname(upload_folder), os.W_OK)

def test_app_config():
    """Test app configuration."""
    assert app.config['SECRET_KEY'] == 'your-secret-key-here'
    assert app.config['MAX_CONTENT_LENGTH'] == 16 * 1024 * 1024  # 16MB
    assert 'UPLOAD_FOLDER' in app.config

if __name__ == '__main__':
    pytest.main([__file__]) 