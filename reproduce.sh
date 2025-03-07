#!/usr/bin/env bash

# Set Up

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Build Docker image
sudo docker build -t exli ./exli

# Run Docker container
sudo docker run --rm \
    -v $(pwd)/exli:/exli \
    exli /bin/bash -c '
        cd /exli/python && \
        bash prepare-conda-env.sh && \
        source /opt/conda/etc/profile.d/conda.sh && \
        conda activate exli && \
        echo "Python environment activated successfully" && \
        bash reproduce.sh
    '
