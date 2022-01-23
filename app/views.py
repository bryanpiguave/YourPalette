from fileinput import filename
import matplotlib.pyplot as plt
import matplotlib.patches as pt
import matplotlib as mpl
mpl.use('Agg')

import cv2 as cv
from sklearn.cluster import KMeans
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from werkzeug.utils import secure_filename
import numpy as np
import os

def process_image(img, n_clusters ):
    clt =KMeans(n_clusters=n_clusters)
    clt_1 = clt.fit(img.reshape(-1, 3))
    palette=get_palette(clt_1)
    fig, ax = plt.subplots(2, 1,gridspec_kw={'height_ratios': [4,1]})
    ax[0].imshow(img,extent=[-img.shape[1]/2., img.shape[1]/2., -img.shape[0]/2., img.shape[0]/2.] )
    num_colors=len(palette)
    width,height,channels=img.shape
    for idx,color in enumerate(palette):
        rectangle=pt.Rectangle ((0.1+idx*0.8/num_colors,0.4),0.7/num_colors,1,color=color)
        ax[1].add_patch(rectangle)
    ax[0].axis('off') #hide the axis
    ax[1].axis('off')
    fig.tight_layout(pad=0.9,h_pad=0.5)
    zoom = 0.5
    w, h = fig.get_size_inches()
    fig.set_size_inches(w * zoom, h * zoom)
    return fig

def get_palette(clusters):
    palette=[]
    for idx, centers in enumerate(clusters.cluster_centers_): 
        r,g,b=centers/255
        palette.append((r,g,b))
    return palette


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/",methods =["POST"])
def uploads():
    if 'file' not in request.files:
        flash("No file part")
        return redirect(request.url)
    file = request.files["file"]
    if file.filename =="":
        flash("No image selected for uploading")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename =secure_filename(file.filename)
        file_url=os.path.join(app.config['UPLOAD_FOLDER'],filename)
        file.save(file_url)
        img = cv.imread(file_url)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        processed_image =process_image(img,n_clusters=4)       
        processed_image.savefig(file_url)
        return render_template("index.html",filename=filename)
    else:   
       flash('Allowed image types are - png, jpg, jpeg, gif')
       return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)
 


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True,threaded=True)
