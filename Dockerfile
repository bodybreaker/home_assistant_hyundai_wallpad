ARG BUILD_FROM=ghcr.io/hassio-addons/base:15.0.6
FROM ${BUILD_FROM}

ENV LANG C.UTF-8

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install requirements for add-on
RUN \
    apk add --no-cache \
        python3=3.11.9-r0 \
    \
    && apk add --no-cache \
        py3-pip=23.3.1-r0 \
    \
    && python3 --version \
    && pip3 --version \
    && pip install pyserial paho-mqtt 

# # Copy root file system
COPY rootfs /

CMD [ "/test.sh" ]