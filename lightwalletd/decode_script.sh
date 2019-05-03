#!/bin/bash

docker exec -it zcashd-lwd bash -c "sudo -u zcash zcash-cli decodescript \"$@\""
