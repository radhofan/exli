#!/usr/bin/env bash

# Set Up

# Fix permissions for the build context
sudo chown -R $USER:$USER ./my_mounting_point
chmod -R 755 ./my_mounting_point

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add user to the docker group
sudo usermod -aG docker $USER
newgrp docker

# Build and run the Docker container
docker build -t exli .
docker run --rm exli /bin/bash -c '
    cd exli/python && \
    chmod +x exli/python/prepare-conda-env.sh && \
    chmod +x exli/python/reproduce.sh && \
    bash exli/python/prepare-conda-env.sh && \
    source /opt/conda/etc/profile.d/conda.sh && \
    conda activate exli && \
    echo "Python environment activated successfully" && \
    bash exli/python/reproduce.sh
'
