#!/bin/bash

CONTAINER=priv-zcashd
ARG=${@:1}
CMD="sudo -u zcash zcash-cli ${ARG}"
echo $CMD
docker exec -it $CONTAINER bash -c "$CMD"
