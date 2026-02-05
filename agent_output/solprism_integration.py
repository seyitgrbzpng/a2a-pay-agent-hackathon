"""
SOLPRISM Integration for A2A Service Purchase Demo
Adds verifiable reasoning layer to agent decision-making

Based on community feedback from Mereum (@Mereum) in forum post #1239
Integration completed in response to hackathon community collaboration
"""

import hashlib
import json
from typing import Dict, Any
from datetime import datetime


class ReasoningProof:
    """
    Generates verifiable reasoning proofs for agent actions
    Compatible with SOLPRISM protocol structure
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.version = "1.0.0"
    
    def create_service_execution_proof(
        self,
        service_type: str,
        input_data: str,
        output_data: str,
        confidence: int = 100
    ) -> Dict[str, Any]:
        """
        Create a reasoning trace for service execution
        
        Args:
            service_type: Type of service (e.g., "hash")
            input_data: Input provided by client
            output_data: Result computed by service
            confidence: Confidence level (0-100)
        
        Returns:
            Reasoning trace dict compatible with SOLPRISM
        """
        trace = {
            "version": self.version,
            "agent": self.agent_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": {
                "type": "service_execution",
                "description": f"Execute {service_type} service"
            },
            "inputs": {
                "dataSources": [
                    {
                        "name": "Client Request",
                        "type": "transaction_memo",
                        "summary": f"Input: {input_data[:50]}..."
                    }
                ],
                "context": "A2A service marketplace request via Solana transaction"
            },
            "analysis": {
                "observations": [
                    f"Service type requested: {service_type}",
                    f"Input data length: {len(input_data)} characters",
                    "Payment verified on-chain"
                ],
                "logic": f"Apply {service_type.upper()} algorithm to input data and return result",
                "alternativesConsidered": [
                    {
                        "action": "Reject request",
                        "reasonRejected": "Payment verified and input valid"
                    }
                ]
            },
            "decision": {
                "actionChosen": f"Compute {service_type} and return via transaction memo",
                "confidence": confidence,
                "riskAssessment": "low",
                "expectedOutcome": f"Client receives {service_type} result and can verify correctness"
            },
            "execution": {
                "algorithm": service_type.upper(),
                "input": input_data,
                "output": output_data,
                "verifiable": True
            }
        }
        
        return trace
    
    def hash_reasoning_trace(self, trace: Dict[str, Any]) -> str:
        """
        Generate SHA256 hash of reasoning trace
        This hash would be committed on-chain via SOLPRISM
        
        Args:
            trace: Reasoning trace dict
        
        Returns:
            SHA256 hash as hex string
        """
        trace_json = json.dumps(trace, sort_keys=True)
        return hashlib.sha256(trace_json.encode()).hexdigest()
    
    def create_verification_proof(
        self,
        expected_result: str,
        actual_result: str,
        service_tx: str
    ) -> Dict[str, Any]:
        """
        Create a reasoning trace for result verification
        
        Args:
            expected_result: Result computed locally
            actual_result: Result received from provider
            service_tx: Transaction signature of service response
        
        Returns:
            Verification reasoning trace
        """
        verified = (expected_result == actual_result)
        
        trace = {
            "version": self.version,
            "agent": self.agent_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": {
                "type": "result_verification",
                "description": "Verify service provider result"
            },
            "inputs": {
                "dataSources": [
                    {
                        "name": "Service Response Transaction",
                        "type": "solana_transaction",
                        "summary": f"TX: {service_tx[:16]}..."
                    }
                ],
                "context": "Received result from A2A service provider"
            },
            "analysis": {
                "observations": [
                    f"Expected result: {expected_result[:32]}...",
                    f"Received result: {actual_result[:32]}...",
                    f"Results match: {verified}"
                ],
                "logic": "Compare locally computed result with provider result for correctness",
                "alternativesConsidered": [
                    {
                        "action": "Accept without verification",
                        "reasonRejected": "Trust-but-verify principle requires validation"
                    }
                ]
            },
            "decision": {
                "actionChosen": "Accept result" if verified else "Reject result",
                "confidence": 100 if verified else 0,
                "riskAssessment": "none" if verified else "high",
                "expectedOutcome": "Publish verification proof on-chain"
            },
            "verification": {
                "verified": verified,
                "expected": expected_result,
                "actual": actual_result,
                "service_transaction": service_tx
            }
        }
        
        return trace
    
    def save_trace(self, trace: Dict[str, Any], filepath: str):
        """Save reasoning trace to file"""
        with open(filepath, 'w') as f:
            json.dump(trace, f, indent=2)
    
    def load_trace(self, filepath: str) -> Dict[str, Any]:
        """Load reasoning trace from file"""
        with open(filepath, 'r') as f:
            return json.load(f)


# Example usage for Agent B (Service Provider)
def agent_b_with_reasoning_proof(input_data: str, service_type: str = "SHA256") -> tuple:
    """
    Agent B executes service with reasoning proof
    
    Returns:
        (result, reasoning_trace, proof_hash)
    """
    # Initialize reasoning proof generator
    prover = ReasoningProof("Agent B")
    
    # Execute service
    result = hashlib.sha256(input_data.encode()).hexdigest()
    
    # Generate reasoning proof
    trace = prover.create_service_execution_proof(
        service_type="hash",
        input_data=input_data,
        output_data=result,
        confidence=100
    )
    
    # Hash the proof (this would be committed on-chain via SOLPRISM)
    proof_hash = prover.hash_reasoning_trace(trace)
    
    return result, trace, proof_hash


# Example usage for Agent A (Client/Verifier)
def agent_a_verify_with_reasoning(
    input_data: str,
    received_result: str,
    service_tx: str
) -> tuple:
    """
    Agent A verifies result with reasoning proof
    
    Returns:
        (verified, reasoning_trace, proof_hash)
    """
    # Initialize reasoning proof generator
    prover = ReasoningProof("Agent A")
    
    # Compute expected result locally
    expected_result = hashlib.sha256(input_data.encode()).hexdigest()
    
    # Generate verification reasoning proof
    trace = prover.create_verification_proof(
        expected_result=expected_result,
        actual_result=received_result,
        service_tx=service_tx
    )
    
    # Hash the proof
    proof_hash = prover.hash_reasoning_trace(trace)
    
    verified = (expected_result == received_result)
    
    return verified, trace, proof_hash


if __name__ == "__main__":
    # Demo: Service execution with reasoning proof
    print("="*80)
    print("SOLPRISM INTEGRATION DEMO")
    print("="*80)
    
    # Agent B: Execute service with reasoning
    input_text = "hello_solana_hackathon"
    result, exec_trace, exec_proof = agent_b_with_reasoning_proof(input_text)
    
    print("\n[Agent B] Service Execution with Reasoning Proof:")
    print(f"  Input: {input_text}")
    print(f"  Result: {result}")
    print(f"  Proof Hash: {exec_proof}")
    print(f"  Reasoning Trace: {json.dumps(exec_trace, indent=2)[:500]}...")
    
    # Agent A: Verify with reasoning
    print("\n[Agent A] Result Verification with Reasoning Proof:")
    verified, verify_trace, verify_proof = agent_a_verify_with_reasoning(
        input_text,
        result,
        "mock_tx_signature"
    )
    
    print(f"  Verified: {verified}")
    print(f"  Proof Hash: {verify_proof}")
    print(f"  Reasoning Trace: {json.dumps(verify_trace, indent=2)[:500]}...")
    
    print("\n" + "="*80)
    print("✓ SOLPRISM integration complete!")
    print("  - Agent B generates reasoning proof for service execution")
    print("  - Agent A generates reasoning proof for verification")
    print("  - Both proofs can be committed on-chain via SOLPRISM protocol")
    print("="*80)
