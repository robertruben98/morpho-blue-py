"""Inspect a MetaMorpho vault and a wallet's positions.

Run: python examples/vaults_and_positions.py
"""

from __future__ import annotations

from morpho_blue import MorphoClient

STEAKHOUSE_USDC = "0xBEEF01735c132Ada46AA9aA4c54623cAA92A64CB"


def main() -> None:
    with MorphoClient() as client:
        vault = client.get_vault(STEAKHOUSE_USDC, chain_id=1)
        print(f"Vault {vault.name} ({vault.symbol})")
        if vault.state:
            print(f"  net APY: {vault.state.net_apy:.2%}")
            print(f"  total assets: ${vault.state.total_assets_usd:,.0f}")
            print(f"  allocations: {len(vault.state.allocation)} markets")

        user = client.get_user(STEAKHOUSE_USDC, chain_id=1)
        print(f"\nPositions for {user.address}:")
        print(f"  market positions: {len(user.market_positions)}")
        print(f"  vault positions:  {len(user.vault_positions)}")


if __name__ == "__main__":
    main()
