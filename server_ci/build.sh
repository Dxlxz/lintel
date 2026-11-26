#!/bin/bash


docker buildx build \
    --platform linux/amd64 \
    -f "./server_ci/Dockerfile" \
    -t "guardrails:server-ci" \
    --build-arg LINTEL_TOKEN="$LINTEL_TOKEN" \
    --progress plain \
    --load . \
    || exit 1