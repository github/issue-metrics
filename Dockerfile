#checkov:skip=CKV_DOCKER_2
#checkov:skip=CKV_DOCKER_3
FROM python:3.13-slim@sha256:4c2cf9917bd1cbacc5e9b07320025bdb7cdf2df7b0ceaccb55e9dd7e30987419
LABEL com.github.actions.name="issue-metrics" \
    com.github.actions.description="Gather metrics on issues/prs/discussions such as time to first response, count of issues opened, closed, etc." \
    com.github.actions.icon="check-square" \
    com.github.actions.color="white" \
    maintainer="@zkoppert" \
    org.opencontainers.image.url="https://github.com/github/issue-metrics" \
    org.opencontainers.image.source="https://github.com/github/issue-metrics" \
    org.opencontainers.image.documentation="https://github.com/github/issue-metrics" \
    org.opencontainers.image.vendor="GitHub" \
    org.opencontainers.image.description="Gather metrics on issues/prs/discussions such as time to first response, count of issues opened, closed, etc."

WORKDIR /action/workspace
COPY requirements.txt *.py /action/workspace/

RUN python3 -m pip install --no-cache-dir -r requirements.txt \
    && apt-get -y update \
    && apt-get -y install --no-install-recommends git=1:2.39.5-0+deb12u2 \
    && rm -rf /var/lib/apt/lists/*

CMD ["/action/workspace/issue_metrics.py"]
ENTRYPOINT ["python3", "-u"]
