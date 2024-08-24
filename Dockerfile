FROM python:latest

WORKDIR /main

COPY . .

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get -y install \
    && pip install --upgrade pip \
    && pip install requests \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf \
        /tmp/* \
        /moviepilot/.cache \
        /var/lib/apt/lists/* \
        /var/tmp/*

COPY entrypoint /entrypoint

RUN chmod +x /entrypoint

ENTRYPOINT ["/entrypoint"]
