import re
import requests
from datetime import datetime
import json
import pandas as pd

# Function to fetch station data from GasBuddy website
def fetch_station_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        js_data = re.search(r'window\.__APOLLO_STATE__ = ({.*?});', response.text).group(1)
        data = json.loads(js_data)
        return data
    else:
        print("Failed to fetch data from GasBuddy. Status code:", response.status_code)
        return None

# Function to update station info CSV
def update_station_info_csv(station_data):
    # check if the station info CSV exists else create it with defined columns
    try:
        station_info = pd.read_csv("./Data/stationInfo.csv")
    except FileNotFoundError:
        station_info = pd.DataFrame(columns=["stationID", "StationName", "address"])
        
    new_stations = []
    if station_data:
        station_id = station_data['id']
        if station_id not in station_info["stationID"].values:
            new_stations.append({
                "stationID": station_id,
                "StationName": station_data['name'],
                "address": station_data['address']['line1'] + ", " + station_data['address']['locality'] + ", " + station_data['address']['region'] + " " + station_data['address']['postalCode']
            })

    if new_stations:
        new_stations_df = pd.DataFrame(new_stations)
        station_info = pd.concat([station_info, new_stations_df], ignore_index=True)
        station_info.to_csv("./Data/stationInfo.csv", index=False)

# Function to update logger CSV
def update_logger_csv(data):
    # check if the logger CSV exists else create it with defined columns
    try:
        logger = pd.read_csv("./Data/logger.csv")
    except FileNotFoundError:
        logger = pd.DataFrame(columns=["stationID", "date", "regularGasPrice"])

    if data:
        station_id = data['id']
        iso_date_time = data['prices'][0]['credit']['postedTime']
        date_time = datetime.fromisoformat(iso_date_time[:-1]).strftime("%Y-%m-%d %H:%M:%S")
        regular_gas_price = data['prices'][0]['credit']['price']
        ## Append the new data to the logger
        logger = logger._append({
            "stationID": station_id,
            "date": date_time,
            "regularGasPrice": regular_gas_price
        }, ignore_index=True)

    logger.to_csv("./Data/logger.csv", index=False)

# URL of the GasBuddy station
URL = "https://www.gasbuddy.com/station/87143"
station_data = fetch_station_data(URL)

URL2 = "https://www.gasbuddy.com/station/15371"
station_data2 = fetch_station_data(URL2)

if station_data and station_data2:
    thortons = station_data['Station:87143']
    speedway = station_data['Station:17220']
    sams_club = station_data2['Station:15371']
    # Update the station info CSV and logger CSV for both stations
    update_station_info_csv(thortons)
    update_logger_csv(thortons)
    update_station_info_csv(speedway)
    update_logger_csv(speedway)
    update_logger_csv(sams_club)
    update_station_info_csv(sams_club)
    print("Data updated successfully.")
