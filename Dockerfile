FROM debian:bullseye-slim

LABEL maintainer="stanislav.v.v@gmail.com"
LABEL description="fb2 opds service"

ARG DEBIAN_FRONTEND=noninteractive

RUN set -ex && \
    apt-get update && \
    apt-get install -y --no-install-recommends python3-lxml python3-bs4 python3-xmltodict python3-flask gunicorn && \
    apt-get clean

ADD . /fb2_srv/

RUN set -ex && \
    rm -rf /fb2_srv/data && \
    mkdir -p /fb2_srv/data && \
    mv -f /fb2_srv/app/config.py.example /fb2_srv/app/config.py

COPY docker_entrypoint.sh /usr/local/bin/entrypoint

ENTRYPOINT ["entrypoint"]
