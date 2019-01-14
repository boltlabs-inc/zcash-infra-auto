FROM debian:jessie AS builder

ENV ZCASH_URL=https://github.com/zcash/zcash.git \
    ZCASH_CONF=/home/zcash/.zcash/zcash.conf

ARG TAG

RUN apt-get update

RUN apt-get -qqy install --no-install-recommends build-essential \
    automake ncurses-dev libcurl4-openssl-dev libssl-dev libgtest-dev \
    make autoconf automake libtool git apt-utils pkg-config libc6-dev \
    libcurl3-dev libudev-dev m4 g++-multilib unzip git python zlib1g-dev \
    wget ca-certificates pwgen bsdmainutils curl

WORKDIR /src
RUN git clone ${ZCASH_URL}

WORKDIR /src/zcash
RUN git checkout $TAG
RUN ./zcutil/build.sh -j$(nproc)

WORKDIR /src/zcash/src
RUN /usr/bin/install -c zcash-tx zcashd zcash-cli zcash-gtest ../zcutil/fetch-params.sh -t /usr/bin/

FROM debian:jessie

ENV ZCASH_CONF=/home/zcash/.zcash/zcash.conf

RUN apt-get update

RUN apt-get install -y build-essential git wget libzmq3-dev gnupg2 libgomp1 curl 
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y nodejs

RUN apt-get clean all -y


COPY --from=builder /usr/bin/zcash-cli /usr/bin/zcashd /usr/bin/fetch-params.sh /usr/bin/

RUN adduser --uid 1000 --group --system zcash && \
    mkdir -p /home/zcash/.npm-global/ && \
    mkdir -p /home/zcash/.zcash/ && \
    mkdir -p /home/zcash/.zcash-params/ && \
    chown -R zcash /home/zcash && \
    echo "Success"

ENV PATH=/home/zcash/.npm-global/bin:$PATH
ENV NPM_CONFIG_PREFIX=/home/zcash/.npm-global

USER zcash
RUN npm install -g npm@latest
RUN npm -g install zcash-hackworks/bitcore-node-zcash
RUN echo "rpcuser=zcash" > ${ZCASH_CONF} && \
        echo "rpcpassword=`head /dev/urandom | tr -dc A-Za-z0-9 | head -c 13 ; echo ''`" >> ${ZCASH_CONF} && \
        echo "addnode=mainnet.z.cash" >> ${ZCASH_CONF} && \
        echo "Success"

WORKDIR /home/zcash/
RUN bitcore-node create zc
COPY --chown=zcash:zcash ./bitcore-node.json /home/zcash/zc/

WORKDIR /home/zcash/zc/
RUN bitcore-node install zcash-hackworks/insight-api-zcash zcash-hackworks/insight-ui-zcash

#VOLUME ["/home/zcash/.zcash"]
ENTRYPOINT ["/home/zcash/zc/node_modules/bitcore-node-zcash/bin/bitcore-node", "start"]
