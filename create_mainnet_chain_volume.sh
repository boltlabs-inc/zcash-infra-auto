#!/bin/bash

docker volume create mainnet-chain

CUR_PATH=`PWD`

docker run -itd \
--name zcashd-chain \
--mount source=mainnet-chain,destination=/home/zcash/.zcash \
--mount source=mainnet-params,destination=/home/zcash/.zcash-params \
-v $CUR_PATH/mainnet.daemon.conf:/home/zcash/.zcash/zcash.conf \
boltlabs/zcashd-lite:v2.0.2

docker exec -itd zcashd-chain bash -c "zcashd"

#docker stop zcashd-chain
#docker rm zcashd-chain
