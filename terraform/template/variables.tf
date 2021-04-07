variable "application_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "region" {
  type = string
}

variable "docker_image_tag" {
  type = string
  default = "latest"
}

variable "function_handler" {
  type = string
}

variable "tags" {
  type = map(string)
}

variable "ferje_pathtaker_source_queue_name" {
  type = string
  description = "Name of the SQS queue, where our Lambda should enqueue signals"
}