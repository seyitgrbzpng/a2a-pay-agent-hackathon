#!/bin/bash
################################################################################
# A2A Service Purchase Demo - Execution Script
# Single command to run the complete agent-to-agent interaction demo
################################################################################

set -e  # Exit on error

echo "================================================================================"
echo "  A2A SERVICE PURCHASE DEMO ON SOLANA DEVNET"
echo "  Autonomous Agent-to-Agent Interaction"
echo "================================================================================"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

echo "Checking dependencies..."
python3 -c "import solana; import solders" 2>/dev/null || {
    echo "Installing dependencies..."
    pip3 install --quiet solders solana anchorpy
}

echo "✓ Dependencies ready"
echo ""

# Run the demo
echo "Starting demo..."
echo ""
python3 agent_output/demo.py

echo ""
echo "================================================================================"
echo "  DEMO EXECUTION COMPLETE"
echo "================================================================================"
echo ""
echo "Generated files:"
echo "  - logs/agent_a_transactions.json (Agent A transaction log)"
echo "  - logs/agent_b_transactions.json (Agent B transaction log)"
echo "  - logs/demo_results.json (Demo results summary)"
echo "  - wallets/agent_a.json (Agent A wallet)"
echo "  - wallets/agent_b.json (Agent B wallet)"
echo ""
echo "All transactions are recorded on Solana devnet blockchain."
echo "View transactions on Solana Explorer: https://explorer.solana.com/?cluster=devnet"
echo ""
