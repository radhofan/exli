#!/usr/bin/env bash

# Set Up

docker build -t exli .
docker run --rm exli /bin/bash -c '
    cd exli/python && \
    bash exli/python/prepare-conda-env.sh && \
    source /opt/conda/etc/profile.d/conda.sh && \
    conda activate exli && \
    echo "Python environment activated successfully" && \
    bash exli/python/reproduce.sh
'

