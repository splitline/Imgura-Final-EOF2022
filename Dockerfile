FROM docker:dind

RUN mkdir -p /manager

WORKDIR /manager

RUN apk add --no-cache --update nodejs npm python3 python3-dev py-pip docker-compose gcc g++

RUN pip install requests aiohttp


RUN printf "*/5 * * * * /usr/bin/python3 /manager/scripts/update.py;\n" >> /etc/crontabs/root

COPY ./init.sh /init.sh
RUN chmod +x /init.sh

# USER 1000
