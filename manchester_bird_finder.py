from ebird.api  import get_notable_observations
import json
import pandas as pd

api_key = "APIKEYHERE"

# Get interesting birds seen in a specific location
interesting_records_manc = get_notable_observations(api_key, 'GB-ENG-MAN') # arg2 e.g. US-NY

# write json and create df
df = pd.read_json('manchester_interesting_records.json')

#convert df to csv
df.to_csv('interesting-manchester-birds.csv')
