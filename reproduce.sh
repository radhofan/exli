#!/usr/bin/env bash

# Set Up

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Build Docker image
sudo docker build -t exli .

# Run Docker container
sudo docker run --rm exli /bin/bash -c '
    cd exli/python && \
    bash exli/python/prepare-conda-env.sh && \
    source /opt/conda/etc/profile.d/conda.sh && \
    conda activate exli && \
    echo "Python environment activated successfully" && \
    bash exli/python/reproduce.sh
'
