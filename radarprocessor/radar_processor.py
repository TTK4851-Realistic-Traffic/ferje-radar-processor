from datetime import datetime
import uuid

import pytz

TIMEZONE_NORWAY = pytz.timezone('Europe/Oslo')
TIMEZONE_UTC = pytz.timezone('UTC')


def _build_timestamp_utc(time_start_base: int, time_offset: float) -> str:
    time = datetime.fromtimestamp(time_start_base + time_offset)
    time_source_localized = TIMEZONE_NORWAY.localize(time)
    return str(time_source_localized.astimezone(TIMEZONE_UTC))


def radar_data(csv_data,start_time_EPOCH):
    # csv-file on format: time, lon, lat, heading(TimeInSecondsPosix,V1x,V1y,V1Heading)
    #start_time_EPOCH i.e 1347516459425 evaluates to 2012-09-12 02:22:50 
    #timezone: 1 for norway
    rows = [x.split(',') for x in csv_data.split('\n')]
    ferryId = str(uuid.uuid4())
    header_row = rows[0]
    header_row_lookup = {}
    for index, value in enumerate(header_row):
        header_row_lookup[value.strip()] = index

    data = []
    for row in rows[1:]:
        if len(row) < len(header_row_lookup):
            print(f"Columns in row is shorter than header columns: {row}")
            continue

        time_offset_from_epoch = float(row[header_row_lookup['TimeInSecondsPosix']])

        ship_signal = {
            'timestamp': _build_timestamp_utc(start_time_EPOCH, time_offset_from_epoch),
            'ferryId': ferryId,
            # TODO V1x should actually be longitude, but is in the source set set as latitude
            'lat': float(row[header_row_lookup['V1x']]),
            'lon': float(row[header_row_lookup['V1y']]),
            'source': 'radar',
            'metadata': {
                'heading': float(row[header_row_lookup['V1Heading']]),
                # Estimating width and length was out of scope for the current project,
                # but has potential for future work
                'width': 1,
                'length': 5,
                # This type is chosen based on the assumption that most vessels tracked
                # by this radar is some sort of leisure craft. We may wish to
                # estimate a more precise type, at a later moment
                'type': 37,
            },
        }
        data.append(ship_signal)
    return data
