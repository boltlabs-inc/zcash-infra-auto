#!/bin/bash

export TAG=v2.0.6
docker build --build-arg TAG -t boltlabs/zcashd-lite:$TAG --memory-swap -1 .
