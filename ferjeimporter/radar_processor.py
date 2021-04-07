# ferjeimporter/ais_processor.py
from dataclasses import dataclass
import datetime as dt
import uuid

#import numpy as np
# ...
# 

def radar_data(csv_data,start_time_EPOCH,timezone):
    # csv-file on format: time, lon, lat, heading(TimeInSecondsPosix,V1x,V1y,V1Heading)
    #start_time_EPOCH i.e 1347516459425 evaluates to 2012-09-12 02:22:50 
    #timezone: 1 for norway
    rows = [x.split(',') for x in csv_data.split('\n')]
    header_row = rows[0]
    header_row_lookup = {}
    for index, value in enumerate(header_row):
        header_row_lookup[value.strip()] = index

    print(header_row_lookup)
    data = []
    for row in rows[1:]:
        if len(row) < len(header_row_lookup):
            print(f"Columns in row is shorter than header columns: {row}")
            continue
        time = float(row[header_row_lookup['TimeInSecondsPosix']])
        datetime_time = dt.datetime.fromtimestamp(start_time_EPOCH + time)
        ship_signal = {}
        ship_signal['timestamp'] = (str(datetime_time), '+0', str(timezone),':00')
        ship_signal['ferryId'] = uuid.uuid4()
        ship_signal['lat'] = float(row[header_row_lookup['V1y']])
        ship_signal['lon'] = float(row[header_row_lookup['V1x']])
        ship_signal['source'] = "radar"
        metadata = {}
        metadata["heading"] = float(row[header_row_lookup['V1Heading']])
        metadata["widht"] = 1
        metadata["lenghth"] = 5
        metadata["type"] = 37
        ship_signal['metadata']=metadata
        data.append(ship_signal)
    return data

# if __name__ == "__main__":
#     with open("ScenarioLatLon.csv", "r") as f:
#         csv_data = f.read()
#     data=radar_data(csv_data,1571005498,1)
#     print(data)