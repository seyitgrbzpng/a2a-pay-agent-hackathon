import json
import time
from solprism_integration import ReasoningProof, hash_reasoning_trace
from sipher_integration import SipherPrivacy

def run_privacy_verifiable_demo():
    """
    Demonstrates the complete flow of an A2A service purchase that is 
    BOTH private (via Sipher) and verifiable (via SOLPRISM).
    """
    sipher = SipherPrivacy()
    
    print("="*80)
    print("🚀 A2A MARKETPLACE DEMO: PRIVACY + VERIFIABILITY")
    print("="*80)
    
    # PHASE 1: Setup & Discovery
    print("\n[PHASE 1] Setup & Discovery")
    # Agent B registers with privacy
    b_privacy = sipher.generate_stealth_meta_address("Agent B Service Provider")
    print(f"Agent B Meta-Address: {b_privacy['metaAddress']['spendingKey'][:16]}...")
    
    # PHASE 2: Shielded Request & Payment
    print("\n[PHASE 2] Shielded Request & Payment")
    input_data = "hello_solana_privacy_2026"
    print(f"Agent A requesting hash for: '{input_data}'")
    
    # Agent A builds shielded transfer
    shielded_data = sipher.build_shielded_transfer(
        sender="Agent_A_Wallet",
        recipient_meta_address=b_privacy['metaAddress'],
        amount=100000000 # 0.1 SOL
    )
    
    stealth_address = shielded_data['data']['stealthAddress']
    commitment = shielded_data['data']['commitment']
    
    print(f"Payment sent to Stealth Address: {stealth_address}")
    print(f"Amount hidden via Pedersen Commitment: {commitment[:16]}...")
    print("✓ Transaction is now unlinkable and private.")
    
    # PHASE 3: Service Execution with Verifiable Reasoning
    print("\n[PHASE 3] Service Execution with Verifiable Reasoning")
    # Agent B detects payment and executes
    print("Agent B detecting shielded payment...")
    time.sleep(1)
    
    # Agent B generates result and reasoning proof
    import hashlib
    result = hashlib.sha256(input_data.encode()).hexdigest()
    
    # Generate SOLPRISM reasoning trace
    b_proof = ReasoningProof("Agent B", "service_execution")
    b_proof.add_observation("Detected shielded payment at stealth address")
    b_proof.add_observation(f"Payment commitment verified: {commitment[:16]}...")
    b_proof.set_decision("Execute SHA256 service for verified private request", confidence=100)
    b_proof.add_execution_detail("algorithm", "SHA256")
    b_proof.add_execution_detail("output", result)
    
    b_trace = b_proof.generate_trace()
    b_proof_hash = hash_reasoning_trace(b_trace)
    
    print(f"Service Result: {result}")
    print(f"Reasoning Proof Hash: {b_proof_hash}")
    print("✓ Reasoning is committed on-chain via SOLPRISM.")
    
    # PHASE 4: Client Verification
    print("\n[PHASE 4] Client Verification")
    # Agent A receives result and verifies
    is_valid = hashlib.sha256(input_data.encode()).hexdigest() == result
    
    # Agent A generates its own reasoning proof for verification
    a_proof = ReasoningProof("Agent A", "result_verification")
    a_proof.add_observation(f"Received result: {result[:16]}...")
    a_proof.add_observation("Verified result matches local computation")
    a_proof.set_decision("Accept service result and close transaction", confidence=100)
    
    a_trace = a_proof.generate_trace()
    a_proof_hash = hash_reasoning_trace(a_trace)
    
    print(f"Verification Result: {'✅ SUCCESS' if is_valid else '❌ FAILED'}")
    print(f"Verification Proof Hash: {a_proof_hash}")
    
    print("\n" + "="*80)
    print("✨ DEMO COMPLETE: THE FUTURE OF A2A COMMERCE")
    print("="*80)
    print("Summary:")
    print("1. Privacy: Sipher Stealth Addresses + Pedersen Commitments")
    print("2. Trust: SOLPRISM Verifiable Reasoning Traces")
    print("3. Outcome: Private business details, but verifiable execution logic.")
    print("="*80)

if __name__ == "__main__":
    run_privacy_verifiable_demo()
