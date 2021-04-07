import json
import os
import boto3

from ferjeimporter.radar_processor import radar_data


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
    filtered_signals = radar_data(data_filename,1571005498, 1)

    if len(filtered_signals) > 0:
        queue_url = os.environ.get('SQS_QUEUE_URL', '<No SQS_QUEUE_URL is set in this environment!>')
        print(f'Writing {len(filtered_signals)} items to an SQS message: {queue_url}...')
        sqs.send_message(
            QueueUrl=queue_url,
            DelaySeconds=0,
            MessageBody=json.dumps(filtered_signals)
        )
        print('Done writing!')

    # Processed files are no longer of use and can be discarded
    s3.delete_object(Bucket=bucket, Key=data_filename)

    return {
        'statusCode': 200,
        'body': ''
    }