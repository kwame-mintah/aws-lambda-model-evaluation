import botocore
import pytest
from botocore.exceptions import IncompleteReadError
from botocore.stub import Stubber, ANY

from example_responses import (
    example_sqs_event,
    example_get_object,
    example_describe_training_job_statuses,
)
from model_evaluation import (
    lambda_handler,
    retrieve_object_from_bucket,
    wait_endpoint_status_in_service,
)


@pytest.mark.skip(reason="skipping until implementation flow is completed")
def test_lambda_handler():
    """
    Example unit test for lambda function created, passing in
    the expected event to trigger it.
    """
    event = example_sqs_event()
    result = lambda_handler(event, None)
    assert result["Records"][0]["messageId"] == "059f36b4-87a3-44ab-83d2-661975830a7d"


@pytest.mark.xfail(
    reason="chunking during read returning 0 bytes", raises=IncompleteReadError
)
def test_retrieve_object_from_bucket():
    s3_client = botocore.session.get_session().create_client("s3")
    stubber = Stubber(s3_client)
    expected_params = {"Bucket": ANY, "Key": ANY}
    stubber.add_response("get_object", example_get_object(), expected_params)

    with stubber:
        result = retrieve_object_from_bucket(
            bucket_name="unit-test", key="example_payload.csv", client=s3_client
        )
        assert result == ""  # should return content of `example_payload.csv`


def test_wait_endpoint_status_in_service():
    sagemaker_client = botocore.session.get_session().create_client("sagemaker")
    stubber = Stubber(sagemaker_client)
    expected_params = {"EndpointName": ANY}
    # First response should return 'Creating' to enter while loop.
    stubber.add_response(
        "describe_endpoint",
        example_describe_training_job_statuses(endpoint_status="Creating"),
        expected_params,
    )
    # Second response should return 'InService' to exit while loop.
    stubber.add_response(
        "describe_endpoint",
        example_describe_training_job_statuses(endpoint_status="InService"),
        expected_params,
    )

    with stubber:
        assert (
            wait_endpoint_status_in_service(
                endpoint_name="endpoint-name", boto_client=sagemaker_client
            )
            == "InService"
        )
