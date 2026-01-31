# Book QR Generator

A lightweight desktop application that allows users to upload a PDF book and generate QR codes containing the text content from specific pages or chapters.

## Features

- 📄 **PDF Upload**: Browse and select PDF files from your local system
- 📖 **Page/Chapter Selection**: Specify single pages or page ranges (e.g., "5" or "10-15")
- 📝 **Text Extraction**: Extract text content from specified pages of the PDF
- 📱 **QR Code Generation**: Generate QR codes containing the extracted text
- 💾 **Save & Preview**: Display generated QR codes in the app and save them as PNG images
- ✅ **Cross-Platform**: Works on Windows, macOS, and Linux
- 🛡️ **Error Handling**: Comprehensive validation and user-friendly error messages

## Installation

### Prerequisites

- Python 3.x (Python 3.7 or higher recommended)
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository** (or download the source code):
   ```bash
   git clone https://github.com/marcusg999/book-qr-generator.git
   cd book-qr-generator
   ```

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - `pypdf` (version 3.0.0+) - For PDF text extraction
   - `qrcode[pil]` (version 7.4.2+) - For QR code generation
   - `Pillow` (version 10.0.0+) - For image handling

## Usage

### Running the Application

Run the application using Python:

```bash
python app.py
```

### How to Use

1. **Select a PDF File**:
   - Click the "Browse PDF" button
   - Navigate to and select your PDF file
   - The application will display the total number of pages

2. **Specify Page(s)**:
   - For a single page: Enter the page number (e.g., `5`)
   - For a page range: Enter the range with a hyphen (e.g., `10-15`)
   - The default is page 1

3. **Generate QR Code**:
   - Click the "Generate QR Code" button
   - The application will extract text from the specified page(s)
   - A QR code will be generated and displayed in the preview area
   - Character count will be shown for reference

4. **Save QR Code**:
   - Click the "Save QR Code" button
   - Choose a location and filename
   - The QR code will be saved as a PNG image

5. **Clear Form**:
   - Click the "Clear" button to reset the application and start over

## Technical Details

### QR Code Size Limitations

QR codes have data capacity limitations based on several factors:

- **Maximum capacity**: Approximately 4,296 alphanumeric characters (theoretical maximum)
- **Recommended limit**: ~2,000 characters for reliable scanning
- **Warning threshold**: The application warns when text exceeds 2,000 characters
- **Large text**: QR codes with large amounts of text become very dense and may be difficult to scan

**Tips for best results**:
- Use smaller page ranges for chapters with dense text
- Test QR codes with a mobile scanner app after generation
- If a QR code is too dense, try splitting it into smaller ranges

### Error Handling

The application handles various error scenarios:

- **Invalid PDF**: Validates that the selected file is a valid PDF
- **Page out of range**: Checks that specified pages exist in the PDF
- **Invalid page format**: Validates page number and range formats
- **Empty pages**: Alerts if no text can be extracted from selected pages
- **Text too large**: Warns when text may be too large for reliable QR scanning
- **Save errors**: Handles file permission and path issues gracefully

### Text Processing

- Text from multiple pages in a range is concatenated with spacing
- Excessive whitespace is cleaned up for better QR code efficiency
- Original text formatting from PDF is preserved where possible

## Dependencies

The application requires the following Python packages:

```
pypdf>=3.0.0          # PDF text extraction
qrcode[pil]>=7.4.2    # QR code generation with image support
Pillow>=10.0.0        # Image handling and processing
```

All dependencies are cross-platform and work on Windows, macOS, and Linux.

## GUI Framework

The application uses **Tkinter**, which is included with most Python installations and requires no additional setup. This makes the application truly lightweight with minimal external dependencies.

## Troubleshooting

### Common Issues

**Issue**: "No module named 'tkinter'" error
- **Solution**: Install Tkinter for your Python version:
  - Ubuntu/Debian: `sudo apt-get install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`
  - macOS: Tkinter is included with Python from python.org
  - Windows: Tkinter is included with standard Python installation

**Issue**: QR code won't scan on mobile device
- **Solution**: The text might be too large. Try:
  - Using a smaller page range
  - Splitting content into multiple QR codes
  - Ensure good lighting when scanning

**Issue**: "Failed to load PDF" error
- **Solution**: 
  - Verify the file is a valid PDF
  - Check if the PDF is password-protected (not supported)
  - Try opening the PDF in a PDF reader to confirm it's not corrupted

**Issue**: No text extracted from page
- **Solution**: 
  - The page might contain only images or scanned content
  - PDFs with text as images require OCR (not included in this app)
  - Try different pages that contain selectable text

## Testing

To verify the application works correctly:

1. ✅ Test with a single page selection
2. ✅ Test with a page range selection
3. ✅ Test with invalid page numbers (should show error)
4. ✅ Test with page ranges exceeding total pages (should show error)
5. ✅ Test with empty/image-only pages (should show warning)
6. ✅ Test with large text content (should show warning)
7. ✅ Scan generated QR codes with a mobile device to verify content
8. ✅ Test save functionality in different directories

## License

This project is provided as-is for educational and personal use.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Author

Created as a lightweight, cross-platform solution for generating QR codes from PDF content.