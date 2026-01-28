FROM alpine:3.19

RUN apk add --no-cache \
    curl \
    jq \
    bash \
    busybox-suid \
    tzdata

WORKDIR /app

COPY run_carousel.sh /app/scripts/carousel/run_carousel.sh
COPY fetch_espacios.sh /app/scripts/carousel/fetch_espacios.sh
COPY crontab /etc/crontabs/root

RUN chmod +x \
    /app/scripts/carousel/fetch_espacios.sh \
    /app/scripts/carousel/run_carousel.sh
RUN cp /usr/share/zoneinfo/America/Mexico_City /etc/localtime

CMD ["/app/scripts/carousel/run_carousel.sh"]
