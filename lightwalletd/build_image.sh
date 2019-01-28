#!/bin/bash

export TAG=latest
docker build --build-arg TAG -t boltlabs/zcashd-lwd:$TAG --memory-swap -1 .
