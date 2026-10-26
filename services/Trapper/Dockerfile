FROM node:20-bookworm AS build

WORKDIR /app

COPY services/Trapper/package.json services/Trapper/tsconfig.json ./
RUN npm install && npx playwright install --with-deps chromium

COPY services/Trapper/src ./src
RUN npx tsc || true

FROM node:20-bookworm

WORKDIR /app

# Install system dependencies for Chromium
RUN npx playwright install-deps chromium && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /root/.cache/ms-playwright /root/.cache/ms-playwright
COPY services/Trapper/package.json ./

EXPOSE 3000

CMD ["node", "dist/index.js"]
