#!/bin/bash

# first run 'aws configure' (if you have not done so already)

LOGIN_CMD=`aws ecr get-login --region us-east-1 --no-include-email`

echo "Login to Amazon ECR"
$LOGIN_CMD
STATUS=$?

echo "> $LOGIN_CMD"

if [ "$STATUS" -eq "0" ]; then
   AWS_ACCOUNT_ID=183812568438 # bolt labs
   AWS_REGION=us-east-1
   IMAGE=zcashd-lwd

   #docker build -t $IMAGE .
   docker tag boltlabs/$IMAGE:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE:latest
   docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE:latest
fi

exit 0
