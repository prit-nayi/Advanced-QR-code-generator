# QR Code Generator Website - Technical Documentation

## Project Overview
A full-stack web application that generates customizable QR codes with logo integration capabilities. Built with Flask backend and HTML/CSS/JS frontend.

## Architecture
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python Flask with qrcode/pyqrcode libraries
- **Image Processing**: Pillow (PIL) for logo integration
- **Communication**: RESTful API with JSON responses

## Key Features

### 1. QR Code Types
- URL, Text, Contact (vCard), WiFi, Email, Phone, SMS
- Each type has specific data formatting rules

### 2. Customization Options
- Size: 100px to 1000px (slider control)
- Error Correction: L (7%), M (15%), Q (25%), H (30%)
- Colors: Predefined schemes + custom color picker
- Logo Integration: Embed logos into QR codes

### 3. Output Formats
- PNG: Raster format for web use
- SVG: Vector format for scaling

## Technical Implementation

### Frontend Architecture

#### State Management
```javascript
let selectedType = 'url';
let selectedErrorCorrection = 'M';
let selectedColorScheme = 'default';
let selectedSize = 300;
let uploadedImage = null;
```

#### API Communication
```javascript
async function generateQR(data) {
    const response = await fetch('/api/generate-qr', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return await response.json();
}
```

#### File Upload Handling
```javascript
function handleFileUpload(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        uploadedImage = e.target.result;
        updatePreview();
    };
    reader.readAsDataURL(file);
}
```

### Backend Architecture

#### Flask Application Setup
```python
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import qrcode
import pyqrcode
from PIL import Image
import io
import base64

app = Flask(__name__)
CORS(app)
```

#### Core QR Generation
```python
def generate_qr_code(content, qr_type, size, error_correction, 
                     foreground_color, background_color):
    qr = qrcode.QRCode(
        version=None,
        error_correction=getattr(qrcode.constants, f'ERROR_CORRECT_{error_correction}'),
        box_size=10,
        border=4,
    )
    
    # Add data based on type
    if qr_type == 'url':
        qr.add_data(content)
    elif qr_type == 'contact':
        qr.add_data(f"BEGIN:VCARD\nVERSION:3.0\nFN:{content}\nEND:VCARD")
    
    qr.make(fit=True)
    return qr.make_image(fill_color=foreground_color, back_color=background_color)
```

## API Endpoints

### 1. Generate QR Code
```http
POST /api/generate-qr
{
    "content": "https://example.com",
    "qrType": "url",
    "size": 300,
    "errorCorrection": "M",
    "foregroundColor": "#000000",
    "backgroundColor": "#FFFFFF",
    "backgroundImage": "data:image/png;base64,..."
}
```

### 2. Download QR Code
```http
POST /api/download-qr
{
    "content": "https://example.com",
    "qrType": "url",
    "size": 300,
    "errorCorrection": "M",
    "foregroundColor": "#000000",
    "backgroundColor": "#FFFFFF",
    "format": "png"
}
```

### 3. Health Check
```http
GET /api/health
```

## Logo Integration Feature

### Technical Process:
1. **Frontend**: Converts uploaded image to base64
2. **Backend**: Decodes base64 to PIL Image object
3. **Processing**: Resizes logo to 25% of QR code size
4. **Integration**: Adds white background for contrast, centers logo
5. **Output**: Returns integrated QR code as base64

### Code Implementation:
```python
def integrate_logo(qr_img, logo_data):
    # Decode base64 logo data
    logo_bytes = base64.b64decode(logo_data.split(',')[1])
    logo_img = Image.open(io.BytesIO(logo_bytes))
    
    # Convert QR to RGBA for transparency
    if qr_img.mode != 'RGBA':
        qr_img = qr_img.convert('RGBA')
    
    # Calculate dimensions
    qr_width, qr_height = qr_img.size
    logo_size = min(qr_width, qr_height) // 4  # 25% of QR size
    
    # Resize and process logo
    logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    if logo_img.mode != 'RGBA':
        logo_img = logo_img.convert('RGBA')
    
    # Create white background for logo area
    white_bg = Image.new('RGBA', (logo_size, logo_size), (255, 255, 255, 255))
    white_bg.paste(logo_img, (0, 0), logo_img.split()[3] if len(logo_img.split()) == 4 else None)
    
    # Paste logo onto QR code
    result_img = qr_img.copy()
    logo_x = (qr_width - logo_size) // 2
    logo_y = (qr_height - logo_size) // 2
    result_img.paste(white_bg, (logo_x, logo_y), white_bg)
    
    return result_img
```

## Error Handling

### Frontend Error Handling:
```javascript
try {
    const result = await generateQR(data);
    if (result.success) {
        displayQRCode(result.qrCode);
    } else {
        showError(result.error);
    }
} catch (error) {
    showError('Failed to generate QR code. Please try again.');
}
```

### Backend Error Handling:
```python
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False, 'error': 'Invalid request data'}), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500
```

## Security Considerations

### Input Validation:
- Content length limits (10,000 characters max)
- File size restrictions (5MB max)
- File type validation (images only)
- QR type validation

### CORS Configuration:
```python
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:5000'])
```

## Performance Optimizations

### Frontend:
- Debounced preview updates (prevents excessive API calls)
- Lazy loading of UI components
- Image compression for uploads

### Backend:
- Efficient image processing with PIL
- Memory management for large images
- Async processing for complex operations

## Deployment

### Development:
```bash
cd projects/qr-code-generator
pip install -r requirements.txt
python app.py
```

### Production:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Interview Questions & Answers

### 1. "Explain the architecture"
**Answer:** "Client-server architecture with Flask backend and HTML/CSS/JS frontend. Frontend handles UI interactions and sends API requests. Backend processes requests using Python QR libraries and returns generated QR codes. RESTful API design with clear separation of concerns."

### 2. "How does logo integration work?"
**Answer:** "Uses PIL to process uploaded images. Logo is resized to 25% of QR size, white background added for contrast, centered within QR code. Maintains scannability through error correction and size limitations. Handles base64 image data with comprehensive error handling."

### 3. "What challenges did you face?"
**Answer:** "QR library issues (pyqrcode file requirements), CORS problems between frontend/backend, complex image processing for logo integration, and comprehensive error handling for both user inputs and system failures."

### 4. "How do you ensure QR scannability with logos?"
**Answer:** "Limit logo size to 25%, use high error correction (H - 30%), place logo in center where error correction is strongest, add white background for contrast, and recommend testing generated QR codes."

### 5. "What security measures?"
**Answer:** "Input validation for content and file uploads, CORS configuration, file size/type restrictions, error handling to prevent information leakage, and rate limiting for production deployment."

### 6. "How would you scale this?"
**Answer:** "Load balancing with multiple server instances, Redis caching for generated QR codes, CDN for static assets, database for user preferences, microservices architecture, and Docker containerization."

### 7. "Testing strategies?"
**Answer:** "Unit tests for QR generation logic, integration tests for API endpoints, UI tests for user interactions, performance tests for load testing, and security tests for input validation."

### 8. "Most complex feature?"
**Answer:** "Logo integration was most complex - required understanding of image processing, QR error correction, transparency handling, and careful positioning while maintaining scannability."

### 9. "Performance optimizations?"
**Answer:** "Debounced preview updates, image compression, async processing, caching strategies, lazy loading, and efficient image processing with PIL."

### 10. "Error handling approach?"
**Answer:** "Comprehensive error handling on both frontend and backend, graceful degradation for failed operations, user-friendly error messages, and logging for debugging."

This documentation provides a complete technical overview of the QR code generator website, suitable for interview preparation and understanding the system's architecture and implementation details. 