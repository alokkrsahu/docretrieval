import os
import json
import argparse
import logging
import pdfplumber
from docx import Document
from odf.opendocument import load
from odf.text import P

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_paragraphs_from_pdf(file_path):
    paragraphs = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    paragraphs.extend(text.split('\n\n'))  # Assuming paragraphs are separated by double newlines
        logging.info(f"Successfully extracted {len(paragraphs)} paragraphs from PDF: {file_path}")
    except Exception as e:
        logging.error(f"Error reading .pdf file '{file_path}': {e}")
    return paragraphs

def extract_paragraphs_from_docx(file_path):
    paragraphs = []
    try:
        doc = Document(file_path)
        for paragraph in doc.paragraphs:
            paragraphs.append(paragraph.text)
        logging.info(f"Successfully extracted {len(paragraphs)} paragraphs from DOCX: {file_path}")
    except Exception as e:
        logging.error(f"Error reading .docx file '{file_path}': {e}")
    return paragraphs

def extract_paragraphs_from_odt(file_path):
    paragraphs = []
    try:
        odt_file = load(file_path)
        paragraphs_elements = odt_file.getElementsByType(P)
        for paragraph in paragraphs_elements:
            paragraphs.append(paragraph.textContent)
        logging.info(f"Successfully extracted {len(paragraphs)} paragraphs from ODT: {file_path}")
    except Exception as e:
        logging.error(f"Error reading .odt file '{file_path}': {e}")
    return paragraphs

def extract_text_from_folder(folder_path):
    output = []
    paragraph_id = 1
    unsupported_files = []
    # Traverse the folder and subfolders
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            logging.info(f"Processing file: {file_path}")
            if file_name.endswith('.pdf'):
                paragraphs = extract_paragraphs_from_pdf(file_path)
            elif file_name.endswith('.docx'):
                paragraphs = extract_paragraphs_from_docx(file_path)
            elif file_name.endswith('.odt'):
                paragraphs = extract_paragraphs_from_odt(file_path)
            else:
                unsupported_files.append(file_name)
                logging.warning(f"Skipping unsupported file format: {file_name}")
                continue
            for para in paragraphs:
                if para:  # Ensure that we are not adding empty paragraphs
                    output.append({"id": paragraph_id, "text": para})
                    paragraph_id += 1
    logging.info(f"Extracted a total of {len(output)} paragraphs from all documents")
    return output, unsupported_files

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Extract text from documents in a specified folder.")
    parser.add_argument('folder_path', type=str, help="Path to the folder containing the documents")
    args = parser.parse_args()

    # Check if the provided path is a directory
    if not os.path.isdir(args.folder_path):
        logging.error(f"The provided path '{args.folder_path}' is not a valid directory.")
        print(f"Error: The provided path '{args.folder_path}' is not a valid directory.")
        return

    # Create the output directory inside destination_folder if it does not exist
    output_dir = os.path.join(args.folder_path, 'sys', 'temp')
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"Created output directory: {output_dir}")

    # Process the folder and extract text
    documents, unsupported_files = extract_text_from_folder(args.folder_path)

    # Write the extracted text data to a JSON file
    output_file_path = os.path.join(output_dir, 'extracted_data.json')
    with open(output_file_path, 'w') as f:
        json.dump(documents, f, indent=2)
    logging.info(f"Wrote extracted data to JSON file: {output_file_path}")

    # Print the path to the JSON file
    print(f"Files have been saved to {output_file_path}")

    # Print information about unsupported files
    if unsupported_files:
        logging.warning("The following files were skipped due to unsupported format:")
        for file in unsupported_files:
            logging.warning(f"  - {file}")
        print("Warning: Some files were skipped due to unsupported format. Check the log for details.")

if __name__ == "__main__":
    main()
