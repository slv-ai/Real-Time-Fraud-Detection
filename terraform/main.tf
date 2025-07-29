terraform {
    required_version = ">= 1.0"
    backend "s3" {
        bucket = "tf-state-fraud-detection"
        key = "mlops-project-stg.tfstate"
        region = "us-east-1
        encrypt = true
    }
}