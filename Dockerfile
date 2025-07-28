FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy environment file first for better caching
COPY environment-ci.yml .

# Create conda environment
RUN conda env create -f environment-ci.yml

# Make RUN commands use the conda environment
SHELL ["conda", "run", "-n", "palette", "/bin/bash", "-c"]

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p app/static/uploads

# Set environment variables
ENV FLASK_APP=app/views.py
ENV FLASK_ENV=development
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Run the application using conda
CMD ["conda", "run", "-n", "palette", "python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080"] 