# Security Policy

## Supported version
The latest `main` branch is supported.

## Model
API Mock Studio is intended for local development. It binds to `127.0.0.1` by default, does not execute code from configuration, and limits request bodies to 1 MiB. Route delays are capped at 30 seconds.

Binding to `0.0.0.0` exposes mocks to the network; do so only on a trusted network and never use mock responses as an authentication boundary. `--cors` deliberately enables permissive development CORS.

## Reporting
Please report security concerns privately through GitHub's available security-reporting mechanism when enabled. Do not include real secrets or sensitive production payloads in reports or fixtures.
