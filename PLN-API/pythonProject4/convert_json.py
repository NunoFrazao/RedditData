"""
Author: Leandro Vieira
Module: 2
"""

import json

# Function to convert JSON to NDJSON
def json_to_ndjson(json_file, ndjson_file):
    # Read the JSON data from the input file
    with open(json_file, 'r') as infile:
        data = json.load(infile)
        
    # Ensure the data is a list of objects
    if not isinstance(data, list):
        raise ValueError("JSON data must be an array of objects.")

    # Write the NDJSON data to the output file
    with open(ndjson_file, 'w') as outfile:
        for item in data:
            json.dump(item, outfile)
            outfile.write('\n')

# Example usage
json_to_ndjson('analyzed_data_cache.txt', 'analyzed_data_cache.ndjson')
