FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    curl \
    jq \
    bash \
    cron \
    tzdata \
 && rm -rf /var/lib/apt/lists/*


# Set timezone
ENV TZ=America/Mexico_City
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime

WORKDIR /app

# Copy only the scripts that exist inside the build context
COPY . /app/scripts/
RUN chmod +x /app/scripts/*.sh

# Copy crontab from the context (relative to carousel folder)
COPY crontab /etc/cron.d/carousel
RUN chmod 644 /etc/cron.d/carousel && crontab /etc/cron.d/carousel

CMD ["/app/scripts/run_carousel.sh"]
