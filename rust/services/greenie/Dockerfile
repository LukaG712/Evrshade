# Build stage
FROM rust:1.75-slim AS builder

WORKDIR /app
COPY rust/Cargo.toml rust/Cargo.lock ./
COPY rust/crates/evershade-core/Cargo.toml crates/evershade-core/Cargo.toml
COPY rust/crates/evershade-db/Cargo.toml crates/evershade-db/Cargo.toml
COPY rust/crates/evershade-events/Cargo.toml crates/evershade-events/Cargo.toml
COPY rust/services/greenie/Cargo.toml services/greenie/Cargo.toml

RUN mkdir -p crates/evershade-core/src crates/evershade-db/src crates/evershade-events/src services/greenie/src
RUN echo "pub fn dummy() {}" > crates/evershade-core/src/lib.rs
RUN echo "pub fn dummy() {}" > crates/evershade-db/src/lib.rs
RUN echo "pub fn dummy() {}" > crates/evershade-events/src/lib.rs
RUN echo "fn main() {}" > services/greenie/src/main.rs

RUN cargo build --release -p greenie 2>/dev/null

COPY rust/crates/evershade-core/src crates/evershade-core/src
COPY rust/crates/evershade-db/src crates/evershade-db/src
COPY rust/crates/evershade-events/src crates/evershade-events/src
COPY rust/services/greenie/src services/greenie/src

RUN cargo build --release -p greenie

# Runtime stage
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends libsqlite3-0 curl docker.io && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app/target/release/greenie /usr/local/bin/greenie
RUN mkdir -p /app/data

ENV RUST_LOG=info
ENV DB_URL=sqlite:////app/data/greenie.db

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["greenie"]
