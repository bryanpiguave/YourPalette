# YourPalette 🎨

A modern web application that extracts beautiful color palettes from your images using machine learning algorithms. Upload any image and get an automatically generated color palette with customizable extraction options.

![YourPalette Demo](https://user-images.githubusercontent.com/60787494/150698309-dd49316d-4ec2-45b8-8e1d-62bee8787d9f.png)

## ✨ Features

- **Smart Color Extraction**: Uses K-means clustering and other ML algorithms
- **Customizable Options**: Adjust number of colors, clustering method, and color space
- **Modern UI**: Beautiful, responsive interface with drag & drop upload
- **Export Options**: Export palettes as CSS or JSON
- **Interactive Display**: Click colors to copy hex codes
- **Multiple Formats**: Supports PNG, JPG, JPEG, GIF

## 🚀 Quick Installation

### Method 1: Using conda (Recommended)

```bash
# Clone the repository
git clone https://github.com/bryanpiguave/yourpalette.git
cd yourpalette

# Create and activate conda environment
conda env create -f environment.yml
conda activate palette

# Run the application
python app/views.py
```

**Note**: Use `environment.yml` for local development. For CI/CD, use `environment-ci.yml`.

**Note**: If you encounter issues with conda, try these alternative approaches:

**Option A: Create environment manually**
```bash
conda create -n yourpalette python=3.13.5
conda activate yourpalette
conda install -c conda-forge flask numpy scikit-learn matplotlib scipy pillow
pip install opencv-python pytest pytest-flask gunicorn
```

**Option B: Use mamba (faster conda alternative)**
```bash
# Install mamba first: conda install mamba -c conda-forge
mamba env create -f environment.yml
conda activate yourpalette
```

### Method 3: Using Docker

```bash
# Clone the repository
git clone   git@github.com:bryanpiguave/YourPalette.git
cd yourpalette

# Build and run with Docker Compose
docker-compose up --build
```


## 🌐 Usage

1. **Start the application** using one of the installation methods above
2. **Open your browser** and navigate to `http://localhost:8080`
3. **Upload an image** by dragging and dropping or clicking to browse
4. **Customize extraction** options:
   - Number of colors (2-12)
   - Clustering method (K-means, Mini-batch, Spectral)
   - Color space (RGB, HSV, LAB)
5. **Click "Extract Palette"** to generate your color palette
6. **Export or copy** color codes as needed

## 🛠️ Customization Options

- **Number of Colors**: Slider to select 2-12 colors
- **Clustering Method**: 
  - K-Means (default)
  - Mini-Batch K-Means (faster for large images)
  - Spectral Clustering (better for complex patterns)
- **Color Space**:
  - RGB (standard)
  - HSV (better for color-based clustering)
  - LAB (perceptually uniform)

## 📦 Dependencies

### Core Requirements
- Python 3.13.5+
- Flask 2.3.3
- OpenCV 4.8.1
- scikit-learn 1.3.0
- matplotlib 3.7.2
- NumPy 1.24.3


## 🔧 Development

### Setting up Development Environment

```bash
# Clone and setup
git clone git@github.com:bryanpiguave/YourPalette.git
cd yourpalette

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
flake8 app/
```

### Project Structure

```
YourPalette/
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── main.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── uploads/
│   ├── templates/
│   │   └── index.html
│   └── views.py
├── tests/
├── requirements.txt
├── environment.yml
├── docker-compose.yml
├── Dockerfile
└── README.md
```


## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## 📝 API Endpoints

- `GET /` - Main application page
- `POST /` - Upload and process image
- `GET /display/<filename>` - Display processed image

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Conda Environment Creation Issues**
   ```bash
   # If conda env create fails, try:
   conda create -n yourpalette python=3.13.5
   conda activate yourpalette
   conda install -c conda-forge flask numpy scikit-learn matplotlib scipy pillow
   pip install opencv-python pytest pytest-flask gunicorn
   ```

2. **OpenCV Installation Issues**
   ```bash
   pip uninstall opencv-python
   pip install opencv-python-headless
   ```

3. **Matplotlib Backend Issues**
   ```bash
   # Add to your Python script
   import matplotlib
   matplotlib.use('Agg')
   ```

4. **Port Already in Use**
   ```bash
   # Change port in app/views.py
   app.run(host="127.0.0.1", port=8081, debug=True)
   ```

5. **Windows-specific Issues**
   ```bash
   # If conda fails on Windows, try:
   conda install -c conda-forge mamba
   mamba env create -f environment.yml
   ```

For more detailed troubleshooting, see [INSTALL.md](INSTALL.md).

## 📞 Support

- 📧 Email: bpiguave@nd.edu
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/yourpalette/issues)
- 📖 Documentation: [INSTALL.md](INSTALL.md)



