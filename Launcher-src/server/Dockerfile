FROM node:22-alpine AS build

WORKDIR /app
COPY server/package.json server/package-lock.json* ./
RUN npm install --omit=dev --no-audit --no-fund

COPY server/src/ ./src/

FROM node:22-alpine AS runtime

RUN adduser -D -H -s /sbin/nologin manifest

WORKDIR /app
COPY --from=build --chown=manifest:manifest /app /app

RUN npm install --no-save --no-audit --no-fund tsx@^4.21.0

USER manifest
EXPOSE 7384

ENV SOURCE_DIR=/srv/source
ENV LAUNCHER_UPDATES_DIR=/srv/launcher-updates

ENTRYPOINT ["node", "--import", "tsx/esm", "src/index.ts"]
