import json
import random
import time

class LiquidationRadarMock:
    """
    Mock client for Liquidation-Radar API.
    Simulates cross-protocol health ratio monitoring.
    """
    
    def __init__(self, api_url="http://157.180.92.250:3003/api"):
        self.api_url = api_url

    def get_wallet_health(self, wallet_address):
        """
        Simulates GET /risk/:wallet
        Returns aggregated health ratio across Solana protocols.
        """
        # Mocking a realistic response from Liquidation-Radar
        health_ratio = round(random.uniform(1.1, 2.5), 2)
        status = "SAFE" if health_ratio > 1.2 else "DANGER"
        
        return {
            "wallet": wallet_address,
            "aggregatedHealthRatio": health_ratio,
            "status": status,
            "protocols": {
                "mango": {"health": round(health_ratio * 1.05, 2)},
                "drift": {"health": round(health_ratio * 0.95, 2)},
                "marginfi": {"health": round(health_ratio, 2)}
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

def demo_risk_aware_marketplace():
    radar = LiquidationRadarMock()
    
    print("="*80)
    print("🛡️ A2A MARKETPLACE: RISK-AWARE SERVICE DISCOVERY")
    print("="*80)
    
    # 1. Discovery
    target_agent = "3JqgszLcugbyj6YEWebaPXKuxYA5ZB8oH4zSgTkAEVmW" # Agent B
    print(f"\n[Step 1] Discovering Agent B: {target_agent}")
    
    # 2. Risk Assessment via Liquidation-Radar
    print(f"\n[Step 2] Querying Liquidation-Radar for Agent B's credit health...")
    risk_data = radar.get_wallet_health(target_agent)
    
    print(f"  Health Ratio: {risk_data['aggregatedHealthRatio']}")
    print(f"  Risk Status:  {risk_data['status']}")
    
    # 3. Decision Logic
    print(f"\n[Step 3] Decision Making (SOLPRISM Reasoning)")
    if risk_data['aggregatedHealthRatio'] > 1.3:
        print("  ✅ DECISION: Counterparty is solvent. Proceeding with contract.")
        print("  ✓ Reasoning trace generated for SOLPRISM.")
    else:
        print("  ❌ DECISION: High liquidation risk detected. Aborting transaction.")
        print("  ✓ Risk-based rejection proof generated.")

    print("\n" + "="*80)
    print("✨ INTEGRATION POTENTIAL: COMPOSABLE AGENT TRUST")
    print("="*80)

if __name__ == "__main__":
    demo_risk_aware_marketplace()
