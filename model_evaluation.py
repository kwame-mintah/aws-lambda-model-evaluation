import json
import logging
import os
import time
from typing import Any

import boto3
import sagemaker
from sagemaker.predictor import Predictor

from models import SQSRecord, ModelEvalMessage

# Configure S3 client
s3_client = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "eu-west-2"))

# Configure logging
logger = logging.getLogger("model-evaluation")
logger.setLevel(logging.INFO)

# The output bucket name
PREPROCESSED_OUTPUT_BUCKET_NAME = os.environ.get("PREPROCESSED_OUTPUT_BUCKET_NAME")


def lambda_handler(event, context):
    """
    Invoke created endpoint and use test data to generate baseline constraints
    """
    sqs_record = SQSRecord(event)
    logger.info(
        "Received messageId: %s from source: %s with message: %s",
        sqs_record.message_id,
        sqs_record.event_source,
        sqs_record.body,
    )

    message = ModelEvalMessage(**json.loads(sqs_record.body))

    predictor = Predictor(
        endpoint_name=message.endpointName,
        serializer=sagemaker.serializers.CSVSerializer(),
    )

    logger.info(
        "Sending test traffic to the endpoint %s. \nPlease wait...",
        message.endpointName,
    )

    # TODO: Read CSV from S3 Bucket
    with open("test_data/test_sample.csv", "r") as f:
        for row in f:
            payload = row.rstrip("\n")
            response = predictor.predict(data=payload)
            time.sleep(0.5)

    logger.info("Done!")

    return event


def retrieve_object_from_bucket(key: str, client: Any = s3_client) -> bytes:
    """
    Get the csv file from the bucket and return as bytes.

    :param client: boto3 client configured to use s3
    :param key: The full path to object
    :return: bytes from the stream
    """
    s3_object = client.get_object(Bucket=PREPROCESSED_OUTPUT_BUCKET_NAME, Key=key)
    return s3_object["Body"].read().decode("utf-8")
