FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y \
    git \
    zip \
    unzip \
    wget \
    curl \
    python3-pip \
    python3-dev \
    build-essential \
    autoconf \
    automake \
    libtool \
    pkg-config \
    cmake \
    libffi-dev \
    libssl-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libncurses5-dev \
    libncursesw5-dev \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip && pip3 install buildozer cython


RUN sed -i '/def check_root/,/^[[:space:]]*$/c\    def check_root(self):\n        pass' \
    /usr/local/lib/python3.8/dist-packages/buildozer/__init__.py

WORKDIR /app