from api import BrightLocalAPI
import json
from dotenv import find_dotenv, load_dotenv
import os
import time


load_dotenv(find_dotenv())
directory = 'google'

# Step 1: Create a new batch
api_key = os.getenv('BRIGHT_LOCAL_API_KEY')
api_secret = os.getenv('BRIGHT_LOCAL_API_SECRET')
api = BrightLocalAPI(api_key, api_secret)
api.batch_id = api.create_batch()
print(f"Created batch ID {api.batch_id}")

# Step 2: Add directory jobs to batch
searches = ['vetinerary', 'vetinerary near me']
job_params = {
    'search-engine': directory,
    'country': 'USA',
    'google-location': 'Nashville, NSH',
    'search-terms': json.dumps(searches),
    'urls': json.dumps(['https://mypetswellness.net/']),
    'business-names': json.dumps(['mypetswellness'])
}
#try:
response = api.add_job('https://tools.brightlocal.com/seo-tools/api/v4/rankings/bulk-search', job_params)
print(f"Added job with ID {response.get_result()['job-id']}")
#except Exception as e:
   # print(f"Error, job for directory \"{directory}\" not added. Message: {e.message}")

# Commit batch (to indicate that all jobs have been added and that processing should start)
api.batch_id.commit()
print("Batch committed successfully, awaiting results.")

while True:
    response = api.batch_id.get_results()
    if response.get_result()['status'] in ['Stopped', 'Finished']:
        print(response.get_result())
        break
    else:
        time.sleep(5)