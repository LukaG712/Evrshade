# Build stage
FROM rust:1.75-slim AS builder

WORKDIR /app
COPY rust/Cargo.toml rust/Cargo.lock ./
COPY rust/crates/evershade-core/Cargo.toml crates/evershade-core/Cargo.toml
COPY rust/crates/evershade-db/Cargo.toml crates/evershade-db/Cargo.toml
COPY rust/crates/evershade-events/Cargo.toml crates/evershade-events/Cargo.toml
COPY rust/services/slinker/Cargo.toml services/slinker/Cargo.toml

RUN mkdir -p crates/evershade-core/src crates/evershade-db/src crates/evershade-events/src services/slinker/src
RUN echo "pub fn dummy() {}" > crates/evershade-core/src/lib.rs
RUN echo "pub fn dummy() {}" > crates/evershade-db/src/lib.rs
RUN echo "pub fn dummy() {}" > crates/evershade-events/src/lib.rs
RUN echo "fn main() {}" > services/slinker/src/main.rs

RUN cargo build --release -p slinker 2>/dev/null

COPY rust/crates/evershade-core/src crates/evershade-core/src
COPY rust/crates/evershade-db/src crates/evershade-db/src
COPY rust/crates/evershade-events/src crates/evershade-events/src
COPY rust/services/slinker/src services/slinker/src

RUN cargo build --release -p slinker

# Runtime stage
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends libsqlite3-0 curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app/target/release/slinker /usr/local/bin/slinker
RUN mkdir -p /app/data /tmp/workspace

ENV RUST_LOG=info
ENV DB_URL=sqlite:////app/data/slinker.db
ENV WORKSPACE_BASE=/tmp/workspace

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["slinker"]
