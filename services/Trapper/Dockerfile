FROM node:20.18.1-bookworm-slim

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libxshmfence1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY services/Trapper/package.json services/Trapper/package-lock.json services/Trapper/tsconfig.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY services/Trapper/src/ src/

# Install Playwright browsers
RUN npx playwright install chromium && npx playwright install-deps chromium

# Build
RUN npm run build

# Run as non-root user for security
RUN useradd -m -u 5678 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "dist/index.js"]
