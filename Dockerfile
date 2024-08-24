FROM python:latest

WORKDIR /main

COPY . .

RUN pip install --no-cache-dir requests

RUN apt-get update && apt-get install -y cron

RUN echo "*/30 * * * * cd /app && /usr/local/bin/python main.py" > /etc/cron.d/Alist-Move

RUN chmod 0644 /etc/cron.d/Alist-Move

RUN crontab /etc/cron.d/Alist-Move

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
