# Validation tool image only; not a third RX product image.
FROM rust:1.98.1-bookworm@sha256:9a73a5088750b4c95158ab26629c854c3d6fc4b173cb7bc8079ad252d8ed7bfa
RUN rustup component add clippy --toolchain 1.98.1-aarch64-unknown-linux-gnu
