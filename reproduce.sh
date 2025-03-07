#!/usr/bin/env bash

# Set Up

curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
docker build -t exli .
docker run --rm exli /bin/bash -c '
    cd exli/python && \
    bash exli/python/prepare-conda-env.sh && \
    source /opt/conda/etc/profile.d/conda.sh && \
    conda activate exli && \
    echo "Python environment activated successfully" && \
    bash exli/python/reproduce.sh
'

