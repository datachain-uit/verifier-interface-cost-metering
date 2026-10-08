# V2-PRV-D1-01 image (linux/arm64 on the Mac M5 Docker Desktop VM). Same pinned base image and dependency lock as the
# V1 v3 prover image (research/bench); same CPU-visibility adapter (byte-identical copy). No network at run time.
ARG BASE_IMAGE=node:18.20.8-bookworm-slim@sha256:f9ab18e354e6855ae56ef2b290dd225c1e51a564f87584b9bd21dd651838830e
FROM ${BASE_IMAGE}
WORKDIR /opt/zcorp-d1
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts --no-audit --no-fund && npm cache clean --force
COPY cpu-visibility.js d1_harness.js d1_regen.js ./
ENV NODE_OPTIONS="--require /opt/zcorp-d1/cpu-visibility.js --max-old-space-size=4096"
LABEL org.opencontainers.image.title="zcorp-d1" org.opencontainers.image.description="V2-PRV-D1-01 fixed-depth PLONK domain intervention harness"
