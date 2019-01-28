#!/bin/bash

CUR_PATH=`pwd`

docker run -itd \
--name zcashd-lwd \
--mount source=mainnet-chain,destination=/home/zcash/.zcash \
--mount source=mainnet-params,destination=/home/zcash/.zcash-params \
-v $CUR_PATH/mainnet.daemon.conf:/home/zcash/.zcash/zcash.conf \
-p 9067:9067 \
boltlabs/zcashd-lwd:latest
