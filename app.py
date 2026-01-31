#!/usr/bin/env python3
"""
Book QR Generator - A lightweight desktop application for generating QR codes from PDF content.
"""

import sys
import os
import re
from io import BytesIO

# Check for required dependencies with helpful error messages
missing_dependencies = []

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    from tkinter import PhotoImage
except ImportError:
    print("\n❌ ERROR: tkinter is not installed.")
    print("\ntkinter is required for the graphical user interface.")
    print("\nTo install tkinter:")
    print("  • Ubuntu/Debian: sudo apt-get install python3-tk")
    print("  • Fedora: sudo dnf install python3-tkinter")
    print("  • macOS: tkinter is included with Python from python.org")
    print("  • Windows: tkinter is included with standard Python installation")
    sys.exit(1)

try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        missing_dependencies.append("pypdf (or PyPDF2)")

try:
    import qrcode
except ImportError:
    missing_dependencies.append("qrcode[pil]")

try:
    from PIL import Image, ImageTk
except ImportError:
    # Only add Pillow if qrcode is already satisfied (since qrcode[pil] includes Pillow)
    if "qrcode[pil]" not in missing_dependencies:
        missing_dependencies.append("Pillow")

# If any dependencies are missing, provide helpful error message
if missing_dependencies:
    print("\n❌ ERROR: Required Python packages are not installed.\n")
    print("Missing packages:")
    for dep in missing_dependencies:
        print(f"  • {dep}")
    print("\n📦 To install all required dependencies, run:")
    print("     pip install -r requirements.txt")
    print("\nOr install individually:")
    print("     pip install pypdf qrcode[pil]")
    print("\n💡 Note: qrcode[pil] includes Pillow for image support.")
    print("💡 Make sure you're in the book-qr-generator directory.\n")
    sys.exit(1)


class BookQRGenerator:
    """Main application class for the Book QR Generator."""
    
    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("Book QR Generator")
        self.root.geometry("700x800")
        self.root.resizable(True, True)
        
        # Application state for PDF mode
        self.pdf_path = None
        self.pdf_reader = None
        self.total_pages = 0
        self.qr_image = None
        self.qr_photo = None
        self.extracted_text = ""
        self.google_drive_link = ""
        
        # Application state for URL mode
        self.url_qr_image = None
        self.url_qr_photo = None
        self.url_input = None
        self.url_qr_label = None
        self.url_char_count_label = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface with tabbed interface."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.pdf_tab = ttk.Frame(self.notebook, padding="10")
        self.url_tab = ttk.Frame(self.notebook, padding="10")
        
        self.notebook.add(self.pdf_tab, text="PDF to QR Code")
        self.notebook.add(self.url_tab, text="URL to QR Code")
        
        # Set up individual tabs
        self.setup_pdf_tab()
        self.setup_url_tab()
    
    def setup_pdf_tab(self):
        """Set up the PDF to QR Code tab."""
        # Configure grid weights for resizing
        self.pdf_tab.columnconfigure(0, weight=1)
        
        # Help text at top
        help_label = ttk.Label(
            self.pdf_tab,
            text="Extract text from PDF pages and generate QR codes",
            foreground="gray",
            font=("TkDefaultFont", 9, "italic")
        )
        help_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # PDF Selection Section
        pdf_frame = ttk.LabelFrame(self.pdf_tab, text="1. Select PDF File", padding="10")
        pdf_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        pdf_frame.columnconfigure(1, weight=1)
        
        ttk.Button(pdf_frame, text="Browse PDF", command=self.browse_pdf).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        
        self.pdf_path_label = ttk.Label(pdf_frame, text="No file selected", foreground="gray")
        self.pdf_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        self.pdf_info_label = ttk.Label(pdf_frame, text="", foreground="blue")
        self.pdf_info_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Page Selection Section
        page_frame = ttk.LabelFrame(self.pdf_tab, text="2. Select Page(s)", padding="10")
        page_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        page_frame.columnconfigure(1, weight=1)
        
        ttk.Label(page_frame, text="Page Number or Range:").grid(row=0, column=0, sticky=tk.W)
        
        self.page_entry = ttk.Entry(page_frame, width=20)
        self.page_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        self.page_entry.insert(0, "1")
        
        help_text = ttk.Label(
            page_frame,
            text="Enter a single page (e.g., '5') or a range (e.g., '10-15')",
            foreground="gray",
            font=("TkDefaultFont", 8)
        )
        help_text.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Google Drive Link Section
        ttk.Label(page_frame, text="Google Drive Link (Optional):").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        
        # Frame for Google Drive link input and clear button
        link_frame = ttk.Frame(page_frame)
        link_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 0))
        link_frame.columnconfigure(0, weight=1)
        
        self.drive_link_entry = ttk.Entry(link_frame)
        self.drive_link_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(link_frame, text="Clear Link", command=self.clear_drive_link, width=10).grid(
            row=0, column=1, sticky=tk.W
        )
        
        link_help_text = ttk.Label(
            page_frame,
            text="This link will be included in the QR code (e.g., https://drive.google.com/file/d/.../view)",
            foreground="gray",
            font=("TkDefaultFont", 8)
        )
        link_help_text.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Generate Button
        button_frame = ttk.Frame(self.pdf_tab)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        ttk.Button(button_frame, text="Generate QR Code", command=self.generate_qr).grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5)
        )
        
        ttk.Button(button_frame, text="Save QR Code", command=self.save_qr).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5)
        )
        
        ttk.Button(button_frame, text="Clear", command=self.clear_form).grid(
            row=0, column=2, sticky=(tk.W, tk.E), padx=(5, 0)
        )
        
        # Text Info Section
        info_frame = ttk.LabelFrame(self.pdf_tab, text="Text Information", padding="10")
        info_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.text_info_label = ttk.Label(info_frame, text="No text extracted yet")
        self.text_info_label.grid(row=0, column=0, sticky=tk.W)
        
        # QR Code Preview Section
        qr_frame = ttk.LabelFrame(self.pdf_tab, text="QR Code Preview", padding="10")
        qr_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        qr_frame.columnconfigure(0, weight=1)
        qr_frame.rowconfigure(0, weight=1)
        self.pdf_tab.rowconfigure(5, weight=1)
        
        # Canvas for QR code display
        self.qr_canvas = tk.Canvas(qr_frame, width=400, height=400, bg="white", relief=tk.SUNKEN, borderwidth=2)
        self.qr_canvas.grid(row=0, column=0)
        
        # Initial message on canvas
        self.qr_canvas.create_text(
            200, 200,
            text="QR code will appear here",
            fill="gray",
            font=("TkDefaultFont", 12),
            tags="placeholder"
        )
    
    def setup_url_tab(self):
        """Set up the URL to QR Code tab."""
        # Configure grid weights for resizing
        self.url_tab.columnconfigure(0, weight=1)
        self.url_tab.rowconfigure(4, weight=1)
        
        # Help text at top
        help_label = ttk.Label(
            self.url_tab,
            text="Quickly convert any URL or text into a scannable QR code",
            foreground="gray",
            font=("TkDefaultFont", 9, "italic")
        )
        help_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # URL Input Section
        url_frame = ttk.LabelFrame(self.url_tab, text="Enter URL or Text", padding="10")
        url_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(0, weight=1)
        
        ttk.Label(url_frame, text="URL or Text:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Text entry for URL/text input
        self.url_input = tk.Text(url_frame, height=3, wrap=tk.WORD)
        self.url_input.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.url_input.insert("1.0", "https://example.com or any text")
        self.url_input.config(foreground="gray")
        
        # Bind events for placeholder behavior
        self.url_input.bind("<FocusIn>", self.on_url_focus_in)
        self.url_input.bind("<FocusOut>", self.on_url_focus_out)
        self.url_input.bind("<KeyRelease>", self.update_char_count)
        
        # Character count label
        self.url_char_count_label = ttk.Label(url_frame, text="Character Count: 0", foreground="blue")
        self.url_char_count_label.grid(row=2, column=0, sticky=tk.W)
        
        # Button frame
        button_frame = ttk.Frame(self.url_tab)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        ttk.Button(button_frame, text="Generate QR Code", command=self.generate_qr_from_url).grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5)
        )
        
        ttk.Button(button_frame, text="Clear", command=self.clear_url_input).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0)
        )
        
        # QR Code Preview Section
        qr_frame = ttk.LabelFrame(self.url_tab, text="QR Code Preview", padding="10")
        qr_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        qr_frame.columnconfigure(0, weight=1)
        qr_frame.rowconfigure(0, weight=1)
        
        # Canvas for QR code display
        self.url_qr_canvas = tk.Canvas(qr_frame, width=400, height=400, bg="white", relief=tk.SUNKEN, borderwidth=2)
        self.url_qr_canvas.grid(row=0, column=0)
        
        # Initial message on canvas
        self.url_qr_canvas.create_text(
            200, 200,
            text="QR code will appear here",
            fill="gray",
            font=("TkDefaultFont", 12),
            tags="placeholder"
        )
        
        # Save button
        ttk.Button(self.url_tab, text="Save QR Code", command=self.save_url_qr_code).grid(
            row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10)
        )
    
    def on_url_focus_in(self, event):
        """Handle focus in event for URL input (remove placeholder)."""
        if self.url_input.get("1.0", "end-1c") == "https://example.com or any text":
            self.url_input.delete("1.0", tk.END)
            self.url_input.config(foreground="black")
    
    def on_url_focus_out(self, event):
        """Handle focus out event for URL input (restore placeholder if empty)."""
        if not self.url_input.get("1.0", "end-1c").strip():
            self.url_input.insert("1.0", "https://example.com or any text")
            self.url_input.config(foreground="gray")
    
    def update_char_count(self, event=None):
        """Update character count label."""
        content = self.url_input.get("1.0", "end-1c")
        if content == "https://example.com or any text":
            count = 0
        else:
            count = len(content)
        self.url_char_count_label.config(text=f"Character Count: {count}")
    
    def validate_url(self, url):
        """
        Basic URL validation and formatting.
        
        Args:
            url: The URL string to validate
        
        Returns:
            Formatted URL string
        """
        url = url.strip()
        
        # If it looks like a URL but doesn't have protocol, add https://
        if url and not url.startswith(('http://', 'https://', 'ftp://')):
            # Check if it looks like a domain (contains a dot and no spaces)
            if '.' in url and ' ' not in url:
                url = 'https://' + url
        
        return url
    
    def generate_qr_from_url(self):
        """Generate QR code from URL/text input."""
        # Get content from input
        content = self.url_input.get("1.0", "end-1c")
        
        # Check if placeholder is still there
        if content == "https://example.com or any text" or not content.strip():
            messagebox.showwarning("Warning", "Please enter a URL or text to generate QR code")
            return
        
        # Validate and format URL if it looks like one
        content = self.validate_url(content)
        
        # Check length
        content_length = len(content)
        if content_length > 2000:
            response = messagebox.askyesno(
                "Large Text Warning",
                f"The content is very large ({content_length} characters).\n"
                "QR codes work best with smaller amounts of text.\n"
                "The QR code may be difficult to scan.\n\n"
                "Do you want to continue anyway?"
            )
            if not response:
                return
        
        try:
            # Generate QR code with high error correction for URLs
            qr = qrcode.QRCode(
                version=None,  # Auto-size
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
                box_size=10,
                border=4,
            )
            qr.add_data(content)
            qr.make(fit=True)
            
            # Create image
            self.url_qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Display in canvas
            self.display_url_qr_code()
            
            messagebox.showinfo("Success", f"QR code generated successfully!\nContent length: {content_length} characters")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code:\n{str(e)}")
    
    def display_url_qr_code(self):
        """Display the URL QR code on the canvas."""
        if not self.url_qr_image:
            return
        
        # Remove placeholder text
        self.url_qr_canvas.delete("placeholder")
        
        # Resize image to fit canvas (max 380x380 to leave some padding)
        img_width, img_height = self.url_qr_image.size
        max_size = 380
        
        if img_width > max_size or img_height > max_size:
            ratio = min(max_size / img_width, max_size / img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            display_image = self.url_qr_image.resize((new_width, new_height), Image.LANCZOS)
        else:
            display_image = self.url_qr_image
        
        # Convert to PhotoImage
        self.url_qr_photo = ImageTk.PhotoImage(display_image)
        
        # Clear canvas and display image
        self.url_qr_canvas.delete("all")
        canvas_width = self.url_qr_canvas.winfo_width()
        canvas_height = self.url_qr_canvas.winfo_height()
        
        # If canvas dimensions are not yet set, use defaults
        if canvas_width <= 1:
            canvas_width = 400
        if canvas_height <= 1:
            canvas_height = 400
        
        # Center the image
        x = canvas_width // 2
        y = canvas_height // 2
        self.url_qr_canvas.create_image(x, y, image=self.url_qr_photo, anchor=tk.CENTER)
    
    def clear_url_input(self):
        """Clear URL input and reset preview."""
        self.url_input.delete("1.0", tk.END)
        self.url_input.insert("1.0", "https://example.com or any text")
        self.url_input.config(foreground="gray")
        
        # Clear QR code
        self.url_qr_image = None
        self.url_qr_photo = None
        
        # Reset canvas
        self.url_qr_canvas.delete("all")
        self.url_qr_canvas.create_text(
            200, 200,
            text="QR code will appear here",
            fill="gray",
            font=("TkDefaultFont", 12),
            tags="placeholder"
        )
        
        # Reset character count
        self.url_char_count_label.config(text="Character Count: 0")
    
    def save_url_qr_code(self):
        """Save the generated QR code from URL."""
        if not self.url_qr_image:
            messagebox.showwarning("Warning", "Please generate a QR code first")
            return
        
        # Open save dialog
        file_path = filedialog.asksaveasfilename(
            title="Save QR Code",
            defaultextension=".png",
            initialfile="qrcode_url.png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.url_qr_image.save(file_path)
                messagebox.showinfo("Success", f"QR code saved successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save QR code:\n{str(e)}")
    
    def browse_pdf(self):
        """Open file dialog to select a PDF file."""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Try to open and read the PDF
                self.pdf_reader = PdfReader(file_path)
                self.total_pages = len(self.pdf_reader.pages)
                self.pdf_path = file_path
                
                # Update UI
                filename = os.path.basename(file_path)
                self.pdf_path_label.config(text=filename, foreground="black")
                self.pdf_info_label.config(text=f"Total pages: {self.total_pages}")
                
                messagebox.showinfo("Success", f"PDF loaded successfully!\nTotal pages: {self.total_pages}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load PDF:\n{str(e)}")
                self.pdf_path = None
                self.pdf_reader = None
                self.total_pages = 0
    
    def validate_google_drive_link(self, url):
        """
        Validate if the URL appears to be a Google Drive or Google Docs link.
        
        Args:
            url: The URL string to validate
        
        Returns:
            Tuple of (is_valid, warning_message)
            - is_valid: True if URL is valid and appears to be a Google link
            - warning_message: String with warning if not a Google link, None otherwise
        """
        if not url or not url.strip():
            return True, None  # Empty is valid (optional field)
        
        url = url.strip()
        
        # Basic URL pattern check
        if not url.startswith(('http://', 'https://')):
            return False, "URL should start with http:// or https://"
        
        # Check if it's a Google Drive/Docs link
        google_domains = [
            'drive.google.com',
            'docs.google.com',
            'sheets.google.com',
            'slides.google.com'
        ]
        
        is_google_link = any(domain in url.lower() for domain in google_domains)
        
        if not is_google_link:
            return True, "⚠️ This doesn't appear to be a Google Drive/Docs link. Continue anyway?"
        
        return True, None
    
    def clear_drive_link(self):
        """Clear the Google Drive link entry field."""
        self.drive_link_entry.delete(0, tk.END)
    
    def parse_page_input(self, page_input):
        """
        Parse the page input string.
        
        Args:
            page_input: String containing page number or range (e.g., "5" or "10-15")
        
        Returns:
            List of page numbers (1-indexed)
        
        Raises:
            ValueError: If input is invalid
        """
        page_input = page_input.strip()
        
        # Check if it's a range
        if '-' in page_input:
            match = re.match(r'^(\d+)\s*-\s*(\d+)$', page_input)
            if not match:
                raise ValueError("Invalid page range format. Use format like '10-15'")
            
            start_page = int(match.group(1))
            end_page = int(match.group(2))
            
            if start_page < 1:
                raise ValueError("Page numbers must be greater than 0")
            if start_page > end_page:
                raise ValueError("Start page must be less than or equal to end page")
            if end_page > self.total_pages:
                raise ValueError(f"End page {end_page} exceeds total pages ({self.total_pages})")
            
            return list(range(start_page, end_page + 1))
        else:
            # Single page
            if not page_input.isdigit():
                raise ValueError("Invalid page number. Enter a number or range like '10-15'")
            
            page_num = int(page_input)
            if page_num < 1:
                raise ValueError("Page number must be greater than 0")
            if page_num > self.total_pages:
                raise ValueError(f"Page {page_num} exceeds total pages ({self.total_pages})")
            
            return [page_num]
    
    def extract_text(self, page_numbers):
        """
        Extract text from specified pages.
        
        Args:
            page_numbers: List of page numbers (1-indexed)
        
        Returns:
            Extracted and cleaned text
        """
        extracted_texts = []
        
        for page_num in page_numbers:
            # Convert to 0-indexed for pypdf
            page = self.pdf_reader.pages[page_num - 1]
            text = page.extract_text()
            
            if text:
                extracted_texts.append(text)
        
        # Concatenate all texts
        combined_text = "\n\n".join(extracted_texts)
        
        # Clean up text - remove excessive whitespace
        combined_text = re.sub(r'\s+', ' ', combined_text)
        combined_text = combined_text.strip()
        
        return combined_text
    
    def generate_qr(self):
        """Generate QR code from extracted text."""
        # Validate PDF is loaded
        if not self.pdf_reader:
            messagebox.showwarning("Warning", "Please select a PDF file first")
            return
        
        # Get and validate page input
        page_input = self.page_entry.get().strip()
        if not page_input:
            messagebox.showwarning("Warning", "Please enter a page number or range")
            return
        
        try:
            page_numbers = self.parse_page_input(page_input)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        
        # Get and validate Google Drive link
        drive_link = self.drive_link_entry.get().strip()
        if drive_link:
            is_valid, warning_message = self.validate_google_drive_link(drive_link)
            if not is_valid:
                messagebox.showerror("Error", warning_message)
                return
            if warning_message:
                response = messagebox.askyesno("Warning", warning_message)
                if not response:
                    return
        
        # Extract text
        try:
            self.extracted_text = self.extract_text(page_numbers)
            
            if not self.extracted_text:
                messagebox.showwarning(
                    "Warning",
                    "No text could be extracted from the specified page(s).\n"
                    "The page(s) might be empty or contain only images."
                )
                return
            
            # Prepare QR code content
            qr_content = self.extracted_text
            
            # Add Google Drive link if provided
            if drive_link:
                qr_content = f"{self.extracted_text}\n\n---\nGoogle Drive Link: {drive_link}"
                self.google_drive_link = drive_link
            else:
                self.google_drive_link = ""
            
            # Check text length (QR codes have limitations)
            text_length = len(qr_content)
            
            # QR code can typically hold up to ~4296 characters (with low error correction)
            # We'll use a more conservative limit
            if text_length > 2000:
                response = messagebox.askyesno(
                    "Large Text Warning",
                    f"The combined content is very large ({text_length} characters).\n"
                    "QR codes work best with smaller amounts of text.\n"
                    "The QR code may be difficult to scan.\n\n"
                    "Do you want to continue anyway?"
                )
                if not response:
                    return
            
            # Update text info
            page_range_str = f"Page {page_numbers[0]}" if len(page_numbers) == 1 else f"Pages {page_numbers[0]}-{page_numbers[-1]}"
            
            # Calculate breakdown for display
            if drive_link:
                text_only_length = len(self.extracted_text)
                # Calculate the link portion including formatting
                link_portion = f"\n\n---\nGoogle Drive Link: {drive_link}"
                link_length = len(link_portion)
                self.text_info_label.config(
                    text=f"Text: {text_only_length} chars | Link: {link_length} chars | Total: {text_length} characters"
                )
            else:
                self.text_info_label.config(
                    text=f"Text extracted from {page_range_str}: {text_length} characters"
                )
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=None,  # Auto-size
                error_correction=qrcode.constants.ERROR_CORRECT_L,  # Low error correction for more data
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            
            # Create image
            self.qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Display in canvas
            self.display_qr_code()
            
            success_msg = f"QR code generated successfully!\n"
            success_msg += f"Text length: {len(self.extracted_text)} characters\n"
            if drive_link:
                success_msg += f"Link included: {len(drive_link)} characters\n"
                success_msg += f"Total: {text_length} characters\n"
            success_msg += f"Pages: {page_range_str}"
            
            messagebox.showinfo("Success", success_msg)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code:\n{str(e)}")
    
    def display_qr_code(self):
        """Display the QR code on the canvas."""
        if not self.qr_image:
            return
        
        # Remove placeholder text
        self.qr_canvas.delete("placeholder")
        
        # Resize image to fit canvas (max 380x380 to leave some padding)
        img_width, img_height = self.qr_image.size
        max_size = 380
        
        if img_width > max_size or img_height > max_size:
            ratio = min(max_size / img_width, max_size / img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            display_image = self.qr_image.resize((new_width, new_height), Image.LANCZOS)
        else:
            display_image = self.qr_image
        
        # Convert to PhotoImage
        self.qr_photo = ImageTk.PhotoImage(display_image)
        
        # Clear canvas and display image
        self.qr_canvas.delete("all")
        canvas_width = self.qr_canvas.winfo_width()
        canvas_height = self.qr_canvas.winfo_height()
        
        # If canvas dimensions are not yet set, use defaults
        if canvas_width <= 1:
            canvas_width = 400
        if canvas_height <= 1:
            canvas_height = 400
        
        # Center the image
        x = canvas_width // 2
        y = canvas_height // 2
        self.qr_canvas.create_image(x, y, image=self.qr_photo, anchor=tk.CENTER)
    
    def save_qr(self):
        """Save the QR code to a file."""
        if not self.qr_image:
            messagebox.showwarning("Warning", "Please generate a QR code first")
            return
        
        # Open save dialog
        file_path = filedialog.asksaveasfilename(
            title="Save QR Code",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.qr_image.save(file_path)
                messagebox.showinfo("Success", f"QR code saved successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save QR code:\n{str(e)}")
    
    def clear_form(self):
        """Clear the form and reset to initial state."""
        self.pdf_path = None
        self.pdf_reader = None
        self.total_pages = 0
        self.qr_image = None
        self.qr_photo = None
        self.extracted_text = ""
        self.google_drive_link = ""
        
        self.pdf_path_label.config(text="No file selected", foreground="gray")
        self.pdf_info_label.config(text="")
        self.page_entry.delete(0, tk.END)
        self.page_entry.insert(0, "1")
        self.drive_link_entry.delete(0, tk.END)
        self.text_info_label.config(text="No text extracted yet")
        
        # Clear canvas
        self.qr_canvas.delete("all")
        self.qr_canvas.create_text(
            200, 200,
            text="QR code will appear here",
            fill="gray",
            font=("TkDefaultFont", 12),
            tags="placeholder"
        )


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = BookQRGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
