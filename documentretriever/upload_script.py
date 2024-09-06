import os
import subprocess
import re
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command):
    """Executes a shell command and returns the cleaned output."""
    try:
        logging.info(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logging.debug(f"Command output: {result.stdout}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Command '{' '.join(command)}' failed with exit code {e.returncode}")
        logging.error(f"Error output: {e.stderr.strip()}")
        raise RuntimeError(f"Command '{' '.join(command)}' failed: {e.stderr.strip()}")

def extract_path_from_output(output):
    """Extracts the path from the command output."""
    logging.debug(f"Extracting path from output: {output}")
    match = re.search(r'(?:Files have been saved to\s)(.+)', output)
    if match:
        path = match.group(1)
        logging.info(f"Extracted path: {path}")
        return path
    logging.error(f"Failed to extract path from output: {output}")
    raise ValueError(f"Invalid path in output. Got output: {output}")

def upload_files(folder_path):
    """Uploads files and returns the destination folder path."""
    if not os.path.isdir(folder_path):
        logging.error(f"The specified folder does not exist: {folder_path}")
        raise ValueError(f"The specified folder does not exist: {folder_path}")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    upload_script = os.path.join(current_dir, 'upload.py')
    
    if not os.path.isfile(upload_script):
        logging.error(f"Upload script not found: {upload_script}")
        raise FileNotFoundError(f"Upload script not found: {upload_script}")

    command = ['python3', upload_script, folder_path]
    output = run_command(command)
    return extract_path_from_output(output)

def main(folder_path):
    try:
        logging.info(f"Starting upload process for folder: {folder_path}")
        destination_folder = upload_files(folder_path)
        logging.info(f"Upload completed. Destination Folder: {destination_folder}")
        print(f"Destination Folder: {destination_folder}")
        return 0
    except (RuntimeError, ValueError, FileNotFoundError) as e:
        logging.error(f"Error during upload process: {str(e)}")
        print(f"Error: {e}")
        return 1
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        print(f"Unexpected error: {e}")
        return 2

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python upload_script.py <folder_path>")
        sys.exit(1)
    
    sys.exit(main(sys.argv[1]))
