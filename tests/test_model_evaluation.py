import botocore
import pytest
from botocore.stub import Stubber, ANY

from example_responses import (
    example_sqs_event,
    example_describe_training_job_statuses,
    example_parameters_response,
)
from model_evaluation import (
    lambda_handler,
    wait_endpoint_status_in_service,
    get_parameter_store_value,
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


def test_get_parameter_store_value():
    ssm_client = botocore.session.get_session().create_client("ssm")
    stubber = Stubber(ssm_client)
    expected_params = {"Name": ANY, "WithDecryption": True}
    stubber.add_response(
        "get_parameter", example_parameters_response(), expected_params
    )

    with stubber:
        assert get_parameter_store_value("unit-test", ssm_client) == "string"
