FROM postgres:13

ENV TMPDIR=/var/tmp

RUN mkdir -p /var/tmp && \
    chmod 1777 /var/tmp && \
    apt-get clean && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y wget build-essential postgresql-server-dev-13

RUN wget https://github.com/pgvector/pgvector/archive/v0.4.4.tar.gz && \
    tar -xzvf v0.4.4.tar.gz && \
    cd pgvector-0.4.4 && \
    make && \
    make install

COPY ./init.sql /docker-entrypoint-initdb.d/
