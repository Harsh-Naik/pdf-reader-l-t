import os
import re
import shutil
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import json

# Ensure the Tesseract executable is in the PATH or specify the path directly
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path if needed

# Define keywords for each type of document
keywords_10th = ['Class 10', 'Secondary School', 'Matriculation', 'High School']
keywords_12th = ['Class 12', 'Higher Secondary', 'Senior Secondary']
keywords_degree = ['Degree', 'Graduation', 'Bachelor']
aadhaar_pattern = r'\d{4}\s\d{4}\s\d{4}'
pan_pattern = r'[A-Z]{5}\d{4}[A-Z]{1}'
keywords_offer_letter = ['Offer Letter', 'Appointment Letter']
keywords_appraisal = ['Appraisal', 'Performance Review']

def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

def extract_text_from_pdf(pdf_document):
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

def identify_document_type(text):
    if re.search(aadhaar_pattern, text):
        return "Aadhaar Card"
    elif re.search(pan_pattern, text):
        return "PAN Card"
    elif any(keyword.lower() in text.lower() for keyword in keywords_offer_letter):
        return "Offer Letter"
    elif any(keyword.lower() in text.lower() for keyword in keywords_appraisal):
        return "Appraisal"
    else:
        return "Unknown Document"

def identify_marksheet(text):
    for keyword in keywords_10th:
        if re.search(keyword, text, re.IGNORECASE):
            return "10th Marksheet"
    for keyword in keywords_12th:
        if re.search(keyword, text, re.IGNORECASE):
            return "12th Marksheet"
    for keyword in keywords_degree:
        if re.search(keyword, text, re.IGNORECASE):
            return "Degree Marksheet"
    return "Unknown Document"

def process_pdf(file_path, output_directory):
    document = fitz.open(file_path)
    text = extract_text_from_pdf(document)
    document_type = identify_document_type(text)
    marksheet_type = identify_marksheet(text)
    
    if document_type in ["Aadhaar Card", "PAN Card", "Offer Letter", "Appraisal"]:
        target_directory = os.path.join(output_directory, "National Documents" if document_type in ["Aadhaar Card", "PAN Card"] else "Office Documents", document_type)
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        dest_path = os.path.join(target_directory, os.path.basename(file_path))
        shutil.copy(file_path, dest_path)
        return document_type, dest_path
    elif marksheet_type != "Unknown Document":
        target_directory = os.path.join(output_directory, "Academic Documents", marksheet_type)
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        dest_path = os.path.join(target_directory, os.path.basename(file_path))
        shutil.copy(file_path, dest_path)
        return marksheet_type, dest_path
    
    # If no document type is identified, try extracting text from images in the PDF
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        img_list = page.get_images(full=True)
        for img_index, img in enumerate(img_list):
            xref = img[0]
            base_image = document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            text = extract_text_from_image(image)
            document_type = identify_document_type(text)
            marksheet_type = identify_marksheet(text)
            
            if document_type in ["Aadhaar Card", "PAN Card", "Offer Letter", "Appraisal"]:
                target_directory = os.path.join(output_directory, "National Documents" if document_type in ["Aadhaar Card", "PAN Card"] else "Office Documents", document_type)
                if not os.path.exists(target_directory):
                    os.makedirs(target_directory)
                dest_path = os.path.join(target_directory, os.path.basename(file_path))
                shutil.copy(file_path, dest_path)
                return document_type, dest_path
            elif marksheet_type != "Unknown Document":
                target_directory = os.path.join(output_directory, "Academic Documents", marksheet_type)
                if not os.path.exists(target_directory):
                    os.makedirs(target_directory)
                dest_path = os.path.join(target_directory, os.path.basename(file_path))
                shutil.copy(file_path, dest_path)
                return marksheet_type, dest_path
            
    return "Unknown Document", file_path

def process_image(file_path, output_directory):
    img = Image.open(file_path)
    text = extract_text_from_image(img)
    document_type = identify_document_type(text)
    marksheet_type = identify_marksheet(text)
    
    if document_type in ["Aadhaar Card", "PAN Card", "Offer Letter", "Appraisal"]:
        target_directory = os.path.join(output_directory, "National Documents" if document_type in ["Aadhaar Card", "PAN Card"] else "Office Documents", document_type)
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        dest_path = os.path.join(target_directory, os.path.basename(file_path))
        shutil.copy(file_path, dest_path)
        return document_type, dest_path
    elif marksheet_type != "Unknown Document":
        target_directory = os.path.join(output_directory, "Academic Documents", marksheet_type)
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        dest_path = os.path.join(target_directory, os.path.basename(file_path))
        shutil.copy(file_path, dest_path)
        return marksheet_type, dest_path
    else:
        return "Unknown Document", file_path

def load_existing_index(index_file_path):
    if os.path.exists(index_file_path):
        with open(index_file_path, 'r') as json_file:
            return json.load(json_file)
    return {}

def is_file_indexed(index, emp_id, file_name):
    if emp_id in index:
        for doc_type, files in index[emp_id].items():
            for file_info in files:
                if file_info["File"] == file_name:
                    return True
    return False

def process_files_in_folder(folder_path, output_root, index):
    new_files_indexed = 0
    results = {}
    for emp_id_folder in os.listdir(folder_path):
        emp_id_folder_path = os.path.join(folder_path, emp_id_folder)
        if not os.path.isdir(emp_id_folder_path):
            continue
        
        national_documents = []
        academic_documents = []
        office_documents = []
        
        for file_name in os.listdir(emp_id_folder_path):
            if is_file_indexed(index, emp_id_folder, file_name):
                continue
            
            file_path = os.path.join(emp_id_folder_path, file_name)
            if file_path.lower().endswith('.pdf'):
                document_type, dest_path = process_pdf(file_path, emp_id_folder_path)
            elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                document_type, dest_path = process_image(file_path, emp_id_folder_path)
            else:
                document_type = "Unsupported file format"
                dest_path = file_path
            
            if "Aadhaar Card" in document_type or "PAN Card" in document_type:
                national_documents.append({'File': file_name, 'Type': document_type, 'Path': dest_path})
            elif "10th Marksheet" in document_type or "12th Marksheet" in document_type or "Degree Marksheet" in document_type:
                academic_documents.append({'File': file_name, 'Type': document_type, 'Path': dest_path})
            elif "Offer Letter" in document_type or "Appraisal" in document_type:
                office_documents.append({'File': file_name, 'Type': document_type, 'Path': dest_path})
            
            new_files_indexed += 1
        
        results[emp_id_folder] = {
            'National Documents': national_documents,
            'Academic Documents': academic_documents,
            'Office Documents': office_documents
        }
    
    return results, new_files_indexed

def main():
    input_root = r'D:\employee data'  # Root folder containing employee ID folders
    output_root = r'D:\pr_project'  # Root folder where indexed files will be stored
    index_file_path = os.path.join(output_root, 'index.json')
    
    if not os.path.exists(output_root):
        os.makedirs(output_root)
    
    existing_index = load_existing_index(index_file_path)
    results, new_files_indexed = process_files_in_folder(input_root, output_root, existing_index)
    
    # Update the index with new results
    for emp_id, doc_types in results.items():
        if emp_id not in existing_index:
            existing_index[emp_id] = doc_types
        else:
            for doc_type, files in doc_types.items():
                if doc_type not in existing_index[emp_id]:
                    existing_index[emp_id][doc_type] = files
                else:
                    existing_index[emp_id][doc_type].extend(files)
    
    # Store the updated index in a JSON file
    with open(index_file_path, 'w') as json_file:
        json.dump(existing_index, json_file, indent=4)
    
    # Print the index
    print("Index of processed files:")
    for emp_id, doc_types in existing_index.items():
        print(f'Employee ID: {emp_id}')
        for doc_type, files in doc_types.items():
            print(f'    {doc_type}:')
            for idx, file_info in enumerate(files, start=1):
                print(f'        {idx}. File: {file_info["File"]}, Type: {file_info["Type"]}, Path: {file_info["Path"]}')
    
    print(f'\nIndex saved to: {index_file_path}')
    print(f'Total new files indexed: {new_files_indexed}')

if __name__ == "__main__":
    main()
