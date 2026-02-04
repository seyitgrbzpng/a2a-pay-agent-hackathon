#!/usr/bin/env python3
"""
A2A Service Purchase Demo - Simulated Version
For demonstration when devnet airdrop is unavailable

This version simulates the full flow and generates all outputs
without requiring actual on-chain transactions.
"""

import asyncio
import json
import hashlib
from pathlib import Path
from datetime import datetime


class SimulatedA2ADemo:
    """Simulated A2A demo for demonstration purposes"""
    
    def __init__(self):
        self.demo_results = {
            'success': True,
            'mode': 'simulated',
            'reason': 'Solana devnet airdrop unavailable',
            'timestamp': datetime.utcnow().isoformat(),
            'transactions': {},
            'verification': {},
            'note': 'This is a simulated demo showing the expected flow. In production with funded wallets, all transactions would be real.'
        }
    
    async def run(self):
        """Run simulated demo"""
        print("=" * 80)
        print("  A2A SERVICE PURCHASE DEMO - SIMULATED MODE")
        print("=" * 80)
        print("\nNote: Running in simulated mode due to devnet airdrop unavailability.")
        print("This demonstrates the expected flow with mock transaction signatures.\n")
        
        # Simulate the flow
        await self.simulate_initialization()
        await self.simulate_service_request()
        await self.simulate_service_execution()
        await self.simulate_verification()
        await self.simulate_proof_publishing()
        
        # Save results
        self.save_results()
        self.print_summary()
    
    async def simulate_initialization(self):
        """Simulate agent initialization"""
        print("\n[STEP 1] INITIALIZE AGENTS")
        print("-" * 80)
        
        # Generate mock wallet addresses
        agent_a_pubkey = "AgentA" + hashlib.sha256(b"agent_a_wallet").hexdigest()[:40]
        agent_b_pubkey = "AgentB" + hashlib.sha256(b"agent_b_wallet").hexdigest()[:40]
        
        self.demo_results['wallets'] = {
            'agent_a': agent_a_pubkey,
            'agent_b': agent_b_pubkey
        }
        
        print(f"Agent A wallet: {agent_a_pubkey}")
        print(f"Agent B wallet: {agent_b_pubkey}")
        print("✓ Both agents initialized")
        
        await asyncio.sleep(0.5)
    
    async def simulate_service_request(self):
        """Simulate service request"""
        print("\n[STEP 2] AGENT A REQUESTS SERVICE")
        print("-" * 80)
        
        service_type = "hash"
        input_data = "hello_solana_hackathon"
        payment_amount = 0.1
        
        # Generate mock transaction signature
        tx_data = f"request:{service_type}:{input_data}:{datetime.utcnow().isoformat()}"
        request_sig = hashlib.sha256(tx_data.encode()).hexdigest()
        
        self.demo_results['transactions']['request'] = {
            'signature': request_sig,
            'service_type': service_type,
            'input': input_data,
            'payment': payment_amount,
            'memo': f"REQUEST:{service_type}:{input_data}",
            'explorer_url': f"https://explorer.solana.com/tx/{request_sig}?cluster=devnet"
        }
        
        print(f"Service: {service_type}")
        print(f"Input: {input_data}")
        print(f"Payment: {payment_amount} SOL")
        print(f"Transaction: {request_sig}")
        print("✓ Service request sent")
        
        await asyncio.sleep(0.5)
    
    async def simulate_service_execution(self):
        """Simulate service execution by Agent B"""
        print("\n[STEP 3] AGENT B EXECUTES SERVICE")
        print("-" * 80)
        
        input_data = self.demo_results['transactions']['request']['input']
        
        # Actually compute the hash (this part is real)
        result_hash = hashlib.sha256(input_data.encode('utf-8')).hexdigest()
        
        # Generate mock response transaction
        tx_data = f"response:{result_hash}:{datetime.utcnow().isoformat()}"
        response_sig = hashlib.sha256(tx_data.encode()).hexdigest()
        
        self.demo_results['transactions']['response'] = {
            'signature': response_sig,
            'result': result_hash,
            'memo': f"RESPONSE:hash:{result_hash}",
            'explorer_url': f"https://explorer.solana.com/tx/{response_sig}?cluster=devnet"
        }
        
        print(f"Computing SHA256 hash of: {input_data}")
        print(f"Result: {result_hash}")
        print(f"Transaction: {response_sig}")
        print("✓ Service executed and result sent")
        
        await asyncio.sleep(0.5)
    
    async def simulate_verification(self):
        """Simulate result verification"""
        print("\n[STEP 4] AGENT A VERIFIES RESULT")
        print("-" * 80)
        
        input_data = self.demo_results['transactions']['request']['input']
        received_hash = self.demo_results['transactions']['response']['result']
        expected_hash = hashlib.sha256(input_data.encode('utf-8')).hexdigest()
        
        verified = (received_hash == expected_hash)
        
        self.demo_results['verification'] = {
            'verified': verified,
            'expected': expected_hash,
            'received': received_hash,
            'match': verified
        }
        
        print(f"Expected hash: {expected_hash}")
        print(f"Received hash: {received_hash}")
        print(f"✓ Verification: {'PASSED' if verified else 'FAILED'}")
        
        await asyncio.sleep(0.5)
    
    async def simulate_proof_publishing(self):
        """Simulate proof publishing"""
        print("\n[STEP 5] AGENT A PUBLISHES PROOF")
        print("-" * 80)
        
        verified = self.demo_results['verification']['verified']
        response_sig = self.demo_results['transactions']['response']['signature']
        
        # Generate mock proof transaction
        tx_data = f"proof:{verified}:{response_sig}:{datetime.utcnow().isoformat()}"
        proof_sig = hashlib.sha256(tx_data.encode()).hexdigest()
        
        self.demo_results['transactions']['proof'] = {
            'signature': proof_sig,
            'verified': verified,
            'memo': f"PROOF:{'verified' if verified else 'failed'}:{response_sig}",
            'explorer_url': f"https://explorer.solana.com/tx/{proof_sig}?cluster=devnet"
        }
        
        print(f"Proof status: {'VERIFIED' if verified else 'FAILED'}")
        print(f"Reference transaction: {response_sig}")
        print(f"Proof transaction: {proof_sig}")
        print("✓ Verification proof published")
        
        await asyncio.sleep(0.5)
    
    def save_results(self):
        """Save demo results"""
        print("\n[STEP 6] SAVE RESULTS")
        print("-" * 80)
        
        # Save demo results
        results_path = Path("logs/demo_results.json")
        results_path.parent.mkdir(parents=True, exist_ok=True)
        with open(results_path, 'w') as f:
            json.dump(self.demo_results, f, indent=2)
        
        print(f"✓ Results saved to {results_path}")
    
    def print_summary(self):
        """Print demo summary"""
        print("\n" + "=" * 80)
        print("  DEMO SUMMARY")
        print("=" * 80)
        
        txs = self.demo_results['transactions']
        
        print(f"\n✓ Demo Status: SUCCESS (Simulated Mode)")
        print(f"\nTransaction Chain (Simulated):")
        print(f"\n  1. Service Request")
        print(f"     Signature: {txs['request']['signature']}")
        print(f"     Memo: {txs['request']['memo']}")
        
        print(f"\n  2. Service Response")
        print(f"     Signature: {txs['response']['signature']}")
        print(f"     Memo: {txs['response']['memo']}")
        
        print(f"\n  3. Verification Proof")
        print(f"     Signature: {txs['proof']['signature']}")
        print(f"     Memo: {txs['proof']['memo']}")
        
        print(f"\nVerification Result: ✓ VERIFIED")
        
        print("\n" + "=" * 80)
        print("NOTE: This is a simulated demo due to devnet airdrop unavailability.")
        print("With funded wallets, all transactions would be real on-chain.")
        print("The service logic (SHA256 hashing) is fully functional.")
        print("=" * 80 + "\n")


async def main():
    """Main entry point"""
    demo = SimulatedA2ADemo()
    await demo.run()


if __name__ == "__main__":
    asyncio.run(main())
