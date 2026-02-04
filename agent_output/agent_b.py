#!/usr/bin/env python3
"""
Agent B - Service Provider
Responsibilities:
1. Receive payment from Agent A
2. Parse service request from transaction memo
3. Execute the requested service
4. Return result to Agent A via transaction with memo
"""

import asyncio
import json
from pathlib import Path
from solders.pubkey import Pubkey
from utils import WalletManager, SolanaClient, ServiceProvider, print_section


class AgentB:
    """Agent B - Service Provider"""
    
    def __init__(self, wallet_path: str = "wallets/agent_b.json"):
        self.wallet_manager = WalletManager(wallet_path)
        self.keypair = None
        self.solana_client = SolanaClient()
        self.transaction_log = []
        self.services = {
            'hash': self._execute_hash_service
        }
    
    async def initialize(self):
        """Initialize Agent B"""
        print_section("AGENT B INITIALIZATION")
        
        # Create or load wallet
        self.keypair = self.wallet_manager.create_or_load()
        
        # Check balance
        balance = await self.solana_client.get_balance(self.keypair.pubkey())
        print(f"Current balance: {balance} SOL")
        
        # Request airdrop if balance is low (needed for transaction fees)
        if balance < 0.5:
            print("Balance too low for transaction fees. Requesting airdrop...")
            try:
                await self.solana_client.request_airdrop(self.keypair.pubkey(), 1.0)
                balance = await self.solana_client.get_balance(self.keypair.pubkey())
                print(f"New balance: {balance} SOL")
            except Exception as e:
                print(f"Airdrop failed: {e}")
                print("Continuing with current balance...")
        
        print("Agent B initialized successfully!")
        print(f"Ready to provide services: {list(self.services.keys())}")
    
    async def process_service_request(self, request_signature: str, agent_a_pubkey: Pubkey):
        """
        Process a service request from Agent A
        
        Args:
            request_signature: Transaction signature containing the service request
            agent_a_pubkey: Public key of Agent A (for sending response)
        
        Returns:
            Response transaction signature
        """
        print_section("PROCESSING SERVICE REQUEST")
        
        print(f"Request Transaction: {request_signature}")
        
        # Wait a bit for transaction to be fully processed
        await asyncio.sleep(2)
        
        # Retrieve memo from request transaction
        memo = await self.solana_client.get_transaction_memo(request_signature)
        
        if not memo:
            print("✗ Could not retrieve memo from request transaction")
            raise Exception("No memo found in request transaction")
        
        print(f"Request Memo: {memo}")
        
        # Parse service request
        request = ServiceProvider.parse_service_request(memo)
        
        if not request:
            print("✗ Invalid service request format")
            raise Exception("Invalid service request format")
        
        service_type = request['type']
        input_data = request['input']
        
        print(f"Service Type: {service_type}")
        print(f"Input Data: {input_data}")
        
        # Verify payment was received
        await self._verify_payment_received(request_signature, agent_a_pubkey)
        
        # Execute service
        result = await self.execute_service(service_type, input_data)
        
        # Send result back to Agent A
        response_signature = await self.send_service_result(
            agent_a_pubkey,
            service_type,
            result
        )
        
        # Log transaction
        self.transaction_log.append({
            'type': 'service_execution',
            'request_signature': request_signature,
            'response_signature': response_signature,
            'service_type': service_type,
            'input': input_data,
            'result': result,
            'client': str(agent_a_pubkey)
        })
        
        return response_signature
    
    async def _verify_payment_received(self, tx_signature: str, expected_sender: Pubkey):
        """Verify that payment was received in the transaction"""
        print("\nVerifying payment...")
        
        # In a production system, we would:
        # 1. Parse the transaction to verify the transfer amount
        # 2. Verify the sender matches expected_sender
        # 3. Verify the recipient is our address
        # For this demo, we assume the transaction exists and is valid
        
        balance = await self.solana_client.get_balance(self.keypair.pubkey())
        print(f"Current balance: {balance} SOL")
        print("✓ Payment verified (transaction exists on-chain)")
    
    async def execute_service(self, service_type: str, input_data: str) -> str:
        """
        Execute the requested service
        
        Args:
            service_type: Type of service to execute
            input_data: Input data for the service
        
        Returns:
            Service result as string
        """
        print_section("EXECUTING SERVICE")
        
        if service_type not in self.services:
            raise Exception(f"Unknown service type: {service_type}")
        
        # Execute the service
        result = await self.services[service_type](input_data)
        
        print(f"Service Type: {service_type}")
        print(f"Input: {input_data}")
        print(f"Result: {result}")
        print("\n✓ Service executed successfully!")
        
        return result
    
    async def _execute_hash_service(self, input_data: str) -> str:
        """Execute SHA256 hash service"""
        return ServiceProvider.compute_sha256(input_data)
    
    async def send_service_result(
        self,
        recipient: Pubkey,
        service_type: str,
        result: str,
        amount_sol: float = 0.001
    ) -> str:
        """
        Send service result back to client
        
        Args:
            recipient: Client's public key
            service_type: Type of service executed
            result: Service result
            amount_sol: Small amount to send (for transaction to be valid)
        
        Returns:
            Transaction signature
        """
        print_section("SENDING SERVICE RESULT")
        
        # Create response memo
        response_memo = ServiceProvider.create_service_response(service_type, result)
        
        print(f"Sending result to: {recipient}")
        print(f"Response Memo: {response_memo}")
        
        # Send transaction with result memo
        signature, _ = await self.solana_client.send_transaction_with_memo(
            sender=self.keypair,
            recipient=recipient,
            amount_sol=amount_sol,
            memo=response_memo
        )
        
        print(f"\n✓ Service result sent!")
        print(f"Response Transaction: https://explorer.solana.com/tx/{signature}?cluster=devnet")
        
        return signature
    
    def save_transaction_log(self, output_path: str = "logs/agent_b_transactions.json"):
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
    Main execution flow for Agent B (standalone mode)
    This is used for testing Agent B independently
    """
    agent_b = AgentB()
    
    try:
        # Initialize
        await agent_b.initialize()
        
        # For standalone testing, you would need to provide a request signature
        # In the full demo, this will be coordinated by the demo script
        print("\nAgent B is ready to provide services.")
        print("Use the demo script to run the full A2A interaction.")
        
    finally:
        await agent_b.close()


if __name__ == "__main__":
    asyncio.run(main())
