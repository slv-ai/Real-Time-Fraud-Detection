variable "aws_region" {
  description = "AWS region to create resources"
  default     = "eu-east-1"
}

variable "project_id" {
  description = "project_id"
  default = "mlops-project"
}

variable "source_stream_name" {
  description = ""
}

variable "output_stream_name" {
  description = ""
}