#!/bin/bash

echo "Confirm we can retrieve the latest block..."
grpcurl -plaintext localhost:9067 cash.z.wallet.sdk.rpc.CompactTxStreamer/GetLatestBlock

echo "Check that Sapling is activated..."
grpcurl -plaintext -d '{"height": 280000}' localhost:9067 cash.z.wallet.sdk.rpc.CompactTxStreamer/GetBlock

