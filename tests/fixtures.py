"""Realistic GraphQL response fixtures captured from the live Morpho Blue API.

These mirror the exact shape returned by https://blue-api.morpho.org/graphql so
that unit tests exercise real field names without touching the network.
"""

from __future__ import annotations

from typing import Any

# Response for a `markets` query (Query.markets -> PaginatedMarkets).
MARKETS_RESPONSE: dict[str, Any] = {
    "data": {
        "markets": {
            "items": [
                {
                    "marketId": "0x8eaf7b29f02ba8d8c1d7aeb587403dcb16e2e943e4e2f5f94b0963c2386406c9",
                    "lltv": "915000000000000000",
                    "chain": {"id": 1, "network": "Ethereum"},
                    "loanAsset": {
                        "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                        "symbol": "USDC",
                        "decimals": 6,
                    },
                    "collateralAsset": {
                        "address": "0x45804880De22913dAFE09f4980848ECE6EcbAf78",
                        "symbol": "PAXG",
                        "decimals": 18,
                    },
                    "state": {
                        "supplyApy": 0.0521,
                        "borrowApy": 0.0712,
                        "utilization": 0.91,
                        "supplyAssets": "1480310629000000",
                        "borrowAssets": "1340000000000000",
                        "supplyAssetsUsd": 1480310629.40,
                        "borrowAssetsUsd": 1340000000.0,
                        "fee": 0.0,
                    },
                },
                {
                    "marketId": "0x1dca6989b0d2b0a546530b3a739e91402eee2e1536a2d3ded4f5ce589a9cd1c2",
                    "lltv": "945000000000000000",
                    "chain": {"id": 1, "network": "Ethereum"},
                    "loanAsset": {
                        "address": "0x66a1E37c9b0eAddca17d3662D6c05F4DECf3e110",
                        "symbol": "USR",
                        "decimals": 18,
                    },
                    # collateralAsset is nullable in the schema (idle markets).
                    "collateralAsset": None,
                    "state": {
                        "supplyApy": 0.031,
                        "borrowApy": 0.045,
                        "utilization": 0.5,
                        "supplyAssets": "3685631994000000000",
                        "borrowAssets": "1842815997000000000",
                        "supplyAssetsUsd": 3685631994.46,
                        "borrowAssetsUsd": 1842815997.0,
                        "fee": 0.0,
                    },
                },
            ],
            "pageInfo": {"countTotal": 1590, "count": 2, "limit": 2, "skip": 0},
        }
    }
}

# Response for `marketById` (Query.marketById -> Market).
MARKET_BY_ID_RESPONSE: dict[str, Any] = {
    "data": {
        "marketById": {
            "marketId": "0x8eaf7b29f02ba8d8c1d7aeb587403dcb16e2e943e4e2f5f94b0963c2386406c9",
            "lltv": "915000000000000000",
            "chain": {"id": 1, "network": "Ethereum"},
            "loanAsset": {
                "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                "symbol": "USDC",
                "decimals": 6,
            },
            "collateralAsset": {
                "address": "0x45804880De22913dAFE09f4980848ECE6EcbAf78",
                "symbol": "PAXG",
                "decimals": 18,
            },
            "state": {
                "supplyApy": 0.0521,
                "borrowApy": 0.0712,
                "utilization": 0.91,
                "supplyAssets": "1480310629000000",
                "borrowAssets": "1340000000000000",
                "supplyAssetsUsd": 1480310629.40,
                "borrowAssetsUsd": 1340000000.0,
                "fee": 0.0,
            },
        }
    }
}

# Response for `vaults` (Query.vaults -> PaginatedMetaMorphos).
VAULTS_RESPONSE: dict[str, Any] = {
    "data": {
        "vaults": {
            "items": [
                {
                    "address": "0xBEEF01735c132Ada46AA9aA4c54623cAA92A64CB",
                    "name": "Steakhouse USDC",
                    "symbol": "steakUSDC",
                    "chain": {"id": 1, "network": "Ethereum"},
                    "asset": {
                        "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                        "symbol": "USDC",
                        "decimals": 6,
                    },
                    "state": {
                        "apy": 0.0366,
                        "netApy": 0.0347,
                        "totalAssets": "95871274932472",
                        "totalAssetsUsd": 95857281.66,
                        "fee": 0.05,
                        "allocation": [
                            {
                                "supplyAssetsUsd": 11335891.40,
                                "supplyCapUsd": 50000000.0,
                                "market": {
                                    "marketId": "0x3a85e619751152991742810df6ec69ce473daef99e28a64ab2340d7b7ccfee49"
                                },
                            },
                            {
                                "supplyAssetsUsd": 699289.86,
                                "supplyCapUsd": 5000000.0,
                                "market": {
                                    "marketId": "0x94b823e6bd8ea533b4e33fbc307faea0b307301bc48763acc4d4aa4def7636cd"
                                },
                            },
                        ],
                    },
                }
            ],
            "pageInfo": {"countTotal": 320, "count": 1, "limit": 1, "skip": 0},
        }
    }
}

# Response for `vaultByAddress` (Query.vaultByAddress -> Vault).
VAULT_BY_ADDRESS_RESPONSE: dict[str, Any] = {
    "data": {"vaultByAddress": VAULTS_RESPONSE["data"]["vaults"]["items"][0]}
}

# Response for `userByAddress` (Query.userByAddress -> User) with positions.
USER_BY_ADDRESS_RESPONSE: dict[str, Any] = {
    "data": {
        "userByAddress": {
            "address": "0x47E2D28169738039755586743E2dfCF3bd643f86",
            "chain": {"id": 1, "network": "Ethereum"},
            "marketPositions": [
                {
                    "market": {
                        "marketId": "0x495130878b7d2f1391e21589a8bcaef22cbc7e1fbbd6866127193b3cc239d8b1",
                        "loanAsset": {
                            "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                            "symbol": "USDC",
                            "decimals": 6,
                        },
                        "collateralAsset": {
                            "address": "0xae78736Cd615f374D3085123A210448E74Fc6393",
                            "symbol": "rETH",
                            "decimals": 18,
                        },
                    },
                    "healthFactor": 1.85,
                    "state": {
                        "supplyAssets": "1000000000",
                        "borrowAssets": "500000000",
                        "collateral": "2000000000000000000",
                        "supplyAssetsUsd": 1000.0,
                        "borrowAssetsUsd": 500.0,
                        "collateralUsd": 5400.0,
                    },
                }
            ],
            "vaultPositions": [
                {
                    "vault": {
                        "address": "0xBEEF01735c132Ada46AA9aA4c54623cAA92A64CB",
                        "symbol": "steakUSDC",
                        "name": "Steakhouse USDC",
                    },
                    "state": {
                        "assets": "1500000000",
                        "assetsUsd": 1500.0,
                        "shares": "1450000000000000000000",
                    },
                }
            ],
        }
    }
}

# An error response (GraphQL returns HTTP 200 with an `errors` array).
ERROR_RESPONSE: dict[str, Any] = {
    "errors": [
        {
            "message": 'Cannot query field "uniqueKey" on type "Market".',
            "status": "GRAPHQL_VALIDATION_FAILED",
            "extensions": {},
        }
    ]
}
