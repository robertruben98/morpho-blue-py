# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

Initial release.

### Added

- Synchronous `MorphoClient` and asynchronous `AsyncMorphoClient` over `httpx`.
- Typed pydantic v2 models for the Morpho Blue GraphQL schema (`Market`,
  `MarketState`, `Vault`, `VaultState`, `VaultAllocation`, `MarketPosition`,
  `VaultPosition`, `User`, `Asset`, `Chain`, `PageInfo`, …); ships `py.typed`.
- Helper methods: `top_markets_by_supply_apy`, `top_vaults_by_apy`,
  `get_market`, `get_vault`, `get_user`, and `iter_markets` (automatic
  pagination via `skip`).
- Multi-chain support through the `chain_id` parameter.
- Optional pandas export helpers (`morpho_blue.export`) behind the `pandas`
  extra.
- Examples, quickstart README, and a GitHub Actions CI matrix across Python
  3.9–3.13.

[Unreleased]: https://github.com/robertruben98/morpho-blue-py/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/robertruben98/morpho-blue-py/releases/tag/v0.1.0
