# 🚀 Advanced QR Code Generator

A beautiful, modern web application for generating customizable QR codes. Built with Flask and inspired by the desktop QR code generator.

## ✨ Features

- **Multiple QR Code Types**: URL, Text, Email, Phone, SMS, WiFi, Contact, Location, Event
- **Customizable Appearance**: Size, error correction, color schemes
- **Real-time Preview**: See your QR code as you type
- **Download Options**: Save as PNG or SVG
- **Copy to Clipboard**: Copy QR code content easily
- **Responsive Design**: Works on desktop and mobile
- **Modern UI**: Beautiful gradient design with smooth animations

## 🛠️ Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd projects/qr-code-generator
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser and go to:**
   ```
   http://127.0.0.1:5000
   ```

## 🎯 Usage

### Generating QR Codes

1. **Select QR Code Type**: Choose from URL, Text, Email, Phone, SMS, WiFi, Contact, Location, or Event
2. **Enter Content**: Type or paste your content in the text area
3. **Customize Settings**:
   - **Size**: Adjust from 1x to 20x scale
   - **Error Correction**: Choose from L (7%), M (15%), Q (25%), or H (30%)
   - **Color Scheme**: Select from Classic, Blue, Green, Purple, Red, or Custom
4. **Generate**: Click "🔄 Generate QR Code" to create your QR code
5. **Download**: Click "💾 Download" to save the QR code as PNG
6. **Copy**: Click "📋 Copy" to copy the content to clipboard

### QR Code Types

- **URL**: Website links (e.g., https://www.example.com)
- **Text**: Plain text messages
- **Email**: Email addresses (e.g., example@email.com)
- **Phone**: Phone numbers (e.g., +1234567890)
- **SMS**: SMS messages with phone number and text
- **WiFi**: WiFi network credentials
- **Contact**: Contact information in vCard format
- **Location**: Geographic coordinates
- **Event**: Calendar events in iCalendar format

## 🎨 Customization

### Color Schemes
- **Classic**: Black and white
- **Blue**: Blue QR code on white background
- **Green**: Green QR code on white background
- **Purple**: Purple QR code on white background
- **Red**: Red QR code on white background
- **Custom**: Choose your own colors

### Error Correction Levels
- **L (Low)**: 7% - Good for clean printing
- **M (Medium)**: 15% - Default, good balance
- **Q (Quartile)**: 25% - Better for small sizes
- **H (High)**: 30% - Maximum error correction

## 🏗️ Project Structure

```
qr-code-generator/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── templates/
    └── index.html        # Main HTML template
```

## 🔧 API Endpoints

- `GET /` - Main page
- `POST /generate-qr` - Generate QR code
- `POST /download-qr` - Download QR code
- `GET /history` - Get generation history
- `GET /settings` - Get current settings
- `POST /settings` - Save settings
- `GET /qr-types` - Get available QR types
- `GET /color-schemes` - Get available color schemes
- `GET /health` - Health check

## 🚀 Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **QR Generation**: pyqrcode, qrcode
- **Image Processing**: Pillow (PIL)
- **Styling**: Custom CSS with gradients and animations
- **Fonts**: Google Fonts (Inter)

## 🎯 Features from Desktop Version

This web version includes all the key features from the desktop QR code generator:

- ✅ Multiple QR code types
- ✅ Customizable size and error correction
- ✅ Color schemes and customization
- ✅ Real-time preview
- ✅ Download functionality
- ✅ Copy to clipboard
- ✅ Modern, responsive UI

## 🌟 Future Enhancements

- [ ] History management with database
- [ ] User accounts and saved QR codes
- [ ] Bulk QR code generation
- [ ] QR code scanning functionality
- [ ] Advanced customization options
- [ ] API rate limiting and security
- [ ] Export to different formats (PDF, SVG)

## 🤝 Contributing

Feel free to contribute to this project by:
- Reporting bugs
- Suggesting new features
- Improving the UI/UX
- Adding new QR code types

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Inspired by the desktop QR code generator
- Built with Flask web framework
- Uses pyqrcode and qrcode libraries
- Modern UI design with CSS gradients

---


**Happy QR Code Generating! 🚀** 
