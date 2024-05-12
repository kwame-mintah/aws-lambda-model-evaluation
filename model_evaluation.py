import json
import logging
import os
import time
from typing import Any

import boto3
import sagemaker
from sagemaker.predictor import Predictor

from models import SQSRecord, ModelEvalMessage

# The AWS region
aws_region = os.environ.get("AWS_REGION", "eu-west-2")

# Configure S3 client
s3_client = boto3.client("s3", region_name=aws_region)

# Configure SageMaker client
sagemaker_client = boto3.client(service_name="sagemaker", region_name=aws_region)

# Configure logging
logger = logging.getLogger("model-evaluation")
logger.setLevel(logging.INFO)


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

    if (
        wait_endpoint_status_in_service(endpoint_name=message.endpointName)
        != "InService"
    ):
        logger.warning(
            "Endpoint failed to deployed, will not invoke endpoint with test data."
        )
        return

    # Create predictor object for making predictions against endpoint
    # https://sagemaker.readthedocs.io/en/stable/api/inference/predictors.html#predictors
    predictor = Predictor(
        endpoint_name=message.endpointName,
        serializer=sagemaker.serializers.CSVSerializer(),
    )

    logger.info(
        "Sending test data traffic to the endpoint %s. \nPlease wait...",
        message.endpointName,
    )

    # Retrieve test data for the model endpoint
    csv_rows = retrieve_object_from_bucket(
        bucket_name=message.testDataS3BucketName, key=message.testDataS3Key
    )

    # Loop through each row in the file and use as a payload to the endpoint
    # https://sagemaker.readthedocs.io/en/stable/api/inference/predictors.html#sagemaker.predictor.Predictor.predict
    for row in csv_rows:
        payload = row.rstrip("\n")
        predictor.predict(data=payload)
        time.sleep(0.5)

    logger.info(
        "Completed invoking endpoint with test data, please see model monitoring bucket output"
    )
    return event


def wait_endpoint_status_in_service(
    endpoint_name: str, boto_client: Any = sagemaker_client
) -> str:
    """
    Wait for endpoint to reach a terminal state (InService) using describe endpoint

    :param endpoint_name: Endpoint to query
    :param boto_client: boto3 SageMaker client
    """
    describe_endpoint_response = boto_client.describe_endpoint(
        EndpointName=endpoint_name
    )
    # Possible statuses returned:
    # 'EndpointStatus': 'OutOfService'|'Creating'|'Updating'|'SystemUpdating'|'RollingBack'|'InService'
    # |'Deleting'|'Failed'|'UpdateRollbackFailed'

    while describe_endpoint_response["EndpointStatus"] == "Creating":
        describe_endpoint_response = boto_client.describe_endpoint(
            EndpointName=endpoint_name
        )
        logger.info(
            "Waiting for endpoint: %s to be in InService, currently in: %s",
            endpoint_name,
            describe_endpoint_response["EndpointStatus"],
        )
        time.sleep(15)
    logger.info(
        "Endpoint: %s, status is currently: %s",
        endpoint_name,
        describe_endpoint_response["EndpointStatus"],
    )
    return describe_endpoint_response["EndpointStatus"]


def retrieve_object_from_bucket(
    bucket_name: str, key: str, client: Any = s3_client
) -> bytes:
    """
    Get the csv file from the bucket and return as bytes.

    :param bucket_name: The bucket name containing the object.
    :param key: Key of the object to get.
    :param client: boto3 client configured to use s3
    :return: bytes from the stream
    """
    s3_object = client.get_object(Bucket=bucket_name, Key=key)
    return s3_object["Body"].read().decode("utf-8")
