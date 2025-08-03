from flask import Flask, render_template, request, jsonify, send_file
import pyqrcode
import qrcode
from PIL import Image
import io
import os
import json
from datetime import datetime
import base64

app = Flask(__name__)

# QR Code types
QR_TYPES = {
    "URL": "Website Link",
    "Text": "Plain Text",
    "Email": "Email Address",
    "Phone": "Phone Number",
    "SMS": "SMS Message",
    "WiFi": "WiFi Network",
    "Contact": "Contact Information",
    "Location": "Geographic Location",
    "Event": "Calendar Event"
}

# Color schemes
COLOR_SCHEMES = {
    "Classic": ("#000000", "#FFFFFF"),
    "Blue": ("#1e3a8a", "#ffffff"),
    "Green": ("#059669", "#ffffff"),
    "Purple": ("#7c3aed", "#ffffff"),
    "Red": ("#dc2626", "#ffffff"),
    "Custom": ("#000000", "#ffffff")
}

# In-memory storage for demo (in production, use a database)
history = []
settings = {
    'default_size': 10,
    'default_error_correction': 'M',
    'default_color_scheme': 'Classic',
    'auto_save': True,
    'auto_history': True,
    'default_type': 'URL'
}

@app.route('/')
def index():
    """Renders the main QR generator page."""
    return render_template('index.html')

@app.route('/generate-qr', methods=['POST'])
def generate_qr():
    """Handles QR code generation requests."""
    try:
        # Handle both JSON and FormData
        if request.is_json:
            data = request.json
            content = data.get('content', '').strip()
            size = data.get('size', 10)
            error_correction = data.get('errorCorrection', 'M')
            color_scheme = data.get('colorScheme', 'Classic')
            foreground_color = data.get('foregroundColor', COLOR_SCHEMES[color_scheme][0])
            background_color = data.get('backgroundColor', COLOR_SCHEMES[color_scheme][1])
            qr_type = data.get('type', 'Text')
            background_image = None
        else:
            # Handle FormData
            content = request.form.get('content', '').strip()
            size = int(request.form.get('size', 10))
            error_correction = request.form.get('errorCorrection', 'M')
            color_scheme = request.form.get('colorScheme', 'Classic')
            foreground_color = request.form.get('foregroundColor', COLOR_SCHEMES[color_scheme][0])
            background_color = request.form.get('backgroundColor', COLOR_SCHEMES[color_scheme][1])
            qr_type = request.form.get('type', 'Text')
            
            # Check for background image in files or form data
            background_image = request.files.get('backgroundImage')
            if not background_image:
                # Check if background image is sent as base64 in form data
                background_image_data = request.form.get('backgroundImage')
                if background_image_data and background_image_data.startswith('data:image'):
                    # Convert base64 to file-like object
                    try:
                        # Remove data URL prefix
                        if ',' in background_image_data:
                            background_image_data = background_image_data.split(',')[1]
                        
                        # Decode base64
                        image_data = base64.b64decode(background_image_data)
                        background_image = io.BytesIO(image_data)
                        background_image.name = 'background.png'  # Give it a name for PIL
                    except Exception as e:
                        print(f"Error processing background image: {e}")
                        background_image = None
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # Ensure colors are properly formatted
        if not foreground_color.startswith('#'):
            foreground_color = '#000000'
        if not background_color.startswith('#'):
            background_color = '#FFFFFF'
        
        # Generate QR code using qrcode library
        qr = qrcode.QRCode(
            version=None,
            error_correction=getattr(qrcode.constants, f'ERROR_CORRECT_{error_correction}'),
            box_size=size,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color=foreground_color, back_color=background_color)
        
        # If background image is provided, integrate logo into QR code
        if background_image:
            print(f"Processing logo integration: {type(background_image)}")
            try:
                # Open the logo image
                logo_img = Image.open(background_image)
                
                # Convert QR code to RGBA for transparency support
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Get QR code dimensions
                qr_width, qr_height = img.size
                
                # Calculate logo size (typically 20-30% of QR code size)
                logo_size = min(qr_width, qr_height) // 4  # 25% of QR code size
                
                # Resize logo to fit in center
                logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                
                # Convert logo to RGBA if needed
                if logo_img.mode != 'RGBA':
                    logo_img = logo_img.convert('RGBA')
                
                # Create a mask for the logo (white areas become transparent)
                logo_mask = logo_img.split()[3] if len(logo_img.split()) == 4 else None
                
                # Calculate position to center logo in QR code
                logo_x = (qr_width - logo_size) // 2
                logo_y = (qr_height - logo_size) // 2
                
                # Create a copy of the QR code
                result_img = img.copy()
                
                # Create a white background for the logo area (to ensure good contrast)
                # This creates a small white square where the logo will be placed
                white_bg = Image.new('RGBA', (logo_size, logo_size), (255, 255, 255, 255))
                
                # Paste the logo onto the white background
                if logo_mask:
                    white_bg.paste(logo_img, (0, 0), logo_mask)
                else:
                    white_bg.paste(logo_img, (0, 0))
                
                # Paste the logo area onto the QR code
                result_img.paste(white_bg, (logo_x, logo_y), white_bg)
                
                # Convert to bytes
                img_io = io.BytesIO()
                result_img.save(img_io, format='PNG')
                img_io.seek(0)
                img_data = img_io.getvalue()
                
            except Exception as e:
                print(f"Error integrating logo: {e}")
                # If logo integration fails, fall back to regular QR code
                img_io = io.BytesIO()
                img.save(img_io, format='PNG')
                img_io.seek(0)
                img_data = img_io.getvalue()
        else:
            # Convert to bytes
            img_io = io.BytesIO()
            img.save(img_io, format='PNG')
            img_io.seek(0)
            img_data = img_io.getvalue()
        
        # Convert to base64 for preview
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        image_url = f"data:image/png;base64,{img_base64}"
        
        # Add to history if auto-save is enabled
        if settings.get('auto_history', True):
            history_item = {
                'id': len(history) + 1,
                'content': content,
                'type': qr_type,
                'size': size,
                'errorCorrection': error_correction,
                'colorScheme': color_scheme,
                'foregroundColor': foreground_color,
                'backgroundColor': background_color,
                'imageUrl': image_url,
                'createdAt': datetime.now().isoformat()
            }
            history.append(history_item)
        
        return jsonify({
            'imageUrl': image_url,
            'content': content,
            'type': qr_type,
            'size': size,
            'errorCorrection': error_correction,
            'colorScheme': color_scheme,
            'foregroundColor': foreground_color,
            'backgroundColor': background_color
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-qr', methods=['POST'])
def download_qr():
    """Handles QR code download requests."""
    try:
        # Handle both JSON and FormData
        if request.is_json:
            data = request.json
            content = data.get('content', '').strip()
            format_type = data.get('format', 'png')
            size = data.get('size', 10)
            error_correction = data.get('errorCorrection', 'M')
            color_scheme = data.get('colorScheme', 'Classic')
            foreground_color = data.get('foregroundColor', COLOR_SCHEMES[color_scheme][0])
            background_color = data.get('backgroundColor', COLOR_SCHEMES[color_scheme][1])
            background_image = None
        else:
            # Handle FormData
            content = request.form.get('content', '').strip()
            format_type = request.form.get('format', 'png')
            size = int(request.form.get('size', 10))
            error_correction = request.form.get('errorCorrection', 'M')
            color_scheme = request.form.get('colorScheme', 'Classic')
            foreground_color = request.form.get('foregroundColor', COLOR_SCHEMES[color_scheme][0])
            background_color = request.form.get('backgroundColor', COLOR_SCHEMES[color_scheme][1])
            
            # Check for background image in files or form data
            background_image = request.files.get('backgroundImage')
            if not background_image:
                # Check if background image is sent as base64 in form data
                background_image_data = request.form.get('backgroundImage')
                if background_image_data and background_image_data.startswith('data:image'):
                    # Convert base64 to file-like object
                    try:
                        # Remove data URL prefix
                        if ',' in background_image_data:
                            background_image_data = background_image_data.split(',')[1]
                        
                        # Decode base64
                        image_data = base64.b64decode(background_image_data)
                        background_image = io.BytesIO(image_data)
                        background_image.name = 'background.png'  # Give it a name for PIL
                    except Exception as e:
                        print(f"Error processing background image: {e}")
                        background_image = None
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # Ensure colors are properly formatted
        if not foreground_color.startswith('#'):
            foreground_color = '#000000'
        if not background_color.startswith('#'):
            background_color = '#FFFFFF'
        
        # Generate QR code using qrcode library
        qr = qrcode.QRCode(
            version=None,
            error_correction=getattr(qrcode.constants, f'ERROR_CORRECT_{error_correction}'),
            box_size=size,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)
        
        if format_type == 'svg':
            # For SVG, we'll use pyqrcode
            pyqr = pyqrcode.create(content, error=error_correction)
            svg_data = pyqr.svg(scale=size)
            return svg_data, 200, {'Content-Type': 'image/svg+xml'}
        else:
            # Generate PNG
            img = qr.make_image(fill_color=foreground_color, back_color=background_color)
            
            # If background image is provided, integrate logo into QR code
            if background_image:
                try:
                    # Open the logo image
                    logo_img = Image.open(background_image)
                    
                    # Convert QR code to RGBA for transparency support
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    # Get QR code dimensions
                    qr_width, qr_height = img.size
                    
                    # Calculate logo size (typically 20-30% of QR code size)
                    logo_size = min(qr_width, qr_height) // 4  # 25% of QR code size
                    
                    # Resize logo to fit in center
                    logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                    
                    # Convert logo to RGBA if needed
                    if logo_img.mode != 'RGBA':
                        logo_img = logo_img.convert('RGBA')
                    
                    # Create a mask for the logo (white areas become transparent)
                    logo_mask = logo_img.split()[3] if len(logo_img.split()) == 4 else None
                    
                    # Calculate position to center logo in QR code
                    logo_x = (qr_width - logo_size) // 2
                    logo_y = (qr_height - logo_size) // 2
                    
                    # Create a copy of the QR code
                    result_img = img.copy()
                    
                    # Create a white background for the logo area (to ensure good contrast)
                    # This creates a small white square where the logo will be placed
                    white_bg = Image.new('RGBA', (logo_size, logo_size), (255, 255, 255, 255))
                    
                    # Paste the logo onto the white background
                    if logo_mask:
                        white_bg.paste(logo_img, (0, 0), logo_mask)
                    else:
                        white_bg.paste(logo_img, (0, 0))
                    
                    # Paste the logo area onto the QR code
                    result_img.paste(white_bg, (logo_x, logo_y), white_bg)
                    
                    # Create file-like object
                    img_io = io.BytesIO()
                    result_img.save(img_io, format='PNG')
                    img_io.seek(0)
                    
                except Exception as e:
                    print(f"Error integrating logo: {e}")
                    # If logo integration fails, fall back to regular QR code
                    img_io = io.BytesIO()
                    img.save(img_io, format='PNG')
                    img_io.seek(0)
            else:
                # Create file-like object
                img_io = io.BytesIO()
                img.save(img_io, format='PNG')
                img_io.seek(0)
            
            return send_file(
                img_io,
                mimetype='image/png',
                as_attachment=True,
                download_name=f'qr-code-{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Returns the history of generated QR codes."""
    try:
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/settings', methods=['GET'])
def get_settings():
    """Returns the current settings."""
    try:
        return jsonify(settings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/settings', methods=['POST'])
def save_settings():
    """Saves the settings."""
    try:
        global settings
        settings.update(request.json)
        return jsonify({'message': 'Settings saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/qr-types', methods=['GET'])
def get_qr_types():
    """Returns available QR code types."""
    try:
        return jsonify(QR_TYPES)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/color-schemes', methods=['GET'])
def get_color_schemes():
    """Returns available color schemes."""
    try:
        return jsonify(COLOR_SCHEMES)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'message': 'QR Code Generator API is running'})

if __name__ == '__main__':
    print("Starting QR Code Generator...")
    print("Server will be available at: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000) 