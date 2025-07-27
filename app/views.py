from fileinput import filename
import matplotlib.pyplot as plt
import matplotlib.patches as pt
import matplotlib as mpl
mpl.use('Agg')

import cv2 as cv
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
from sklearn.cluster import SpectralClustering
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import numpy as np
import os
import json
import base64
from io import BytesIO

def process_image(img, n_clusters=4, clustering_method='kmeans', color_space='rgb'):
    """
    Process image and extract color palette with customizable parameters
    """
    # Convert color space if needed
    if color_space == 'hsv':
        img = cv.cvtColor(img, cv.COLOR_RGB2HSV)
    elif color_space == 'lab':
        img = cv.cvtColor(img, cv.COLOR_RGB2LAB)
    
    # Reshape image for clustering
    img_reshaped = img.reshape(-1, 3)
    
    # Apply clustering method
    if clustering_method == 'kmeans':
        clt = KMeans(n_clusters=n_clusters, random_state=42)
    elif clustering_method == 'minibatch':
        clt = MiniBatchKMeans(n_clusters=n_clusters, random_state=42)
    elif clustering_method == 'spectral':
        # For spectral clustering, we need to sample the data
        sample_size = min(1000, len(img_reshaped))
        indices = np.random.choice(len(img_reshaped), sample_size, replace=False)
        clt = SpectralClustering(n_clusters=n_clusters, random_state=42)
        clt.fit(img_reshaped[indices])
        # Get cluster centers using k-means on the full data
        temp_kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        temp_kmeans.fit(img_reshaped)
        clt.cluster_centers_ = temp_kmeans.cluster_centers_
    else:
        clt = KMeans(n_clusters=n_clusters, random_state=42)
    
    clt.fit(img_reshaped)
    palette = get_palette(clt, color_space)
    
    return palette, clt

def get_palette(clusters, color_space='rgb'):
    """
    Extract color palette from clustering results
    """
    palette = []
    for idx, centers in enumerate(clusters.cluster_centers_):
        if color_space == 'hsv':
            # Convert HSV back to RGB for display
            hsv_color = centers.astype(np.uint8).reshape(1, 1, 3)
            rgb_color = cv.cvtColor(hsv_color, cv.COLOR_HSV2RGB)
            r, g, b = rgb_color[0, 0] / 255.0
        elif color_space == 'lab':
            # Convert LAB back to RGB for display
            lab_color = centers.astype(np.uint8).reshape(1, 1, 3)
            rgb_color = cv.cvtColor(lab_color, cv.COLOR_LAB2RGB)
            r, g, b = rgb_color[0, 0] / 255.0
        else:
            r, g, b = centers / 255.0
        
        # Ensure values are in valid range
        r, g, b = max(0, min(1, r)), max(0, min(1, g)), max(0, min(1, b))
        palette.append((r, g, b))
    
    return palette

def create_palette_image(img, palette):
    """
    Create a visualization of the original image and extracted palette
    """
    fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [4, 1]})
    
    # Display original image
    ax[0].imshow(img, extent=[-img.shape[1]/2., img.shape[1]/2., -img.shape[0]/2., img.shape[0]/2.])
    
    # Create palette visualization
    num_colors = len(palette)
    for idx, color in enumerate(palette):
        rectangle = pt.Rectangle((0.1 + idx * 0.8/num_colors, 0.4), 0.7/num_colors, 1, color=color)
        ax[1].add_patch(rectangle)
    
    ax[0].axis('off')
    ax[1].axis('off')
    fig.tight_layout(pad=0.9, h_pad=0.5)
    
    # Resize figure
    zoom = 0.5
    w, h = fig.get_size_inches()
    fig.set_size_inches(w * zoom, h * zoom)
    
    return fig

def rgb_to_hex(r, g, b):
    """Convert RGB values to hex color code"""
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

def get_color_details(palette):
    """Get detailed color information for each color in palette"""
    color_details = []
    for i, (r, g, b) in enumerate(palette):
        hex_code = rgb_to_hex(r, g, b)
        color_details.append({
            'index': i + 1,
            'hex': hex_code,
            'rgb': f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})",
            'r': int(r*255),
            'g': int(g*255),
            'b': int(b*255)
        })
    return color_details

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'app/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/process-image", methods=["POST"])
def process_image_api():
    """
    API endpoint for processing images with AJAX
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == "":
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif'}), 400
        
        # Get parameters from request
        color_count = int(request.form.get('colorCount', 4))
        clustering_method = request.form.get('clusteringMethod', 'kmeans')
        color_space = request.form.get('colorSpace', 'rgb')
        
        # Validate parameters
        color_count = max(2, min(12, color_count))  # Clamp between 2-12
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process image
        img = cv.imread(file_path)
        if img is None:
            return jsonify({'error': 'Could not read image file'}), 400
        
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        
        # Extract palette
        palette, clusters = process_image(img, color_count, clustering_method, color_space)
        
        # Create palette visualization
        fig = create_palette_image(img, palette)
        
        # Save processed image
        processed_filename = f"processed_{filename}"
        processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        fig.savefig(processed_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        # Get color details
        color_details = get_color_details(palette)
        
        return jsonify({
            'success': True,
            'original_image': filename,
            'processed_image': processed_filename,
            'palette': color_details,
            'color_count': color_count,
            'clustering_method': clustering_method,
            'color_space': color_space
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

@app.route("/api/export-palette", methods=["POST"])
def export_palette():
    """
    API endpoint for exporting palette data
    """
    try:
        data = request.get_json()
        palette = data.get('palette', [])
        export_format = data.get('format', 'css')
        
        if export_format == 'css':
            css_output = "/* YourPalette Generated CSS */\n"
            for i, color in enumerate(palette):
                css_output += f".color-{i+1} {{\n"
                css_output += f"    background-color: {color['hex']};\n"
                css_output += f"    color: {color['hex']};\n"
                css_output += "}\n\n"
            return jsonify({'css': css_output})
        
        elif export_format == 'json':
            return jsonify({'json': json.dumps(palette, indent=2)})
        
        else:
            return jsonify({'error': 'Invalid export format'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Export error: {str(e)}'}), 500

@app.route("/", methods=["POST"])
def uploads():
    """
    Legacy endpoint for traditional form uploads
    """
    if 'file' not in request.files:
        flash("No file part")
        return redirect(request.url)
    
    file = request.files["file"]
    if file.filename == "":
        flash("No image selected for uploading")
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_url)
        
        img = cv.imread(file_url)
        if img is None:
            flash("Could not read image file")
            return redirect(request.url)
        
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        
        # Get parameters (default values for legacy support)
        color_count = int(request.form.get('colorCount', 4))
        clustering_method = request.form.get('clusteringMethod', 'kmeans')
        color_space = request.form.get('colorSpace', 'rgb')
        
        # Process image
        palette, clusters = process_image(img, color_count, clustering_method, color_space)
        
        # Create and save visualization
        fig = create_palette_image(img, palette)
        fig.savefig(file_url, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        return render_template("index.html", filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True, threaded=True)
