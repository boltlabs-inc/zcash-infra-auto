#!/bin/bash

docker volume create mainnet-params

docker run -itd \
--name zcashd-params \
--mount source=mainnet-params,destination=/home/zcash/.zcash-params \
boltlabs/zcashd-lite:v2.0.4

docker exec -it zcashd-params bash -c "fetch-params.sh"

# Verify that fetch-params a success
docker exec -it zcashd-params bash -c "ls /home/zcash/.zcash-params"

docker stop zcashd-params
docker rm zcashd-params
