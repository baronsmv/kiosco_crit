FROM alpine:3.19

RUN apk add --no-cache curl jq bash

WORKDIR /app

COPY run-carousel.sh /app/scripts/carousel/run-carousel.sh
COPY fetch_espacios.sh /app/scripts/carousel/fetch_espacios.sh

RUN chmod +x \
    /app/scripts/carousel/fetch_espacios.sh \
    /app/scripts/carousel/run-carousel.sh

CMD ["/app/scripts/carousel/run-carousel.sh"]
