#!/usr/bin/env python3
"""
Activate accounts by sending small self-transfers
This ensures accounts are rent-exempt and active on-chain
"""

import asyncio
import json
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.system_program import transfer, TransferParams
from solders.transaction import VersionedTransaction
from solders.message import MessageV0


async def activate_account(keypair: Keypair, client: AsyncClient):
    """Send a small self-transfer to activate the account"""
    print(f"\nActivating account: {keypair.pubkey()}")
    
    # Get latest blockhash
    latest_blockhash = await client.get_latest_blockhash()
    
    # Create self-transfer (0.001 SOL to self)
    transfer_ix = transfer(
        TransferParams(
            from_pubkey=keypair.pubkey(),
            to_pubkey=keypair.pubkey(),
            lamports=1_000_000  # 0.001 SOL
        )
    )
    
    # Create message
    message = MessageV0.try_compile(
        payer=keypair.pubkey(),
        instructions=[transfer_ix],
        address_lookup_table_accounts=[],
        recent_blockhash=latest_blockhash.value.blockhash
    )
    
    # Create and sign transaction
    transaction = VersionedTransaction(message, [keypair])
    
    # Send transaction
    try:
        response = await client.send_transaction(transaction)
        signature = str(response.value)
        print(f"Activation transaction sent: {signature}")
        
        # Wait for confirmation
        await client.confirm_transaction(response.value, commitment=Confirmed)
        print(f"✓ Account activated!")
        return signature
    except Exception as e:
        print(f"✗ Activation failed: {e}")
        return None


async def main():
    print("=" * 80)
    print("  ACTIVATING ACCOUNTS")
    print("=" * 80)
    
    # Load wallets
    with open('wallets/agent_a.json') as f:
        data = json.load(f)
        agent_a = Keypair.from_bytes(bytes(data['secret_key']))
    
    with open('wallets/agent_b.json') as f:
        data = json.load(f)
        agent_b = Keypair.from_bytes(bytes(data['secret_key']))
    
    client = AsyncClient('https://api.devnet.solana.com')
    
    try:
        # Activate both accounts
        sig_a = await activate_account(agent_a, client)
        await asyncio.sleep(2)  # Wait a bit between transactions
        
        sig_b = await activate_account(agent_b, client)
        
        print("\n" + "=" * 80)
        print("  ACTIVATION COMPLETE")
        print("=" * 80)
        print(f"\nAgent A: {agent_a.pubkey()}")
        print(f"Signature: {sig_a}")
        print(f"\nAgent B: {agent_b.pubkey()}")
        print(f"Signature: {sig_b}")
        print("\nAccounts are now active and ready for transactions!")
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
