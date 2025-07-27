// YourPalette JavaScript - Interactive functionality

$(document).ready(function() {
    // Initialize variables
    let selectedFile = null;
    let currentPalette = null;
    
    // Color count slider functionality
    $('#colorCount').on('input', function() {
        const value = $(this).val();
        $('#colorCountDisplay').text(value);
    });
    
    // File input change handler
    $('#fileInput').on('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            selectedFile = file;
            showImagePreview(file);
            $('#submitBtn').prop('disabled', false);
        }
    });
    
    // Drag and drop functionality
    const uploadArea = $('#uploadArea');
    
    uploadArea.on('dragover', function(e) {
        e.preventDefault();
        $(this).addClass('drag-over');
    });
    
    uploadArea.on('dragleave', function(e) {
        e.preventDefault();
        $(this).removeClass('drag-over');
    });
    
    uploadArea.on('drop', function(e) {
        e.preventDefault();
        $(this).removeClass('drag-over');
        
        const files = e.originalEvent.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                selectedFile = file;
                $('#fileInput')[0].files = files;
                showImagePreview(file);
                $('#submitBtn').prop('disabled', false);
            } else {
                showAlert('Please select an image file.', 'danger');
            }
        }
    });
    
    // Submit button click handler
    $('#submitBtn').on('click', function() {
        if (!selectedFile) {
            showAlert('Please select an image first.', 'warning');
            return;
        }
        
        processImage();
    });
    
    // Image preview function
    function showImagePreview(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            $('#imagePreview').attr('src', e.target.result);
            $('#previewCard').removeClass('d-none');
        };
        reader.readAsDataURL(file);
    }
    
    // Process image with AJAX
    function processImage() {
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('colorCount', $('#colorCount').val());
        formData.append('clusteringMethod', $('#clusteringMethod').val());
        formData.append('colorSpace', $('#colorSpace').val());
        
        // Show progress bar
        $('#progressBar').removeClass('d-none');
        $('#submitBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>Processing...');
        
        $.ajax({
            url: '/api/process-image',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    currentPalette = response.palette;
                    displayResults(response);
                    showAlert('Image processed successfully!', 'success');
                } else {
                    showAlert('Error processing image: ' + response.error, 'danger');
                }
            },
            error: function(xhr) {
                let errorMsg = 'An error occurred while processing the image.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                }
                showAlert(errorMsg, 'danger');
            },
            complete: function() {
                $('#progressBar').addClass('d-none');
                $('#submitBtn').prop('disabled', false).html('<i class="fas fa-magic me-2"></i>Extract Palette');
            }
        });
    }
    
    // Display results
    function displayResults(response) {
        // Update original image
        const originalImg = $('<img>')
            .attr('src', `/display/${response.original_image}`)
            .addClass('img-fluid rounded shadow-sm')
            .attr('alt', 'Original Image');
        
        $('.col-md-6:first img').replaceWith(originalImg);
        
        // Display palette
        displayPalette(response.palette);
        
        // Show color details
        displayColorDetails(response.palette);
        
        // Show export options
        $('#exportCard').removeClass('d-none');
    }
    
    // Display color palette
    function displayPalette(palette) {
        const container = $('#paletteContainer');
        container.empty();
        
        palette.forEach((color, index) => {
            const colorBox = $(`
                <div class="color-box" data-index="${index}" style="background-color: ${color.hex};">
                    <div class="color-info">
                        <span class="color-hex">${color.hex}</span>
                        <button class="btn btn-sm btn-light copy-btn" data-color="${color.hex}">
                            <i class="fas fa-copy"></i>
                        </button>
                    </div>
                </div>
            `);
            container.append(colorBox);
        });
        
        // Add copy functionality
        $('.copy-btn').on('click', function(e) {
            e.stopPropagation();
            const colorHex = $(this).data('color');
            copyToClipboard(colorHex);
            showAlert(`Copied ${colorHex} to clipboard!`, 'success');
        });
    }
    
    // Display color details
    function displayColorDetails(palette) {
        const container = $('#colorDetails');
        container.empty();
        
        palette.forEach((color, index) => {
            const colorDetail = $(`
                <div class="col-md-4 col-sm-6 mb-3">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <div class="color-preview mb-2" style="background-color: ${color.hex}; height: 60px; border-radius: 8px;"></div>
                            <h6 class="card-title">Color ${color.index}</h6>
                            <p class="card-text">
                                <strong>Hex:</strong> ${color.hex}<br>
                                <strong>RGB:</strong> ${color.rgb}<br>
                                <strong>Values:</strong> R:${color.r}, G:${color.g}, B:${color.b}
                            </p>
                            <button class="btn btn-outline-primary btn-sm copy-color" data-color="${color.hex}">
                                <i class="fas fa-copy me-1"></i>Copy
                            </button>
                        </div>
                    </div>
                </div>
            `);
            container.append(colorDetail);
        });
        
        $('#colorDetailsCard').removeClass('d-none');
        
        // Add copy functionality to detail cards
        $('.copy-color').on('click', function() {
            const colorHex = $(this).data('color');
            copyToClipboard(colorHex);
            showAlert(`Copied ${colorHex} to clipboard!`, 'success');
        });
    }
    
    // Copy to clipboard function
    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
        }
    }
    
    // Export palette functions
    window.exportPalette = function(format) {
        if (!currentPalette) {
            showAlert('No palette to export. Please process an image first.', 'warning');
            return;
        }
        
        $.ajax({
            url: '/api/export-palette',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                palette: currentPalette,
                format: format
            }),
            success: function(response) {
                if (format === 'css') {
                    downloadFile(response.css, 'palette.css', 'text/css');
                } else if (format === 'json') {
                    downloadFile(response.json, 'palette.json', 'application/json');
                }
                showAlert(`${format.toUpperCase()} export completed!`, 'success');
            },
            error: function(xhr) {
                let errorMsg = 'Export failed.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                }
                showAlert(errorMsg, 'danger');
            }
        });
    };
    
    // Download file function
    function downloadFile(content, filename, contentType) {
        const blob = new Blob([content], { type: contentType });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }
    
    // Show alert function
    function showAlert(message, type) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-info-circle me-2"></i>${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Remove existing alerts
        $('.alert').remove();
        
        // Add new alert
        $('.container-fluid').append(alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            $('.alert').fadeOut();
        }, 5000);
    }
    
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Add CSS for drag and drop
    $('<style>')
        .prop('type', 'text/css')
        .html(`
            .upload-area {
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                padding: 2rem;
                text-align: center;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .upload-area:hover, .upload-area.drag-over {
                border-color: #007bff;
                background-color: #f8f9fa;
            }
            .color-box {
                height: 80px;
                border-radius: 8px;
                margin: 5px;
                position: relative;
                cursor: pointer;
                transition: transform 0.2s ease;
            }
            .color-box:hover {
                transform: scale(1.05);
            }
            .color-info {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0,0,0,0.7);
                color: white;
                padding: 5px;
                border-radius: 0 0 8px 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .color-hex {
                font-family: monospace;
                font-weight: bold;
            }
            .copy-btn {
                padding: 2px 6px;
                font-size: 0.8rem;
            }
            .palette-container {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 1rem;
            }
        `)
        .appendTo('head');
}); 