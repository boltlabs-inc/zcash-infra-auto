#!/bin/bash

export TAG=latest
docker build --build-arg TAG -t boltlabs/zcashd-lite:$TAG --memory-swap -1 .
