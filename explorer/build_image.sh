#!/bin/bash

#export TAG=v1.1.1
export TAG=v2.0.2
docker build --build-arg TAG -t boltlabs/zcashd-explore:$TAG --memory-swap -1 .
