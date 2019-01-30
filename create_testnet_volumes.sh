#!/bin/bash

docker volume create testnet-chain
docker volume create testnet-params

CUR_PATH=`pwd`

docker run -itd \
--name zcashd-testnet \
--mount source=testnet-chain,destination=/home/zcash/.zcash \
--mount source=testnet-params,destination=/home/zcash/.zcash-params \
-v $CUR_PATH/testnet.daemon.conf:/home/zcash/.zcash/zcash.conf \
boltlabs/zcashd-lite:v2.0.2

docker exec -it zcashd-testnet bash -c "fetch-params.sh"

# Verify that fetch-params a success
docker exec -it zcashd-testnet bash -c "ls /home/zcash/.zcash-params"

docker exec -itd zcashd-testnet bash -c "zcashd"

