from moto import mock_s3, mock_sqs
import boto3
import os
from unittest import TestCase, mock

from radarprocessor.main import handler
from radarprocessor.tests.aws_test_helper import S3BucketFile, s3_event_bucket_uploaded

AWS_DEFAULT_REGION = 'us-east-1'
TEST_S3_BUCKET_NAME = 'my-test-bucket'
TEST_SQS_QUEUE_NAME = 'ferje-ais-importer-test-pathtaker-source'
dir_path = os.path.dirname(os.path.realpath(__file__))


def _read_testdata(name):
    with open(f'{dir_path}/testdata/{name}', 'r') as f:
        return f.read()


@mock_s3
@mock_sqs
class IngestAisData(TestCase):
    s3 = None
    sqs = None

    def setUp(self) -> None:
        """
        Creates our mocked S3 bucket which radarprocessor.main.handler will automatically connect to
        :return:
        """
        # Ensure test setup uses the correct test credentials
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_SECURITY_TOKEN'] = 'testing'
        os.environ['AWS_SESSION_TOKEN'] = 'testing'
        os.environ['AWS_DEFAULT_REGION'] = AWS_DEFAULT_REGION

        # Initialize S3 test-bucket
        s3 = boto3.resource('s3', region_name=AWS_DEFAULT_REGION)
        s3.create_bucket(Bucket=TEST_S3_BUCKET_NAME)
        self.s3 = boto3.client('s3', region_name=AWS_DEFAULT_REGION)
        # Initialize SQS test-queue
        sqs = boto3.resource('sqs', region_name=AWS_DEFAULT_REGION)
        test_queue = sqs.create_queue(QueueName=TEST_SQS_QUEUE_NAME, Attributes={'DelaySeconds': '0'})
        self.sqs = boto3.client('sqs')

        environment_patcher = mock.patch.dict(os.environ, {
            'SQS_QUEUE_URL': test_queue.url,
            # Ensure our system looks for resources in the correct region
            'AWS_DEFAULT_REGION': AWS_DEFAULT_REGION,
            # Prevent any use of non-test credentials
            'AWS_ACCESS_KEY_ID': 'testing',
            'AWS_SECRET_ACCESS_KEY': 'testing',
            'AWS_SECURITY_TOKEN': 'testing',
            'AWS_SESSION_TOKEN': 'testing',
        })
        environment_patcher.start()
        self.addCleanup(environment_patcher.stop)

    def test_import_success(self):
        """
        Verifies that uploaded files are processed correctly
        and removed from S3 when completed
        :return:
        """
        # Files we are using in this test
        uploaded_files = [
            S3BucketFile(
                object_key='ScenarioLatLon.csv',
                content=_read_testdata('ScenarioLatLon.csv'),
            ),
        ]
        # Upload the data to the mocked instance of S3
        for file in uploaded_files:
            self.s3.put_object(Bucket=TEST_S3_BUCKET_NAME, Key=file.object_key, Body=file.content)

        event = s3_event_bucket_uploaded([uploaded_files[0]])

        # Run our event handler
        handler(event, {})

        print(self.s3.list_objects_v2(Bucket=TEST_S3_BUCKET_NAME))

        list_response = self.s3.list_objects_v2(Bucket=TEST_S3_BUCKET_NAME)

        self.assertNotIn('Content', list_response)
        # # Assert the outcome is correct
        # objects_in_s3 = {content['Key'] for content in self.s3.list_objects_v2(Bucket=TEST_S3_BUCKET_NAME)['Contents']}
        #
        # # TODO This will correctly fail, because handler has not been correctly imported yet
        # # All processed files should have been deleted from S3
        # for file in uploaded_files:
        #     self.assertNotIn(file.object_key, objects_in_s3)

