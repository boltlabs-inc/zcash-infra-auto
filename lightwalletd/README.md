# Build Image

To build the docker image for the light wallet server, simply do the following:

	./build_image.sh

To run the docker conatiner:

	./run_zcash_lwd_testnet.sh

## Dependencies

You will need to install the `go` binaries for your platform to run tests against the light wallet server.

After installing `go` and adding to your `PATH`, install `grpcurl` from source as follows:

	go get github.com/fullstorydev/grpcurl
	go install github.com/fullstorydev/grpcurl/cmd/grpcurl

Or if on Mac OS from homebrew:

	brew install grpcurl

# Lightwalletd server tests

Here are basic commands exposed by the proxy server.

Get the latest block:

	grpcurl -plaintext localhost:9067 cash.z.wallet.sdk.rpc.CompactTxStreamer/GetLatestBlock
	
Get a specific block range that includes a sapling transaction:

	grpcurl -plaintext -d '{"start":{"height":366340}, "end":{"height":366345}}' localhost:9067 cash.z.wallet.sdk.rpc.CompactTxStreamer/GetBlockRange
	
Get raw transaction using the hash of tx at height 366344 (from previous command):

	grpcurl -plaintext -d '{"hash": "AxafLgWu7JeDsPU+46Ktncunce6BinzOkxHzgJx2P8c="}' localhost:9067 cash.z.wallet.sdk.rpc.CompactTxStreamer/GetTransaction

