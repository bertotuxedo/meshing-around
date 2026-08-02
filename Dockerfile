# syntax=docker/dockerfile:1.7
FROM python:3.14-slim-bookworm AS wheels

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install --yes --no-install-recommends build-essential python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .
RUN python -m pip wheel --wheel-dir /wheels --requirement requirements.txt


FROM python:3.14-slim-bookworm AS runtime

ARG APP_UID=10001
ARG APP_GID=10001

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    TZ=UTC \
    MESHING_AROUND_CONFIG=/config/config.yaml

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid "$APP_GID" meshing \
    && useradd --uid "$APP_UID" --gid "$APP_GID" --create-home meshing

COPY --from=wheels /wheels /wheels
COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-index --find-links=/wheels --requirement /tmp/requirements.txt \
    && rm -rf /wheels /tmp/requirements.txt

WORKDIR /app
COPY --chown=meshing:meshing . /app

RUN mkdir -p /config /run/meshing-around /var/lib/meshing-around /var/log/meshing-around \
    && chown -R meshing:meshing /config /run/meshing-around /var/lib/meshing-around /var/log/meshing-around \
    && chmod +x /app/script/docker/entrypoint.sh \
    && chmod +x /app/script/docker/render_config.py /app/script/docker/healthcheck.py

USER meshing

VOLUME ["/var/lib/meshing-around", "/var/log/meshing-around"]
EXPOSE 8420

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "/app/script/docker/healthcheck.py"]

ENTRYPOINT ["/app/script/docker/entrypoint.sh"]
CMD ["python", "/app/mesh_bot.py"]
