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
        
        # Application state
        self.pdf_path = None
        self.pdf_reader = None
        self.total_pages = 0
        self.qr_image = None
        self.qr_photo = None
        self.extracted_text = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # PDF Selection Section
        pdf_frame = ttk.LabelFrame(main_frame, text="1. Select PDF File", padding="10")
        pdf_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        pdf_frame.columnconfigure(1, weight=1)
        
        ttk.Button(pdf_frame, text="Browse PDF", command=self.browse_pdf).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        
        self.pdf_path_label = ttk.Label(pdf_frame, text="No file selected", foreground="gray")
        self.pdf_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        self.pdf_info_label = ttk.Label(pdf_frame, text="", foreground="blue")
        self.pdf_info_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Page Selection Section
        page_frame = ttk.LabelFrame(main_frame, text="2. Select Page(s)", padding="10")
        page_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
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
        
        # Generate Button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
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
        info_frame = ttk.LabelFrame(main_frame, text="Text Information", padding="10")
        info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.text_info_label = ttk.Label(info_frame, text="No text extracted yet")
        self.text_info_label.grid(row=0, column=0, sticky=tk.W)
        
        # QR Code Preview Section
        qr_frame = ttk.LabelFrame(main_frame, text="QR Code Preview", padding="10")
        qr_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        qr_frame.columnconfigure(0, weight=1)
        qr_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
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
            
            # Check text length (QR codes have limitations)
            text_length = len(self.extracted_text)
            
            # QR code can typically hold up to ~4296 characters (with low error correction)
            # We'll use a more conservative limit
            if text_length > 2000:
                response = messagebox.askyesno(
                    "Large Text Warning",
                    f"The extracted text is very large ({text_length} characters).\n"
                    "QR codes work best with smaller amounts of text.\n"
                    "The QR code may be difficult to scan.\n\n"
                    "Do you want to continue anyway?"
                )
                if not response:
                    return
            
            # Update text info
            page_range_str = f"Page {page_numbers[0]}" if len(page_numbers) == 1 else f"Pages {page_numbers[0]}-{page_numbers[-1]}"
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
            qr.add_data(self.extracted_text)
            qr.make(fit=True)
            
            # Create image
            self.qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Display in canvas
            self.display_qr_code()
            
            messagebox.showinfo(
                "Success",
                f"QR code generated successfully!\n"
                f"Text length: {text_length} characters\n"
                f"Pages: {page_range_str}"
            )
            
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
        
        self.pdf_path_label.config(text="No file selected", foreground="gray")
        self.pdf_info_label.config(text="")
        self.page_entry.delete(0, tk.END)
        self.page_entry.insert(0, "1")
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
