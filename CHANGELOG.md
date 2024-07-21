## 0.5.0 (2024-07-21)

### Feat

- **perform_predictions**: perform batch predictions against model

## 0.4.2 (2024-07-20)

### Refactor

- **csv_rows**: properly split rows to be used for prediction

## 0.4.1 (2024-05-12)

### Refactor

- **s3_client**: include arg name of `service_name`

## 0.4.0 (2024-05-12)

### Feat

- **lambda_handler**: include checking of endpoint status
- **wait_endpoint_status_in_service**: check endpoint is inservice before invoking requests

### Refactor

- **models**: add examples for modelevalmessage

## 0.3.0 (2024-04-07)

### Feat

- **pre-commit-config**: update black and commitizen versions

## 0.2.0 (2024-03-26)

### Feat

- **model_evaluation**: retrieve test data from s3 bucket for predictions

## 0.1.0 (2024-03-25)

### Feat

- **model_evaluation**: initial implementation to invoke endpoint
- **pre-commit-config**: update hooks used within project
