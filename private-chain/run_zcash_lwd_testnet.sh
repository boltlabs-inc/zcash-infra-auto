#!/bin/bash

CUR_PATH=`pwd`

docker volume create private-chain

docker run -itd \
--name priv-zcashd \
--mount source=private-chain,destination=/home/zcash/.zcash \
--mount source=testnet-params,destination=/home/zcash/.zcash-params \
-v $CUR_PATH/zcash-master.daemon.conf:/home/zcash/.zcash/zcash.conf \
-v $CUR_PATH/zcash-node1.conf:/home/zcash/.zcash/zcash-node1.conf \
-v $CUR_PATH/zcash-node2.conf:/home/zcash/.zcash/zcash-node2.conf \
-v $CUR_PATH/supervisord.conf:/etc/supervisor/conf.d/supervisord.conf \
-p 9067:9067 \
boltlabs/zcashd-lwd:latest
