import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Tuple

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

# The environment the lambda is currently deployed in
SERVERLESS_ENVIRONMENT = os.environ.get("SERVERLESS_ENVIRONMENT")

# Configure logging
logger = logging.getLogger("model-evaluation")
logger.setLevel(logging.INFO)

# The output bucket ssm parameter store name
ssm_model_evaluation_output_bucket_name = (
    "mlops-{region}-{environment}-model-monitoring".format(
        region=aws_region, environment=SERVERLESS_ENVIRONMENT
    )
)


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
        data=data.drop(labels=["y_no", "y_yes"], axis=1).to_numpy(), predictor=predictor
    )

    # Upload csv to output bucket for training
    model_evaluation_output_bucket_name = get_parameter_store_value(
        name=ssm_model_evaluation_output_bucket_name
    )

    # Create confusion matrix to see how well the model predicted vs. actuals.
    prediction_confusion_matrix = pd.crosstab(
        index=data["y_yes"],
        columns=np.round(predictions),
        rownames=["actuals"],
        colnames=["predictions"],
    )

    # predictions   0.0  1.0
    # actuals
    # 0.0          3583   53
    # 1.0           382  101

    calculate_confusion_matrix_metrics(
        true_positive=prediction_confusion_matrix[0][0],
        true_negative=prediction_confusion_matrix[1][1],
        false_positive=prediction_confusion_matrix[1][0],
        false_negative=prediction_confusion_matrix[0][1],
    )

    # Then save to S3 bucket to be reviewed later as markdown.
    prediction_confusion_matrix.to_markdown(
        buf="s3://{bucket_name}/{today}/predictions/{endpoint_name}/PREDICTIONS.md".format(
            bucket_name=model_evaluation_output_bucket_name,
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


def perform_predictions(
    data: np.ndarray, predictor: Predictor, rows: int = 500
) -> np.ndarray:
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


def get_parameter_store_value(
    name: str, client: Any = boto3.client(service_name="ssm", region_name=aws_region)
) -> str:
    """
    Get a parameter store value from AWS.

    :param name: The name or Amazon Resource Name (ARN) of the parameter that you want to query
    :param client: boto3 client configured to use ssm
    :return: value
    """
    logger.info("Retrieving %s from parameter store", name)
    return client.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]


def calculate_confusion_matrix_metrics(
    true_positive: int, true_negative: int, false_positive: int, false_negative: int
) -> tuple[float, float, float, float, float]:
    """
    Calculate quantitative evaluation metrics against machine learning model.

    :param true_positive: positive class being classified correctly.
    :param true_negative: negative class being classified correctly.
    :param false_positive: negative class but being classified wrongly as belonging to the positive class.
    :param false_negative: positive class but being classified wrongly as belonging to the negative class.
    :return: calculated accuracy, precision, recall, f1_score, specificity
    """
    accuracy = (true_negative + true_negative) / (
        true_positive + false_positive + true_negative + false_negative
    )
    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / (true_positive + false_negative)
    f1_score = 2 * (precision * recall) / (precision + recall)
    specificity = true_negative / (false_positive + true_negative)

    logger.info(
        "Model confusion metrics scores, accuracy: %s, precision: %s, recall: %s, F1 score: %s and "
        "specificity: %s",
        accuracy,
        precision,
        recall,
        f1_score,
        specificity,
    )
    return accuracy, precision, recall, f1_score, specificity
