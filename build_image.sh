#!/bin/bash

export TAG=v2.0.4
docker build --build-arg TAG -t boltlabs/zcashd-lite:$TAG --memory-swap -1 .
