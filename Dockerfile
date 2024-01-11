FROM mcr.microsoft.com/vscode/devcontainers/python:0-3.11

ENV PYTHONUNBUFFERED 1

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN \
    pipx uninstall black \
    && pipx uninstall pydocstyle \
    && pipx uninstall pycodestyle \
    && pipx uninstall mypy \
    && pipx uninstall pylint

RUN \
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    # Additional library needed by some tests and accordingly by VScode Tests Discovery
    bluez \
    libudev-dev \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev \
    libpcap-dev \
    libturbojpeg0 \
    libyaml-dev \
    libxml2 \
    git \
    cmake \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspaces

RUN pip3 install --upgrade pip

# Set the default shell to bash instead of sh
ENV SHELL /bin/bash
