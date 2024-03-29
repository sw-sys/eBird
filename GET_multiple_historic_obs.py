import os
import requests
import pandas as pd
from datetime import date
import json
from concurrent.futures import ThreadPoolExecutor
import calendar
import re

# go to ebird api, pass key 
def download_file(url, folder, timeout=60):
    try:
        response = requests.get(url, headers={'X-eBirdApiToken': 'YOURKEYHERE'}, timeout=timeout)
        print(response.status_code)
        if "content-disposition" in response.headers:
            content_disposition = response.headers["content-disposition"]
            filename = re.search(r'filename="(.*?)"', content_disposition).group(1)
        else:
            filename = url.split("/")[-1]
        filepath = os.path.join(folder, filename)
        with open(filepath, mode="wb") as file:
            file.write(response.content)
        print(f"Downloaded file {filename}")

        # Process the API response and save to CSV
        data = json.loads(response.text)
        df = pd.DataFrame(data)
        date_parts = url.split("/")[-3:]
        daily_csv_path = os.path.join(folder, f"{date_parts[0]}-{date_parts[1]}-{date_parts[2]}_bird_obs.csv")
        df.to_csv(daily_csv_path, index=False)
        return daily_csv_path
    except requests.exceptions.Timeout as e:
            print(f"Timeout error for {url}: {e}")
            return None
    except Exception as e:
            print(f"Error downloading {url}: {e}")
            return None

# gen urls to dl daily data
template_url = "https://api.ebird.org/v2/data/obs/GB-ENG/historic/{y}/{m}/{d}"
base_folder = "downloads"
monthly_data_folder = "monthly data"

# file mgt 
if not os.path.exists(base_folder):
    os.makedirs(base_folder)

if not os.path.exists(monthly_data_folder):
    os.makedirs(monthly_data_folder)

#set date range for data to dl
for year in range(2014, 2020):
    for month in range(1, 13):
        month_folder = os.path.join(base_folder, f"{year}-{month:02}")
        if not os.path.exists(month_folder):
            os.makedirs(month_folder)
        
        num_days = calendar.monthrange(year, month)[1]
        daily_csv_paths = []
        for day in range(1, num_days + 1):
            url = template_url.format(y=year, m=month, d=day)
            daily_csv_path = os.path.join(month_folder, f"{year}-{month:02}-{day:02}_bird_obs.csv")
            if os.path.exists(daily_csv_path):
                print(f"Skipping download of {daily_csv_path} as it already exists.")
                daily_csv_paths.append(daily_csv_path)
                continue
            daily_csv_path = download_file(url, month_folder, timeout=120)
            daily_csv_paths.append(daily_csv_path)

            # Loop through the daily CSV files
            for daily_csv_path in daily_csv_paths:
                # Read the daily CSV file
                df = pd.read_csv(daily_csv_path)
                # Normalize the 'locName' column - remove commas from addresses
                df['locName'] = df['locName'].str.replace(',', ' -')
                # Write the updated DataFrame back to the daily CSV file
                df.to_csv(daily_csv_path, index=False)
        
        # Combine daily CSV files into a single monthly CSV file
        monthly_csv_path = os.path.join(monthly_data_folder, f"{year}-{month:02}_bird_obs.csv")
        combined_df = pd.concat([pd.read_csv(path) for path in daily_csv_paths])
        combined_df.to_csv(monthly_csv_path, index=False)
        print(f"Created monthly CSV file: {monthly_csv_path}")