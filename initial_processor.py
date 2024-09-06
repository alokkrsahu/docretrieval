import os
import sys
import subprocess

def run_script(script_name, *args):
    script_path = os.path.join(os.path.dirname(__file__), 'documentretriever', f'{script_name}.py')
    result = subprocess.run(['python3', script_path, *args], 
                            capture_output=True, text=True, check=True)
    return result.stdout.strip()

def extract_path(output, prefix):
    for line in output.split('\n'):
        if line.startswith(prefix):
            return line.split(prefix)[-1].strip()
    raise ValueError(f"Could not find path in output: {output}")

def process_all_documents(tenderdocs):
    # Upload all documents
    upload_output = run_script('upload', tenderdocs)
    destination_folder = extract_path(upload_output, "Files have been saved to")
    
    # Process all documents
    process_output = run_script('process', destination_folder)
    json_output_path = extract_path(process_output, "Files have been saved to")
    
    return json_output_path

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python initial_processor.py <path_to_tenderdocs>")
        sys.exit(1)
    
    tenderdocs = sys.argv[1]
    processed_docs_path = process_all_documents(tenderdocs)
    print(f"All documents processed. Output saved to: {processed_docs_path}")
