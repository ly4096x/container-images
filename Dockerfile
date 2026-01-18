ARG CADDY_VERSION=2.8.4
ARG CACHE_HANDLER_VERSION=v0.15.0
ARG WEBDAV_VERSION=bfcd3903f21e5cdaac29ed47777356a8a18deaf5

FROM caddy:${CADDY_VERSION}-builder AS builder

ARG CACHE_HANDLER_VERSION
ARG WEBDAV_VERSION

RUN xcaddy build \
    --with github.com/caddyserver/cache-handler@${CACHE_HANDLER_VERSION} \
    --with github.com/mholt/caddy-webdav@${WEBDAV_VERSION}

FROM caddy:${CADDY_VERSION}

COPY --from=builder /usr/bin/caddy /usr/bin/caddy

