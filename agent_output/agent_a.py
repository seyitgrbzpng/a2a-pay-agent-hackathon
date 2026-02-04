#!/usr/bin/env python3
"""
Agent A - Service Requester and Payer
Responsibilities:
1. Request service from Agent B
2. Pay Agent B on-chain (Solana devnet)
3. Verify service result
4. Publish verification proof on-chain
"""

import asyncio
import json
from pathlib import Path
from solders.pubkey import Pubkey
from utils import WalletManager, SolanaClient, ServiceProvider, print_section


class AgentA:
    """Agent A - Service Requester"""
    
    def __init__(self, wallet_path: str = "wallets/agent_a.json"):
        self.wallet_manager = WalletManager(wallet_path)
        self.keypair = None
        self.solana_client = SolanaClient()
        self.agent_b_pubkey = None
        self.transaction_log = []
    
    async def initialize(self):
        """Initialize Agent A"""
        print_section("AGENT A INITIALIZATION")
        
        # Create or load wallet
        self.keypair = self.wallet_manager.create_or_load()
        
        # Check balance
        balance = await self.solana_client.get_balance(self.keypair.pubkey())
        print(f"Current balance: {balance} SOL")
        
        # Request airdrop if balance is low
        if balance < 1.0:
            print("Balance too low. Requesting airdrop...")
            try:
                await self.solana_client.request_airdrop(self.keypair.pubkey(), 2.0)
                balance = await self.solana_client.get_balance(self.keypair.pubkey())
                print(f"New balance: {balance} SOL")
            except Exception as e:
                print(f"Airdrop failed: {e}")
                print("Continuing with current balance...")
        
        print("Agent A initialized successfully!")
    
    def set_agent_b_address(self, pubkey: Pubkey):
        """Set Agent B's public key"""
        self.agent_b_pubkey = pubkey
        print(f"Agent B address set: {pubkey}")
    
    async def request_service(self, service_type: str, input_data: str, payment_amount: float = 0.1):
        """
        Request a service from Agent B
        
        Args:
            service_type: Type of service (e.g., 'hash')
            input_data: Input data for the service
            payment_amount: Amount to pay in SOL
        
        Returns:
            Transaction signature
        """
        print_section("REQUESTING SERVICE FROM AGENT B")
        
        if not self.agent_b_pubkey:
            raise Exception("Agent B address not set!")
        
        # Create service request memo
        memo = f"REQUEST:{service_type}:{input_data}"
        
        print(f"Service Type: {service_type}")
        print(f"Input Data: {input_data}")
        print(f"Payment Amount: {payment_amount} SOL")
        
        # Send payment with service request memo
        signature, memo_content = await self.solana_client.send_transaction_with_memo(
            sender=self.keypair,
            recipient=self.agent_b_pubkey,
            amount_sol=payment_amount,
            memo=memo
        )
        
        # Log transaction
        self.transaction_log.append({
            'type': 'service_request',
            'signature': signature,
            'memo': memo_content,
            'amount': payment_amount,
            'recipient': str(self.agent_b_pubkey)
        })
        
        print(f"\n✓ Service request sent successfully!")
        print(f"Transaction: https://explorer.solana.com/tx/{signature}?cluster=devnet")
        
        return signature
    
    async def verify_service_result(self, response_signature: str, expected_input: str) -> bool:
        """
        Verify the service result from Agent B
        
        Args:
            response_signature: Transaction signature of Agent B's response
            expected_input: Original input data to verify against
        
        Returns:
            True if verification passed, False otherwise
        """
        print_section("VERIFYING SERVICE RESULT")
        
        print(f"Response Transaction: {response_signature}")
        
        # Wait a bit for transaction to be fully processed
        await asyncio.sleep(2)
        
        # Retrieve memo from response transaction
        memo = await self.solana_client.get_transaction_memo(response_signature)
        
        if not memo:
            print("✗ Could not retrieve memo from response transaction")
            return False
        
        print(f"Response Memo: {memo}")
        
        # Parse response memo
        # Expected format: RESPONSE:hash:result_hash
        try:
            parts = memo.split(':', 2)
            if len(parts) != 3 or parts[0] != 'RESPONSE':
                print("✗ Invalid response format")
                return False
            
            service_type = parts[1]
            result = parts[2]
            
            print(f"Service Type: {service_type}")
            print(f"Result: {result}")
            
            # Verify the result
            if service_type == 'hash':
                expected_hash = ServiceProvider.compute_sha256(expected_input)
                print(f"Expected Hash: {expected_hash}")
                
                if result == expected_hash:
                    print("\n✓ Verification PASSED! Result is correct.")
                    return True
                else:
                    print("\n✗ Verification FAILED! Result does not match.")
                    return False
            else:
                print(f"✗ Unknown service type: {service_type}")
                return False
        
        except Exception as e:
            print(f"✗ Error during verification: {e}")
            return False
    
    async def publish_verification_proof(self, response_signature: str, verified: bool):
        """
        Publish verification proof on-chain
        
        Args:
            response_signature: Transaction signature being verified
            verified: Whether verification passed
        """
        print_section("PUBLISHING VERIFICATION PROOF")
        
        # Create proof memo
        proof_memo = ServiceProvider.create_verification_proof(response_signature, verified)
        
        print(f"Proof Status: {'VERIFIED' if verified else 'FAILED'}")
        print(f"Reference Transaction: {response_signature}")
        
        # Publish proof as memo-only transaction
        proof_signature = await self.solana_client.send_memo_only(
            sender=self.keypair,
            memo=proof_memo
        )
        
        # Log transaction
        self.transaction_log.append({
            'type': 'verification_proof',
            'signature': proof_signature,
            'memo': proof_memo,
            'verified': verified,
            'reference_tx': response_signature
        })
        
        print(f"\n✓ Verification proof published on-chain!")
        print(f"Proof Transaction: https://explorer.solana.com/tx/{proof_signature}?cluster=devnet")
        
        return proof_signature
    
    def save_transaction_log(self, output_path: str = "logs/agent_a_transactions.json"):
        """Save transaction log to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.transaction_log, f, indent=2)
        
        print(f"\nTransaction log saved to {output_path}")
    
    async def close(self):
        """Cleanup"""
        await self.solana_client.close()


async def main():
    """
    Main execution flow for Agent A (standalone mode)
    This is used for testing Agent A independently
    """
    agent_a = AgentA()
    
    try:
        # Initialize
        await agent_a.initialize()
        
        # For standalone testing, you would need to set Agent B's address
        # In the full demo, this will be coordinated by the demo script
        print("\nAgent A is ready to request services.")
        print("Use the demo script to run the full A2A interaction.")
        
    finally:
        await agent_a.close()


if __name__ == "__main__":
    asyncio.run(main())
