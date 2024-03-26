from pydantic import Field, BaseModel


class S3Record:
    """Instantiated record from an S3 Event"""

    def __init__(self, event: dict):
        self.event_name = event["Records"][0]["eventName"]
        self.bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        self.object_key = event["Records"][0]["s3"]["object"]["key"]


class SQSRecord:
    """Instantiated record from an SQS Event"""

    def __init__(self, event: dict):
        self.message_id = event["Records"][0]["messageId"]
        self.body = event["Records"][0]["body"]
        self.event_source = event["Records"][0]["eventSource"]


# https://docs.pydantic.dev/latest/api/fields/#pydantic.fields.FieldInfo
class ModelEvalMessage(BaseModel):
    endpointName: str = Field(title="AWS SageMaker endpoint created")
    testDataS3BucketName: str = Field(title="AWS S3 Bucket name contain test data")
    testDataS3Key: str = Field(title="Full path of object within AWS S3 Bucket")
