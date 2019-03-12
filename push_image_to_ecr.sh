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
   IMAGE2=zcashd-lite
   VERS2=v2.0.3

   #docker build -t $IMAGE1 .
   docker tag boltlabs/$IMAGE1:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE1:latest
   docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE1:latest

   #docker build -t $IMAGE2 .
   docker tag boltlabs/$IMAGE2:$VERS2 $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE2:$VERS2
   docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE2:$VERS2
fi

exit 0
