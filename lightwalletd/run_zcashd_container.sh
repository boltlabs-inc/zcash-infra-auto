#!/bin/bash

CUR_PATH=`PWD`

docker run -itd \
--name zcashd \
--mount source=mainnet-chain,destination=/home/zcash/.zcash \
--mount source=mainnet-params,destination=/home/zcash/.zcash-params \
-v $CUR_PATH/mainnet.daemon.conf:/home/zcash/.zcash/zcash.conf \
boltlabs/zcashd-lite:latest

docker exec -itd zcashd bash -c "zcashd --daemon"

#docker stop zcashd
#docker rm zcashd
