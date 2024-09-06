'''
pip uninstall camelot
pip uninstall camelot-py
pip install camelot-py[cv]
pip install PyPDF2==1.26.0
pip install xlsxwriter

'''

import os
import re
import pandas as pd
import camelot
import csv
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P
from collections import defaultdict  # Import defaultdict

# Get the current PATH
current_path = os.environ.get('PATH', '')

# Define the new path to add
new_path = "/home/alok/.local/bin"

# Update the PATH environment variable
os.environ['PATH'] = f"{current_path}:{new_path}"


def sanitize_filename(filename):
    """Remove special characters from filenames."""
    return re.sub(r'[^A-Za-z0-9_\-]', '_', filename)


def extract_tables_from_odt(odt_path, output_folder):
    # Load the ODT file
    doc = load(odt_path)
    sanitized_name = sanitize_filename(os.path.splitext(os.path.basename(odt_path))[0])
    
    # Iterate through the elements in the document
    for element in doc.getElementsByType(Table):
        print(f"Extracting table from {odt_path}")
        table_data = []
        for row in element.getElementsByType(TableRow):
            row_data = []
            for cell in row.getElementsByType(TableCell):
                cell_text = ""
                for paragraph in cell.getElementsByType(P):
                    # Iterate through child nodes of the paragraph
                    for node in paragraph.childNodes:
                        if node.nodeType == 3:  # Node is a text node
                            cell_text += node.data
                        elif node.nodeType == 1:  # Node is an element node
                            cell_text += ''.join(child.data for child in node.childNodes if child.nodeType == 3)
                row_data.append(cell_text)
            table_data.append(row_data)
        
        # Save the table as CSV
        table_index = doc.getElementsByType(Table).index(element) + 1
        output_file = os.path.join(output_folder, f'{sanitized_name}_table_odt_{table_index}.csv')
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(table_data)
        print(f"Table {table_index} from {odt_path} saved as {output_file}.")


def extract_tables_from_pdf(pdf_path, output_folder):
    sanitized_name = sanitize_filename(os.path.splitext(os.path.basename(pdf_path))[0])
    try:
        # Try extracting tables using the 'stream' flavor
        tables_stream = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
        for i, table in enumerate(tables_stream):
            # Get the headers (first row)
            headers = table.df.iloc[0].tolist()
            # Concatenate all rows (excluding headers) in each column
            concatenated_row = [' '.join(table.df[col].iloc[1:].str.cat(sep='')) for col in table.df.columns]
            output_file = os.path.join(output_folder, f'{sanitized_name}_table_stream_{i+1}.csv')
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerow(concatenated_row)
            print(f"Single-row table {i+1} from {pdf_path} (stream) saved as {output_file}.")
    except IndexError:
        # Handle the case where the 'stream' flavor fails
        print(f"Stream method failed for {pdf_path}. Trying lattice flavor.")
        try:
            tables_lattice = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
            for i, table in enumerate(tables_lattice):
                output_file = os.path.join(output_folder, f'{sanitized_name}_table_lattice_{i+1}.csv')
                table.to_csv(output_file)
                print(f"Table {i+1} from {pdf_path} (lattice) saved as {output_file}.")
        except Exception as e:
            print(f"Failed to extract tables from {pdf_path} using both stream and lattice methods. Error: {str(e)}")


def process_folder(folder_path, output_folder):
    # Create the output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Traverse the directory and its subfolders
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, folder_path)
            output_subfolder = os.path.join(output_folder, os.path.dirname(relative_path))
            os.makedirs(output_subfolder, exist_ok=True)
            if file.endswith('.odt'):
                extract_tables_from_odt(file_path, output_subfolder)
            elif file.endswith('.pdf'):
                extract_tables_from_pdf(file_path, output_subfolder)


def find_and_group_csv_files(folder_path):
    # A dictionary to hold lists of DataFrames, keyed by the number of columns
    column_groups = defaultdict(list)

    # Traverse the directory and its subfolders to find CSV files
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                try:
                    # Read the CSV file without headers
                    df = pd.read_csv(file_path, header=None, skiprows=1)
                    
                    # Determine the number of columns and append to the appropriate list
                    num_columns = df.shape[1]
                    column_groups[num_columns].append(df)
                except pd.errors.ParserError as e:
                    print(f"Error parsing {file_path}: {str(e)}")
                except Exception as e:
                    print(f"Error reading {file_path}: {str(e)}")

    # Concatenate all DataFrames in each group and return them
    grouped_dataframes = {}
    for num_columns, df_list in column_groups.items():
        grouped_dataframes[num_columns] = pd.concat(df_list, ignore_index=True)

    return grouped_dataframes


def save_dataframe_with_times_new_roman(df, output_file):
    # Save the DataFrame to an Excel file with Times New Roman font
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        
        # Define the Times New Roman format
        times_new_roman_format = workbook.add_format({'font_name': 'Times New Roman'})
        
        # Apply the format to the entire sheet
        worksheet.set_column('A:Z', None, times_new_roman_format)
        worksheet.set_default_row(None, times_new_roman_format)



folder_path = '/home/alok/Documents/alok/files/files/SalesProject/Data/G-Drive'
output_folder = '/home/alok/Documents/alok/files/files/SalesProject/Data/G-Drive-Output'
process_folder(folder_path, output_folder)
grouped_dataframes = find_and_group_csv_files(output_folder)

#print(grouped_dataframes)

if 1 in grouped_dataframes:
    df_one_columns = grouped_dataframes[1]
    save_dataframe_with_times_new_roman(df_one_columns, '/home/alok/Documents/working_tenders/v2/pastcod/output_one_columns.xlsx')
    
if 2 in grouped_dataframes:
    df_two_columns = grouped_dataframes[2]
    save_dataframe_with_times_new_roman(df_two_columns, '/home/alok/Documents/working_tenders/v2/pastcod/output_two_columns.xlsx')

if 3 in grouped_dataframes:
    df_three_columns = grouped_dataframes[3]
    save_dataframe_with_times_new_roman(df_three_columns, '/home/alok/Documents/working_tenders/v2/pastcod/output_three_columns.xlsx')


print("DONE")
