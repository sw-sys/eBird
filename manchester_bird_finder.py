from ebird.api  import get_notable_observations
import json

api_key = "APIKEYHERE"

  # Get interesting birds seen in a specific location
interesting_records_manc = get_notable_observations(api_key, 'GB-ENG-MAN') # arg2 e.g. US-NY
  # create dictionary of data
dict = interesting_records_manc
  # open new file
out_file = open("manchester_interesting_records.json", "w")
  # put json in to file
json.dump(dict, out_file, indent=6)
  #close file
out_file.close()
