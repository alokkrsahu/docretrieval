import pandas as pd
import re, json



def advanced_format_text(text):
    # Remove spaces between letters that should be part of a single word
    text = re.sub(r'(\w)\s(?=\w)', r'\1', text)
    
    # Ensure proper spacing around punctuation and between words
    text = re.sub(r'(?<=[,.!?])(?=\w)', r' ', text)  # Add space after punctuation if it's missing
    text = re.sub(r'(?<=\w)(?=[A-Z])', r' ', text)  # Add space between words that are joined without spaces (e.g., "wordAnother")
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', r' ', text)  # Add space between camelCase like words (e.g., "camelCase")

    # Replace multiple spaces with a single space
    text = re.sub(r'\s{2,}', ' ', text)
    
    # Final clean-up to remove any leading or trailing spaces
    text = text.strip()

    return text

# Load the ODS file into a pandas DataFrame
df = pd.read_excel('pastcod/output_two_columns.ods', engine="odf")

# Apply the first cleaning function to remove single spaces
df = df.applymap(advanced_format_text)

# Convert the filtered DataFrame to a dictionary with 1-based indexing
data_dict = df.reset_index().rename(columns={'index': 'ID'}).set_index('ID').to_dict(orient='index')

# Display the resulting dictionary
print(data_dict)

# Assuming `data_dict` is your dictionary
with open('pastcod/output_two_columns.json', 'w') as json_file:
    json.dump(data_dict, json_file, indent=4)  # `indent=4` makes the JSON file more readable
