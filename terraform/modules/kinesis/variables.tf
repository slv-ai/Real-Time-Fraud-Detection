variable "stream_name" {
    type = string
    description = "kinesis stream name"
}

variable "shard_count" {
    type = number
    description = "kinesis stream shard count "
}

variable "retention_period" {
    type = number
    description = "kinesis stream retention_period"
}

variable "shard_level_metrics"{
    type = list(string)
    description = "shard_level_metrics"
    default = [
        "IncomingBytes",
        "OutgoingBytes",
        "OutgoingRecords",
        "ReadProvisionedThroughputExceeded",
        "WriteProvisionedThroughputExceeded",
        "IncomingRecords",
        "IteratorAgeMilliseconds",
    ]
}

variable "tags" {
    description = "Tags for kinesis stream"
    default = "fraud-detection"
}