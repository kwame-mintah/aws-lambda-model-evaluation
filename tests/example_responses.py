from datetime import datetime


def example_sqs_event():
    """
    Example event received when a new endpoint has been created.
    :return:
    """
    return {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
                "body": '{"endpointName": "example", "testDataS3BucketName": '
                '"unit-test", "testDataS3Key" : "automl/2024-03-18/training/testing/test_23_55_44.csv"}',
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


def example_describe_training_job_statuses(endpoint_status: str = "InService"):
    """
    Example response when describing a training job, with the option to
    change the EndpointStatus returned in the json.
    :param endpoint_status:
    :return:
    """
    return {
        "EndpointName": "endpoint-name",
        "EndpointArn": "arn:aws:sagemaker:eu-west-2::endpoint/endpoint-name",
        "EndpointConfigName": "string",
        "ProductionVariants": [
            {
                "VariantName": "string",
                "DeployedImages": [
                    {
                        "SpecifiedImage": "string",
                        "ResolvedImage": "string",
                        "ResolutionTime": datetime(2015, 1, 1),
                    },
                ],
                "CurrentWeight": 0.1,
                "DesiredWeight": 0.1,
                "CurrentInstanceCount": 123,
                "DesiredInstanceCount": 123,
                "VariantStatus": [
                    {
                        "Status": "Creating",
                        "StatusMessage": "string",
                        "StartTime": datetime(2015, 1, 1),
                    },
                ],
                "CurrentServerlessConfig": {
                    "MemorySizeInMB": 1024,
                    "MaxConcurrency": 123,
                    "ProvisionedConcurrency": 123,
                },
                "DesiredServerlessConfig": {
                    "MemorySizeInMB": 1024,
                    "MaxConcurrency": 123,
                    "ProvisionedConcurrency": 123,
                },
                "ManagedInstanceScaling": {
                    "Status": "ENABLED",
                    "MinInstanceCount": 123,
                    "MaxInstanceCount": 123,
                },
                "RoutingConfig": {"RoutingStrategy": "LEAST_OUTSTANDING_REQUESTS"},
            },
        ],
        "DataCaptureConfig": {
            "EnableCapture": True,
            "CaptureStatus": "Started",
            "CurrentSamplingPercentage": 123,
            "DestinationS3Uri": "string",
            "KmsKeyId": "string",
        },
        "EndpointStatus": endpoint_status,
        "FailureReason": "string",
        "CreationTime": datetime(2015, 1, 1),
        "LastModifiedTime": datetime(2015, 1, 1),
        "LastDeploymentConfig": {
            "BlueGreenUpdatePolicy": {
                "TrafficRoutingConfiguration": {
                    "Type": "ALL_AT_ONCE",
                    "WaitIntervalInSeconds": 123,
                    "CanarySize": {
                        "Type": "INSTANCE_COUNT",
                        "Value": 123,
                    },
                    "LinearStepSize": {
                        "Type": "INSTANCE_COUNT",
                        "Value": 123,
                    },
                },
                "TerminationWaitInSeconds": 123,
                "MaximumExecutionTimeoutInSeconds": 600,
            },
            "RollingUpdatePolicy": {
                "MaximumBatchSize": {
                    "Type": "INSTANCE_COUNT",
                    "Value": 123,
                },
                "WaitIntervalInSeconds": 123,
                "MaximumExecutionTimeoutInSeconds": 600,
                "RollbackMaximumBatchSize": {
                    "Type": "INSTANCE_COUNT",
                    "Value": 123,
                },
            },
            "AutoRollbackConfiguration": {
                "Alarms": [
                    {"AlarmName": "string"},
                ]
            },
        },
        "AsyncInferenceConfig": {
            "ClientConfig": {"MaxConcurrentInvocationsPerInstance": 123},
            "OutputConfig": {
                "KmsKeyId": "string",
                "S3OutputPath": "string",
                "NotificationConfig": {
                    "SuccessTopic": "string",
                    "ErrorTopic": "string",
                    "IncludeInferenceResponseIn": [
                        "SUCCESS_NOTIFICATION_TOPIC",
                    ],
                },
                "S3FailurePath": "string",
            },
        },
        "PendingDeploymentSummary": {
            "EndpointConfigName": "string",
            "ProductionVariants": [
                {
                    "VariantName": "string",
                    "DeployedImages": [
                        {
                            "SpecifiedImage": "string",
                            "ResolvedImage": "string",
                            "ResolutionTime": datetime(2015, 1, 1),
                        },
                    ],
                    "CurrentWeight": 0.1,
                    "DesiredWeight": 0.1,
                    "CurrentInstanceCount": 123,
                    "DesiredInstanceCount": 123,
                    "InstanceType": "ml.t2.medium",
                    "AcceleratorType": "ml.eia1.medium",
                    "VariantStatus": [
                        {
                            "Status": "Creating",
                            "StatusMessage": "string",
                            "StartTime": datetime(2015, 1, 1),
                        },
                    ],
                    "CurrentServerlessConfig": {
                        "MemorySizeInMB": 1024,
                        "MaxConcurrency": 123,
                        "ProvisionedConcurrency": 123,
                    },
                    "DesiredServerlessConfig": {
                        "MemorySizeInMB": 1024,
                        "MaxConcurrency": 123,
                        "ProvisionedConcurrency": 123,
                    },
                    "ManagedInstanceScaling": {
                        "Status": "ENABLED",
                        "MinInstanceCount": 123,
                        "MaxInstanceCount": 123,
                    },
                    "RoutingConfig": {"RoutingStrategy": "LEAST_OUTSTANDING_REQUESTS"},
                },
            ],
            "StartTime": datetime(2015, 1, 1),
            "ShadowProductionVariants": [
                {
                    "VariantName": "string",
                    "DeployedImages": [
                        {
                            "SpecifiedImage": "string",
                            "ResolvedImage": "string",
                            "ResolutionTime": datetime(2015, 1, 1),
                        },
                    ],
                    "CurrentWeight": 0.1,
                    "DesiredWeight": 0.1,
                    "CurrentInstanceCount": 123,
                    "DesiredInstanceCount": 123,
                    "InstanceType": "ml.t2.medium",
                    "AcceleratorType": "ml.eia1.medium",
                    "VariantStatus": [
                        {
                            "Status": "Creating",
                            "StatusMessage": "string",
                            "StartTime": datetime(2015, 1, 1),
                        },
                    ],
                    "CurrentServerlessConfig": {
                        "MemorySizeInMB": 1024,
                        "MaxConcurrency": 123,
                        "ProvisionedConcurrency": 123,
                    },
                    "DesiredServerlessConfig": {
                        "MemorySizeInMB": 1024,
                        "MaxConcurrency": 123,
                        "ProvisionedConcurrency": 123,
                    },
                    "ManagedInstanceScaling": {
                        "Status": "ENABLED",
                        "MinInstanceCount": 123,
                        "MaxInstanceCount": 123,
                    },
                    "RoutingConfig": {"RoutingStrategy": "LEAST_OUTSTANDING_REQUESTS"},
                },
            ],
        },
        "ExplainerConfig": {
            "ClarifyExplainerConfig": {
                "EnableExplanations": "string",
                "InferenceConfig": {
                    "FeaturesAttribute": "string",
                    "ContentTemplate": "string",
                    "MaxRecordCount": 123,
                    "MaxPayloadInMB": 123,
                    "ProbabilityIndex": 123,
                    "LabelIndex": 123,
                    "ProbabilityAttribute": "string",
                    "LabelAttribute": "string",
                    "LabelHeaders": [
                        "string",
                    ],
                    "FeatureHeaders": [
                        "string",
                    ],
                    "FeatureTypes": [
                        "numerical",
                    ],
                },
                "ShapConfig": {
                    "ShapBaselineConfig": {
                        "MimeType": "string",
                        "ShapBaseline": "string",
                        "ShapBaselineUri": "string",
                    },
                    "NumberOfSamples": 123,
                    "UseLogit": True,
                    "Seed": 123,
                    "TextConfig": {
                        "Language": "xx",
                        "Granularity": "token",
                    },
                },
            }
        },
        "ShadowProductionVariants": [
            {
                "VariantName": "string",
                "DeployedImages": [
                    {
                        "SpecifiedImage": "string",
                        "ResolvedImage": "string",
                        "ResolutionTime": datetime(2015, 1, 1),
                    },
                ],
                "CurrentWeight": 0.1,
                "DesiredWeight": 0.1,
                "CurrentInstanceCount": 123,
                "DesiredInstanceCount": 123,
                "VariantStatus": [
                    {
                        "Status": "Creating",
                        "StatusMessage": "string",
                        "StartTime": datetime(2015, 1, 1),
                    },
                ],
                "CurrentServerlessConfig": {
                    "MemorySizeInMB": 1024,
                    "MaxConcurrency": 123,
                    "ProvisionedConcurrency": 123,
                },
                "DesiredServerlessConfig": {
                    "MemorySizeInMB": 1024,
                    "MaxConcurrency": 123,
                    "ProvisionedConcurrency": 123,
                },
                "ManagedInstanceScaling": {
                    "Status": "ENABLED",
                    "MinInstanceCount": 123,
                    "MaxInstanceCount": 123,
                },
                "RoutingConfig": {"RoutingStrategy": "LEAST_OUTSTANDING_REQUESTS"},
            },
        ],
    }


def example_parameters_response():
    """
    Example response when retrieving parameter store value.
    :return:
    """
    return {
        "Parameter": {
            "Name": "string",
            "Type": "String",
            "Value": "string",
            "Version": 123,
            "Selector": "string",
            "SourceResult": "string",
            "LastModifiedDate": datetime(2015, 1, 1),
            "ARN": "string",
            "DataType": "string",
        }
    }
