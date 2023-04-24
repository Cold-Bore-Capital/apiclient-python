from api import BrightLocalAPI, BrightLocalBatch
import json
from dotenv import find_dotenv, load_dotenv
import os
import time
from requests.exceptions import RequestException

class BatchCreateException(RequestException):
    pass

load_dotenv(find_dotenv())
directory = 'google'

# Step 1: Create a new batch
api_key = os.getenv('BRIGHT_LOCAL_API_KEY')
api_secret = os.getenv('BRIGHT_LOCAL_API_SECRET')
api = BrightLocalAPI(api_key, api_secret)
batch_id = api.create_batch()
print(f"Created batch ID {batch_id}")

# Step 2: Add directory jobs to batch
batch = BrightLocalBatch(api_key, api_secret, batch_id)
searches = ['vetinerary', 'vetinerary near me']
job_params = {
    'search-engine': directory,
    'country': 'USA',
    'google-location': 'Nashville, NSH',
    'search-terms': json.dumps(searches),
    'urls': json.dumps(['https://mypetswellness.net/']),
    'business-names': json.dumps(['mypetswellness'])
}
try:
    response = batch.add_job('/rankings/bulk-search', job_params)
    print(f"Added job with ID {response.get_result()['job-id']}")
except BatchCreateException as e:
    print(f"Error, job for directory \"{directory}\" not added. Message: {e.message}")

# Commit batch (to indicate that all jobs have been added and that processing should start)
batch.commit()
print("Batch committed successfully, awaiting results.")

while True:
    response = batch.get_results()
    if response.get_result()['status'] in ['Stopped', 'Finished']:
        print(response.get_result())
        break
    else:
        time.sleep(5)