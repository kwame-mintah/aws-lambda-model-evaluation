from model_evaluation import lambda_handler
import pytest


@pytest.mark.skip(reason="skipping until implementation flow is completed")
def test_lambda_handler():
    """
    Example unit test for lambda function created, passing in
    the expected event to trigger it.
    """
    event = example_sqs_event()
    result = lambda_handler(event, None)
    assert result["Records"][0]["messageId"] == "059f36b4-87a3-44ab-83d2-661975830a7d"


def example_sqs_event():
    """
    Example SQS message event containing expected message body.
    """
    return {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
                "body": '{"endpointName": "example", "testDataS3Location" : "s3//"}',
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1545082649183",
                    "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                    "ApproximateFirstReceiveTimestamp": "1545082649185",
                },
                "messageAttributes": {},
                "md5OfBody": "098f6bcd4621d373cade4e832627b4f6",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:111122223333:my-queue",
                "awsRegion": "us-east-1",
            }
        ]
    }