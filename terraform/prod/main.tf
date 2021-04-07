terraform {
  required_version = "0.14.3"

  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "3.27.0"
    }
  }

  backend "s3" {
    bucket = "lokalvert-terraform-state"
    key    = "ferje-radar-processor/prod.terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  allowed_account_ids = ["314397620259"]
  # Configuration options
  region = "us-east-1"
}

data "aws_region" "current" {}

locals {
  application_name = "ferje-radar-processor"
  environment = "prod"

  last_commit_sha = trimspace(file("../../.git/${trimspace(trimprefix(file("../../.git/HEAD"), "ref:"))}"))

  qualified_name = "${local.application_name}-${local.environment}"
  tags = {
    "managedBy" = "terraform"
    "application" = local.application_name
    "environment" = local.environment
    "ntnuCourse" = "ttk4851"
  }
}

module "ferjeradarprocessor" {
  source = "../template"
  application_name = local.application_name
  environment = local.environment
  function_handler = "main.handler"
  ferje_pathtaker_source_queue_name = "ferje-ais-importer-prod-pathtaker-source"
  docker_image_tag = local.last_commit_sha
  tags = local.tags

  region = data.aws_region.current.name
}
