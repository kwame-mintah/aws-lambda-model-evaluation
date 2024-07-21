import json
import logging
import os
import time
from datetime import datetime
from typing import Any

import boto3
import numpy as np
import pandas as pd
import sagemaker
from sagemaker.predictor import Predictor

from models import SQSRecord, ModelEvalMessage

# The AWS region
aws_region = os.environ.get("AWS_REGION", "eu-west-2")

# Configure S3 client
s3_client = boto3.client(service_name="s3", region_name=aws_region)

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

    # Check that the endpoint is ready to receive requests.
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
    sagemaker_session = sagemaker.Session()
    predictor = Predictor(
        endpoint_name=message.endpointName,
        sagemaker_session=sagemaker_session,
        serializer=sagemaker.serializers.CSVSerializer(),
    )

    # Read the test data CSV from the bucket and exclude the first column.
    data = pd.read_csv(
        filepath_or_buffer="s3://{bucket_name}/{bucket_key}".format(
            bucket_name=message.testDataS3BucketName, bucket_key=message.testDataS3Key
        ),
        index_col=0,
    )

    logger.info("Will use {rows} rows for prediction(s)".format(rows=data.shape[0]))

    logger.info(
        "Sending test data to the endpoint %s. \nPlease wait...",
        message.endpointName,
    )
    predictions = perform_predictions(
        data=data.drop(["y_no", "y_yes"], axis=1).to_numpy(), predictor=predictor
    )

    # Create confusion matrix to see how well the model predicted vs. actuals.
    # Then save to S3 bucket to be reviewed later.
    pd.crosstab(
        index=data["y_yes"],
        columns=np.round(predictions),
        rownames=["actuals"],
        colnames=["predictions"],
    ).to_markdown(
        buf="s3://{bucket_name}/{today}/predictions/{endpoint_name}/PREDICTIONS.md".format(
            bucket_name=message.testDataS3BucketName,
            today=str(datetime.now().strftime("%Y-%m-%d")),
            endpoint_name=message.endpointName,
        ),
        tablefmt="grid",
    )

    logger.info(
        "Completed invoking endpoint with test data, please confusion matrix created for model"
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


def perform_predictions(data: np.ndarray, predictor: Predictor, rows=500) -> np.ndarray:
    """
    Use test dataset and split into mini-batches of rows, converting these batches
    into CSV string payloads, dropping the target variable from the dataset first.
    Then invoke the endpoint for predictions.

    :param data: The test dataset used for invoking.
    :param predictor: SageMaker Predictor object
    :param rows: How to split the data
    :return np.ndarray: collected predictions as a NumPy array
    """
    split_array = np.array_split(data, int(data.shape[0] / float(rows) + 1))
    predictions = ""
    # Loop through each row in the file and use as a payload to the endpoint
    # https://sagemaker.readthedocs.io/en/stable/api/inference/predictors.html#sagemaker.predictor.Predictor.predict
    for array in split_array:
        predictions = ",".join([predictions, predictor.predict(array).decode("utf-8")])

    return np.fromstring(predictions[1:], sep=",")
