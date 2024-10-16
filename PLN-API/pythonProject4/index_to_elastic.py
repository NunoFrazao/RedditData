"""
Author: Leandro Vieira
Module: 2
"""

from elasticsearch import Elasticsearch, helpers
import json
# Connect to Elasticsearch
es = Elasticsearch([{'scheme': 'http','host': '82.155.130.155', 'port': 9200}])

# Index name
index_name = 'analyzed_data_cache'

# Function to generate Elasticsearch actions
def generate_actions(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            doc = json.loads(line)
            yield {
                "_index": index_name,
                "_source": doc
            }

# Path to your NDJSON file
ndjson_file_path = 'analyzed_data_cache.ndjson'

# Use helpers.bulk to upload the documents
success, failed = helpers.bulk(es, generate_actions(ndjson_file_path))

print(f"Successfully indexed {success} documents.")
print(f"Failed to index {failed} documents.")
