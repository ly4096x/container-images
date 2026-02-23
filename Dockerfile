ARG CADDY_VERSION=2.11.0
ARG CACHE_HANDLER_VERSION=v0.16.0
ARG WEBDAV_VERSION=fa2f366b0d75e54c2e381c0aefc3a8df8bf5794b

FROM caddy:${CADDY_VERSION}-builder AS builder

ARG CACHE_HANDLER_VERSION
ARG WEBDAV_VERSION

RUN xcaddy build \
    --with github.com/caddyserver/cache-handler@${CACHE_HANDLER_VERSION} \
    --with github.com/mholt/caddy-webdav@${WEBDAV_VERSION}


FROM caddy:${CADDY_VERSION}

VOLUME /data /config

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
COPY docker-entrypoint.sh /

RUN apk add --no-cache su-exec bash && \
        chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
