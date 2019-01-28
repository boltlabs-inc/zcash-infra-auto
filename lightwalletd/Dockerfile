FROM golang:1.11 AS builder

ENV ZCASH_URL=https://github.com/boltlabs-inc/zcash.git \
    ZCASH_CONF=/home/zcash/.zcash/zcash.conf

ARG TAG

RUN apt-get update

RUN apt-get -qqy install --no-install-recommends build-essential \
    automake ncurses-dev libcurl4-openssl-dev libssl-dev libgtest-dev \
    make autoconf automake libtool git apt-utils pkg-config libc6-dev \
    libcurl3-dev libudev-dev m4 g++-multilib unzip git python zlib1g-dev \
    wget ca-certificates pwgen bsdmainutils curl libzmq3-dev

WORKDIR /src
RUN git clone ${ZCASH_URL}

WORKDIR /src/zcash
RUN git checkout
RUN ./zcutil/build.sh -j$(nproc)

WORKDIR /src/zcash/src
RUN /usr/bin/install -c zcash-tx zcashd zcash-cli zcash-gtest ../zcutil/fetch-params.sh -t /usr/bin/

FROM golang:1.11

ENV ZCASH_CONF=/home/zcash/.zcash/zcash.conf \
    ZCASH_LIGHT=https://github.com/zcash-hackworks/lightwalletd.git

ENV GOPATH=$HOME/go

RUN apt-get update

RUN apt-get install -y sudo libgomp1 wget curl libzmq3-dev git supervisor

RUN apt-get clean all -y


COPY --from=builder /usr/bin/zcash-cli /usr/bin/zcashd /usr/bin/fetch-params.sh /usr/bin/

RUN adduser --uid 1000 --system zcash && \
    mkdir -p /home/zcash/.zcash/ && \
    mkdir -p /home/zcash/.zcash-params/ && \
    chown -R zcash /home/zcash && \
    echo "Success"

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY entrypoint.sh /usr/bin/

#USER zcash
RUN echo "rpcuser=zcash" > ${ZCASH_CONF} && \
        echo "rpcpassword=`head /dev/urandom | tr -dc A-Za-z0-9 | head -c 13 ; echo ''`" >> ${ZCASH_CONF} && \
        echo "addnode=mainnet.z.cash" >> ${ZCASH_CONF} && \
        echo "zmqpubcheckedblock=tcp://127.0.0.1:28332" >> ${ZCASH_CONF} && \
        echo "Success"

WORKDIR /home/zcash

RUN git clone ${ZCASH_LIGHT}

WORKDIR /home/zcash/lightwalletd

RUN go run cmd/ingest/main.go || echo $?

VOLUME ["/home/zcash/.zcash"]

CMD ["/usr/bin/entrypoint.sh"]
