# ferjeimporter/ais_processor.py
from dataclasses import dataclass
import datetime as dt
import pytz
import hashlib
# ...
# 

@dataclass
class CoordinatesArea:
    min_lat: float = 0
    min_lon: float = 0
    max_lat: float = 0
    max_lon: float = 0


# Defines a range of lat and lon that each signal should be in.
# We start with a fairly small area, to avoid storing too much data.
VALID_OPERATING_AREA = CoordinatesArea(
    min_lat=63.0,
    max_lat=64.0,
    min_lon=7,
    max_lon=10.5999
)

def hash_mmsi(mmsi):
    return hashlib.sha256(mmsi.encode()).hexdigest()

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
        lon=float(row[header_row_lookup['V1x']])
        lat=float(row[header_row_lookup['V1y']])
        time = float(row[header_row_lookup['TimeInSecondsPosix']])
        datetime_time = dt.datetime.fromtimestamp(start_time_EPOCH + time)
        print(datetime_time)
        ship_signal = {}
        ship_signal['timestamp'] = str(datetime_time) + '+0' + str(timezone) +':00'
        ship_signal['lat'] = lat
        ship_signal['lon'] = lon
        ship_signal['source'] = "radar"
        metadata = {}
        metadata["heading"] = float(row[header_row_lookup['V1Heading']])
        ship_signal['metadata']=metadata
        data.append(ship_signal)
    return data

if __name__ == '__main__':
    # Enkel måte å mate inn eksempelinput
    radar_signals = """TimeInSecondsPosix,V1x,V1y,V1Heading
2488,63.4350806,10.3925694,6.2083507676063
2488.10006671114,63.4350804556213,10.3925717383907,6.2083507676063
2488.20013342228,63.4350803294644,10.3925739755931,6.2148168217095
2488.30020013342,63.4350802204113,10.3925761158818,6.22139227564389
2488.40026684456,63.4350801273442,10.3925781635315,6.22805033563528
2488.5003335557,63.4350800491451,10.3925801228169,6.23475792912945
2488.60040026684,63.4350799846961,10.3925819980126,6.24147494941483
2488.70046697799,63.4350799328792,10.3925837933933,6.24815351284129
2488.80053368913,63.4350798925765,10.3925855132337,6.25473723764601
2488.90060040027,63.4350798626701,10.3925871618084,6.26116071489985"""

    data=radar_data(radar_signals,1571005498,1)
    print(data)