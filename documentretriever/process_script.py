import os
import subprocess
import re
import sys

def run_command(command):
    """Executes a shell command and returns the cleaned output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command '{' '.join(command)}' failed: {e.stderr.strip()}")

def extract_path_from_output(output):
    """Extracts the path from the command output."""
    match = re.search(r'Files have been saved to (.+)', output)
    if match:
        return match.group(1)
    raise ValueError("Invalid path in output.")

def process_documents(destination_folder):
    """Processes documents and returns the path to the JSON output."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    process_script = os.path.join(current_dir, 'process.py')
    command = ['python3', process_script, destination_folder]
    output = run_command(command)
    return extract_path_from_output(output)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_script.py <destination_folder>")
        sys.exit(1)
    
    destination_folder = sys.argv[1]
    try:
        json_output_path = process_documents(destination_folder)
        print(f"JSON Output Path: {json_output_path}")
    except (RuntimeError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
