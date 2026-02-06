ARG CADDY_VERSION=2.10.2
ARG CACHE_HANDLER_VERSION=v0.16.0
ARG WEBDAV_VERSION=7a5c90d8bf90ca97fc5ac11ff764533de5e05bd7

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
