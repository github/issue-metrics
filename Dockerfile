FROM       python:3.11.4-slim-bookworm AS builder
MAINTAINER nerds.run
ENV        REFRESHED_AT 2023/08/11

ADD . /tmp
WORKDIR /tmp

# install python requirements
RUN set -ex && \
    build_deps='curl gpg lsb-release' && \
    apt update && \
    apt install -y $build_deps --no-install-recommends && \
    curl -q 'https://proget.makedeb.org/debian-feeds/prebuilt-mpr.pub' | gpg --dearmor | tee /usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg 1> /dev/null && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg] https://proget.makedeb.org prebuilt-mpr $(lsb_release -cs)" | tee /etc/apt/sources.list.d/prebuilt-mpr.list && \
    build_deps="${build_deps}" && \
    apt update && \
    apt install -y just --no-install-recommends && \
    pip install --upgrade pip poetry --no-cache && \
    just dev install && \
    apt purge -y --auto-remove $build_deps && \
    rm -rf /var/lib/apt/lists/*



VOLUME /tmp

CMD ["just", "-l"]

FROM builder

WORKDIR /action/workspace

CMD ["/action/workspace/issue_metrics.py"]
ENTRYPOINT ["python3", "-u"]












