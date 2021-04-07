#!/bin/bash

set -e

export CI_COMMIT_HASH=$(git rev-parse --verify HEAD)

echo ""
echo "⏳ Retrieving credentials for ECR..."
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 314397620259.dkr.ecr.us-east-1.amazonaws.com

echo ""
echo "⏳ Building docker image and pushing to ECR..."
echo ""
docker build -t 314397620259.dkr.ecr.us-east-1.amazonaws.com/ferje-ais-importer-prod:$CI_COMMIT_HASH .
docker push 314397620259.dkr.ecr.us-east-1.amazonaws.com/ferje-ais-importer-prod:$CI_COMMIT_HASH

echo ""
echo "⏳ Deploying docker image to lambda..."
echo ""
cd terraform/prod
terraform apply -auto-approve

cd ../../

echo ""
echo "✅ Deployment completed!"
echo ""