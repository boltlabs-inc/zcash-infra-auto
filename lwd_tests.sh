#!/bin/bash

EC2_INS=$1
if [[ $EC2_INS = "" ]]; then
   echo "$0: Missing hostname for EC2 instance"
   exit 1
fi

echo "List the methods available..."
grpcurl -plaintext $EC2_INS:9067 list

echo "Confirm we can retrieve the latest block..."
grpcurl -plaintext $EC2_INS:9067 cash.z.wallet.sdk.rpc.CompactTxStreamer/GetLatestBlock

echo "Check that Sapling is activated..."
grpcurl -plaintext -d '{"height": 280000}' $EC2_INS:9067 cash.z.wallet.sdk.rpc.CompactTxStreamer/GetBlock

