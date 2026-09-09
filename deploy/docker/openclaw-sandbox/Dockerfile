FROM debian:bookworm-slim

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        coreutils \
        curl \
        findutils \
        git \
        grep \
        python3 \
        python3-venv \
        sed \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
CMD ["bash"]
