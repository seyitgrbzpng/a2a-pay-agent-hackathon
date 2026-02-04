#!/usr/bin/env python3
"""
A2A Service Purchase Demo - Main Orchestration Script
Demonstrates autonomous agent-to-agent service purchase on Solana devnet

Flow:
1. Initialize both Agent A and Agent B
2. Agent A requests service from Agent B with payment
3. Agent B processes request and returns result
4. Agent A verifies result and publishes proof
"""

import asyncio
import json
import sys
from pathlib import Path

# Add agent_output to path
sys.path.insert(0, str(Path(__file__).parent))

from agent_a import AgentA
from agent_b import AgentB
from utils import print_section


class A2ADemo:
    """Orchestrates the A2A service purchase demo"""
    
    def __init__(self):
        self.agent_a = AgentA("wallets/agent_a.json")
        self.agent_b = AgentB("wallets/agent_b.json")
        self.demo_results = {
            'success': False,
            'transactions': {},
            'errors': []
        }
    
    async def run(self):
        """Run the complete A2A demo"""
        try:
            print_section("A2A SERVICE PURCHASE DEMO - START")
            print("Demonstrating autonomous agent-to-agent interaction on Solana devnet")
            print("Service: SHA256 Hash Generation")
            print("Payment: 0.1 SOL on devnet")
            
            # Step 1: Initialize both agents
            await self.initialize_agents()
            
            # Step 2: Agent A requests service
            request_signature = await self.agent_a_request_service()
            
            # Step 3: Agent B processes request
            response_signature = await self.agent_b_process_request(request_signature)
            
            # Step 4: Agent A verifies result
            verified = await self.agent_a_verify_result(response_signature)
            
            # Step 5: Agent A publishes proof
            proof_signature = await self.agent_a_publish_proof(response_signature, verified)
            
            # Step 6: Save results
            await self.save_results()
            
            # Mark demo as successful
            self.demo_results['success'] = True
            
            print_section("A2A SERVICE PURCHASE DEMO - COMPLETE")
            self.print_summary()
            
        except Exception as e:
            print_section("DEMO FAILED")
            print(f"Error: {e}")
            self.demo_results['errors'].append(str(e))
            raise
        
        finally:
            await self.cleanup()
    
    async def initialize_agents(self):
        """Initialize both Agent A and Agent B"""
        print_section("STEP 1: INITIALIZE AGENTS")
        
        # Initialize Agent A
        print("\n[Agent A]")
        await self.agent_a.initialize()
        
        # Initialize Agent B
        print("\n[Agent B]")
        await self.agent_b.initialize()
        
        # Connect Agent A to Agent B
        self.agent_a.set_agent_b_address(self.agent_b.keypair.pubkey())
        
        print("\n✓ Both agents initialized and connected!")
    
    async def agent_a_request_service(self) -> str:
        """Agent A requests service from Agent B"""
        print_section("STEP 2: AGENT A REQUESTS SERVICE")
        
        # Service parameters
        service_type = "hash"
        input_data = "hello_solana_hackathon"
        payment_amount = 0.1
        
        print(f"\n[Agent A] Requesting service...")
        signature = await self.agent_a.request_service(
            service_type=service_type,
            input_data=input_data,
            payment_amount=payment_amount
        )
        
        self.demo_results['transactions']['request'] = {
            'signature': signature,
            'service_type': service_type,
            'input': input_data,
            'payment': payment_amount
        }
        
        return signature
    
    async def agent_b_process_request(self, request_signature: str) -> str:
        """Agent B processes the service request"""
        print_section("STEP 3: AGENT B PROCESSES REQUEST")
        
        print(f"\n[Agent B] Processing service request...")
        response_signature = await self.agent_b.process_service_request(
            request_signature=request_signature,
            agent_a_pubkey=self.agent_a.keypair.pubkey()
        )
        
        self.demo_results['transactions']['response'] = {
            'signature': response_signature
        }
        
        return response_signature
    
    async def agent_a_verify_result(self, response_signature: str) -> bool:
        """Agent A verifies the service result"""
        print_section("STEP 4: AGENT A VERIFIES RESULT")
        
        print(f"\n[Agent A] Verifying service result...")
        
        # Get the original input from the request
        original_input = self.demo_results['transactions']['request']['input']
        
        verified = await self.agent_a.verify_service_result(
            response_signature=response_signature,
            expected_input=original_input
        )
        
        self.demo_results['verification'] = {
            'verified': verified,
            'response_signature': response_signature
        }
        
        return verified
    
    async def agent_a_publish_proof(self, response_signature: str, verified: bool) -> str:
        """Agent A publishes verification proof on-chain"""
        print_section("STEP 5: AGENT A PUBLISHES PROOF")
        
        print(f"\n[Agent A] Publishing verification proof...")
        proof_signature = await self.agent_a.publish_verification_proof(
            response_signature=response_signature,
            verified=verified
        )
        
        self.demo_results['transactions']['proof'] = {
            'signature': proof_signature,
            'verified': verified
        }
        
        return proof_signature
    
    async def save_results(self):
        """Save demo results and transaction logs"""
        print_section("STEP 6: SAVE RESULTS")
        
        # Save agent transaction logs
        self.agent_a.save_transaction_log("logs/agent_a_transactions.json")
        self.agent_b.save_transaction_log("logs/agent_b_transactions.json")
        
        # Save demo results
        results_path = Path("logs/demo_results.json")
        with open(results_path, 'w') as f:
            json.dump(self.demo_results, f, indent=2)
        
        print(f"Demo results saved to {results_path}")
    
    def print_summary(self):
        """Print demo summary"""
        print("\n" + "=" * 80)
        print("  DEMO SUMMARY")
        print("=" * 80)
        
        txs = self.demo_results['transactions']
        
        print(f"\n✓ Demo Status: {'SUCCESS' if self.demo_results['success'] else 'FAILED'}")
        print(f"\nTransaction Chain:")
        print(f"  1. Service Request:  {txs['request']['signature']}")
        print(f"     https://explorer.solana.com/tx/{txs['request']['signature']}?cluster=devnet")
        print(f"\n  2. Service Response: {txs['response']['signature']}")
        print(f"     https://explorer.solana.com/tx/{txs['response']['signature']}?cluster=devnet")
        print(f"\n  3. Verification Proof: {txs['proof']['signature']}")
        print(f"     https://explorer.solana.com/tx/{txs['proof']['signature']}?cluster=devnet")
        
        print(f"\nVerification Result: {'✓ VERIFIED' if self.demo_results['verification']['verified'] else '✗ FAILED'}")
        
        print("\n" + "=" * 80)
        print("All transactions are permanently recorded on Solana devnet blockchain.")
        print("This demonstrates cryptographic proof of agent-to-agent interaction.")
        print("=" * 80 + "\n")
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.agent_a.close()
        await self.agent_b.close()


async def main():
    """Main entry point"""
    demo = A2ADemo()
    await demo.run()


if __name__ == "__main__":
    asyncio.run(main())
