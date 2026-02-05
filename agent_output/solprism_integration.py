"""
SOLPRISM Integration for A2A Service Purchase Demo
Adds verifiable reasoning layer to agent decision-making

Based on community feedback from Mereum (@Mereum) in forum post #1239
"""

import hashlib
import json
from typing import Dict, Any, List
from datetime import datetime

def hash_reasoning_trace(trace: Dict[str, Any]) -> str:
    """Generate SHA256 hash of reasoning trace"""
    trace_json = json.dumps(trace, sort_keys=True)
    return hashlib.sha256(trace_json.encode()).hexdigest()

class ReasoningProof:
    """
    Generates verifiable reasoning proofs for agent actions
    Compatible with SOLPRISM protocol structure
    """
    
    def __init__(self, agent_name: str, action_type: str = "general"):
        self.agent_name = agent_name
        self.action_type = action_type
        self.version = "1.0.0"
        self.observations = []
        self.decision = {}
        self.execution_details = {}
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        
    def add_observation(self, observation: str):
        self.observations.append(observation)
        
    def set_decision(self, action_chosen: str, confidence: int = 100, risk: str = "low"):
        self.decision = {
            "actionChosen": action_chosen,
            "confidence": confidence,
            "riskAssessment": risk
        }
        
    def add_execution_detail(self, key: str, value: Any):
        self.execution_details[key] = value
        
    def generate_trace(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "agent": self.agent_name,
            "timestamp": self.timestamp,
            "action": {
                "type": self.action_type,
                "description": f"Agent {self.agent_name} performing {self.action_type}"
            },
            "inputs": {
                "context": "A2A service marketplace interaction"
            },
            "analysis": {
                "observations": self.observations,
                "logic": "Autonomous agent decision-making logic"
            },
            "decision": self.decision,
            "execution": self.execution_details
        }

# Helper functions for original demo compatibility
def agent_b_with_reasoning_proof(input_data: str, service_type: str = "SHA256") -> tuple:
    prover = ReasoningProof("Agent B", "service_execution")
    result = hashlib.sha256(input_data.encode()).hexdigest()
    
    prover.add_observation(f"Received request for {service_type}")
    prover.set_decision(f"Execute {service_type} and return result")
    prover.add_execution_detail("algorithm", service_type)
    prover.add_execution_detail("output", result)
    
    trace = prover.generate_trace()
    return result, trace, hash_reasoning_trace(trace)

def agent_a_verify_with_reasoning(input_data: str, received_result: str, service_tx: str) -> tuple:
    prover = ReasoningProof("Agent A", "result_verification")
    expected = hashlib.sha256(input_data.encode()).hexdigest()
    verified = (expected == received_result)
    
    prover.add_observation(f"Verifying result for tx {service_tx[:8]}...")
    prover.set_decision("Accept result" if verified else "Reject result")
    prover.add_execution_detail("verified", verified)
    
    trace = prover.generate_trace()
    return verified, trace, hash_reasoning_trace(trace)
