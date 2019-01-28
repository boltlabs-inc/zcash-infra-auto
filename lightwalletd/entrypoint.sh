#!/bin/bash

chown -R zcash /home/zcash/.zcash/zcash.conf

/usr/bin/supervisord
