import boto3
import time
import random

client = boto3.client('logs')

LOG_GROUP_NAME = 'MyITOpsLogs'
LOG_STREAM_NAME = 'app-logs'

messages = [
    "INFO: System check passed",
    "WARNING: CPU usage above 75%",
    "ERROR: Application crashed due to memory overflow",
    "INFO: Backup completed successfully",
    "ERROR: Unauthorized access attempt detected"
]
def lambda_handler(event, context):
    response = client.create_log_group(logGroupName=LOG_GROUP_NAME)
    response = client.create_log_stream(logGroupName=LOG_GROUP_NAME, logStreamName=LOG_STREAM_NAME)
    for i in range(100):
        message = random.choice(messages)
        timestamp = int(time.time() * 1000)
        response = client.put_log_events(
            logGroupName=LOG_GROUP_NAME,
            logStreamName=LOG_STREAM_NAME,
            logEvents=[
                {
                    'timestamp': timestamp,
                    'message': message
                }
            ]
        )
        time.sleep(1)
