import os
import argparse
import shutil
import logging
import random
import string
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def save_files_to_timestamped_folder(folder_path):
    # Create the main "all_files" folder if it doesn't exist
    main_folder = "all_files"
    os.makedirs(main_folder, exist_ok=True)
    logging.info(f"Ensuring main folder exists: {main_folder}")

    # Create a timestamped subfolder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination_folder = os.path.join(main_folder, timestamp)
    
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            os.makedirs(destination_folder)
            logging.info(f"Created destination folder: {destination_folder}")
            break
        except FileExistsError:
            logging.warning(f"Destination folder already exists: {destination_folder}")
            # Append a unique identifier to the folder name
            unique_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            destination_folder = f"{destination_folder}_{unique_id}"
            retry_count += 1
    
    if retry_count == max_retries:
        raise RuntimeError(f"Failed to create a unique destination folder after {max_retries} attempts")

    # Walk through the provided folder path and save each file
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(file_path, folder_path)
            destination_path = os.path.join(destination_folder, relative_path)
            
            # Create necessary subfolders in the destination path
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Copy file to the destination path
            try:
                shutil.copy2(file_path, destination_path)
                logging.info(f"Copied file: {file_path} to {destination_path}")
            except Exception as e:
                logging.error(f"Error copying file {file_path}: {str(e)}")

    return destination_folder

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Upload files from a folder to a timestamped folder.")
    parser.add_argument('folder_path', type=str, help="Path to the folder containing files to be uploaded")
    args = parser.parse_args()

    # Check if the provided path is a directory
    if not os.path.isdir(args.folder_path):
        logging.error(f"The provided path '{args.folder_path}' is not a valid directory.")
        return

    try:
        # Save files to the timestamped folder and get the destination folder path
        destination_folder = save_files_to_timestamped_folder(args.folder_path)
        
        # Print and log the path where files were saved
        message = f"Files have been saved to {destination_folder}"
        print(message)
        logging.info(message)
        
        return destination_folder
    except Exception as e:
        logging.error(f"An error occurred during the upload process: {str(e)}")
        raise

if __name__ == "__main__":
    main()
