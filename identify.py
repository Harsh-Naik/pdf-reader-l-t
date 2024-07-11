import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
import os
import shutil

# Ensure the Tesseract executable is in the PATH or specify the path directly
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path if needed

def extract_text_from_images(images):
    text = ""
    
    for image in images:
        text += pytesseract.image_to_string(image)
    
    return text

def identify_document_type(text):
    # Regular expressions for Aadhaar, PAN card, and Indian Passport patterns
    aadhaar_pattern = r'\d{4}\s\d{4}\s\d{4}'
    pan_pattern = r'[A-Z]{5}\d{4}[A-Z]{1}'
    
    if re.search(aadhaar_pattern, text):
        return "Aadhaar Card"
    elif re.search(pan_pattern, text):
        return "PAN Card"
    else:
        return None

def process_documents(input_folder, output_identified, output_error):
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                images = extract_images_from_pdf(file_path)
                text = extract_text_from_images(images)
                document_type = identify_document_type(text)
                
                if document_type == "Aadhaar Card" or document_type == "PAN Card":
                    shutil.copy(file_path, os.path.join(output_identified, file))
                else:
                    shutil.copy(file_path, os.path.join(output_error, file))
                    
                print(f"{file} processed and moved to respective folder.")
                
            except Exception as e:
                print(f"Error processing {file}: {str(e)}")

def extract_images_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    images = []

    for page_num in range(len(document)):
        page = document.load_page(page_num)
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = document.extract_image(xref)
            image_bytes = base_image["image"]
            images.append(Image.open(io.BytesIO(image_bytes)))
    
    return images

def main():
    input_folder = 'D:\employee data'
    output_identified = 'D:\pr_project\identify'
    output_error = 'D:\pr_project\error'
    
    if not os.path.exists(output_identified):
        os.makedirs(output_identified)
    if not os.path.exists(output_error):
        os.makedirs(output_error)
    
    process_documents(input_folder, output_identified, output_error)

if __name__ == "__main__":
    main()
