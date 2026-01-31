# Book QR Generator

A lightweight desktop application that allows users to upload a PDF book and generate QR codes containing the text content from specific pages or chapters.

## Features

- 📄 **PDF Upload**: Browse and select PDF files from your local system
- 📖 **Page/Chapter Selection**: Specify single pages or page ranges (e.g., "5" or "10-15")
- 📝 **Text Extraction**: Extract text content from specified pages of the PDF
- 🔗 **Google Drive Link Integration**: Optionally include a Google Drive link in the QR code
- 📱 **QR Code Generation**: Generate QR codes containing the extracted text and optional link
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

## Screenshots

### Initial Application Interface
![Initial UI](https://github.com/user-attachments/assets/77a7ca7c-6a97-4191-8a9a-48f409308d60)

### Application with PDF Loaded
![PDF Loaded](https://github.com/user-attachments/assets/e0a1278b-3b9c-4c67-8b03-a17f52a47a39)

### Sample Generated QR Code
![Sample QR Code](https://github.com/user-attachments/assets/deccf4cf-ece0-47c7-ac42-586a09a10bfb)

*This QR code contains text from pages 1-2 of a test PDF and can be scanned with any QR code reader.*

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

3. **Add Google Drive Link (Optional)**:
   - Paste a Google Drive link in the "Google Drive Link (Optional)" field
   - Supported formats include:
     - `https://drive.google.com/file/d/[file_id]/view`
     - `https://drive.google.com/open?id=[file_id]`
     - `https://docs.google.com/document/d/[doc_id]/`
   - Click "Clear Link" to remove the link if needed
   - The app will validate if it's a Google link and warn you if not

4. **Generate QR Code**:
   - Click the "Generate QR Code" button
   - The application will extract text from the specified page(s)
   - If a Google Drive link is provided, it will be appended to the QR code content
   - A QR code will be generated and displayed in the preview area
   - Character count breakdown will be shown (text, link, and total)

5. **Save QR Code**:
   - Click the "Save QR Code" button
   - Choose a location and filename
   - The QR code will be saved as a PNG image

6. **Clear Form**:
   - Click the "Clear" button to reset the application and start over

## Technical Details

### QR Code Size Limitations

QR codes have data capacity limitations based on several factors:

- **Maximum capacity**: Approximately 4,296 alphanumeric characters (theoretical maximum)
- **Recommended limit**: ~2,000 characters for reliable scanning
- **Warning threshold**: The application warns when content (text + link) exceeds 2,000 characters
- **Large text**: QR codes with large amounts of text become very dense and may be difficult to scan

**Tips for best results**:
- Use smaller page ranges for chapters with dense text
- Consider the Google Drive link length when selecting page ranges
- Test QR codes with a mobile scanner app after generation
- If a QR code is too dense, try splitting it into smaller ranges or omitting the link

### Google Drive Link Format

When a Google Drive link is included, the QR code content is formatted as follows:

```
[Extracted Text Content]

---
Google Drive Link: [your link]
```

The link validation accepts various Google Drive and Google Docs formats:
- Google Drive files: `https://drive.google.com/file/d/...`
- Google Drive folders: `https://drive.google.com/drive/folders/...`
- Google Docs: `https://docs.google.com/document/d/...`
- Google Sheets: `https://sheets.google.com/spreadsheets/d/...`
- Google Slides: `https://slides.google.com/presentation/d/...`

The application will warn you if the URL doesn't appear to be a Google link, but will still allow generation if you choose to proceed.

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
7. ✅ Test QR code generation without Google Drive link (text only)
8. ✅ Test QR code generation with valid Google Drive link
9. ✅ Test QR code generation with non-Google URL (should warn but allow)
10. ✅ Test "Clear Link" button functionality
11. ✅ Test character count display with and without link
12. ✅ Scan generated QR codes with a mobile device to verify content
13. ✅ Test save functionality in different directories
14. ✅ Test "Clear" button to reset all fields

## License

This project is provided as-is for educational and personal use.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Author

Created as a lightweight, cross-platform solution for generating QR codes from PDF content.