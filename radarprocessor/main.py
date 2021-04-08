import json
import os
import boto3

from radarprocessor.radar_processor import radar_data

# times in radar measures are typically recorded as an offset from 0.
# However, our storage system need to have some sort of absolute time as reference,
# which can be calculated from RADAR_MEASURE_BASE_TIMESTAMP + radar_measure_time.
# The current timestamp has been arbitrarily chosen
RADAR_MEASURE_BASE_TIMESTAMP = 1571005498


def chunk(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def handler(event, context):
    """
    Triggers when objects are created in an S3 storage. Responsible for loading raw
    historical AIS information, filter any files
    :param event:
    :param context:
    :return:
    """
    # Important! This has to be initialized after mocks from moto has been set up.
    # This is the reason why we have placed the declaration inside the handler function
    s3 = boto3.client('s3')
    sqs = boto3.client('sqs')
    data_filename = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']

    print(f'File uploaded to bucket: {bucket} -> {data_filename}. Parsing...')

    data = s3.get_object(Bucket=bucket, Key=data_filename)

    print(f'Reading signals: {data_filename}, {data["ContentLength"]}...')
    signals = data['Body'].read()
    print('\tClosing data-body')
    data['Body'].close()
    print('\tDecoding data')
    signals = signals.decode('utf-8')

    print('Parsing signals...')
    filtered_signals = radar_data(signals, RADAR_MEASURE_BASE_TIMESTAMP)
    chunks = chunk(filtered_signals, 100)

    for signal_chunks in chunks:
        if len(signal_chunks) > 0:
            queue_url = os.environ.get('SQS_QUEUE_URL', '<No SQS_QUEUE_URL is set in this environment!>')
            print(f'Writing {len(signal_chunks)} items to an SQS message: {queue_url}...')
            sqs.send_message(
                QueueUrl=queue_url,
                DelaySeconds=0,
                MessageBody=json.dumps(signal_chunks)
            )
    print('Done writing!')

    # Processed files are no longer of use and can be discarded
    s3.delete_object(Bucket=bucket, Key=data_filename)

    return {
        'statusCode': 200,
        'body': '',
    }