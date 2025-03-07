#!/usr/bin/env bash

# Set Up

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add user to the docker group
sudo usermod -aG docker $USER

# Log out and log back in (or use `su` to reload group permissions)
# Alternatively, use `sg` to switch to the docker group for the current session
sg docker -c "
    docker build -t exli . && \
    docker run --rm exli /bin/bash -c '
        cd exli/python && \
        chmod +x exli/python/prepare-conda-env.sh && \
        chmod +x exli/python/reproduce.sh && \
        bash exli/python/prepare-conda-env.sh && \
        source /opt/conda/etc/profile.d/conda.sh && \
        conda activate exli && \
        echo \"Python environment activated successfully\" && \
        bash exli/python/reproduce.sh
    '
"
