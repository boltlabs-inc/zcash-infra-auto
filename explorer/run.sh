#!/bin/bash

CUR_PATH=`pwd`

docker run -itd \
--name zcashd-explore \
-p 80:3001 \
--mount source=mainnet-chain,destination=/home/zcash/.zcash \
--mount source=mainnet-params,destination=/home/zcash/.zcash-params \
-v $CUR_PATH/mainnet.daemon.conf:/home/zcash/.zcash/zcash.conf \
boltlabs/zcashd-explore:v2.0.3 .
