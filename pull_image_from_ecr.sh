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
   IMAGE1=zcashd-lwd
   VERS1=latest
   IMAGE2=zcashd-lite
   VERS2=v2.0.4

   docker pull $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE1:$VERS1
   docker tag $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE1:$VERS1 boltlabs/$IMAGE1:$VERS1

   docker pull $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE2:$VERS2
   docker tag $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE2:$VERS2 boltlabs/$IMAGE2:$VERS2
fi

exit 0
