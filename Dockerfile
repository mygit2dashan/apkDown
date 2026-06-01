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
    sudo \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip && pip3 install buildozer cython

# 创建非 root 用户（无密码 sudo，但实际构建不需要 sudo）
RUN useradd -m -s /bin/bash builder && echo "builder ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /app
RUN chown -R builder:builder /app

USER builder
