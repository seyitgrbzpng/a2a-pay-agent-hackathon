#!/usr/bin/env python3
"""
Shared utilities for Agent A and Agent B
Handles wallet management, transaction helpers, and memo operations
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.system_program import transfer, TransferParams
from solders.transaction import VersionedTransaction
from solders.message import MessageV0


class WalletManager:
    """Manages wallet creation, loading, and saving"""
    
    def __init__(self, wallet_path: str):
        self.wallet_path = Path(wallet_path)
        self.keypair: Optional[Keypair] = None
    
    def create_or_load(self) -> Keypair:
        """Create new wallet or load existing one"""
        if self.wallet_path.exists():
            print(f"Loading existing wallet from {self.wallet_path}")
            with open(self.wallet_path, 'r') as f:
                data = json.load(f)
                self.keypair = Keypair.from_bytes(bytes(data['secret_key']))
        else:
            print(f"Creating new wallet at {self.wallet_path}")
            self.keypair = Keypair()
            self._save()
        
        print(f"Wallet address: {self.keypair.pubkey()}")
        return self.keypair
    
    def _save(self):
        """Save wallet to file"""
        self.wallet_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.wallet_path, 'w') as f:
            json.dump({
                'public_key': str(self.keypair.pubkey()),
                'secret_key': list(bytes(self.keypair))
            }, f, indent=2)
        print(f"Wallet saved to {self.wallet_path}")


class SolanaClient:
    """Wrapper for Solana RPC client with helper methods"""
    
    # Memo Program ID (official Solana Memo Program)
    MEMO_PROGRAM_ID = Pubkey.from_string("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr")
    
    def __init__(self, rpc_url: str = "https://api.devnet.solana.com"):
        self.rpc_url = rpc_url
        self.client = AsyncClient(rpc_url)
    
    async def get_balance(self, pubkey: Pubkey) -> float:
        """Get SOL balance in SOL (not lamports)"""
        response = await self.client.get_balance(pubkey, commitment=Confirmed)
        lamports = response.value
        return lamports / 1_000_000_000
    
    async def request_airdrop(self, pubkey: Pubkey, amount_sol: float = 2.0, max_retries: int = 5) -> str:
        """Request devnet SOL airdrop with retry logic"""
        import asyncio
        
        for attempt in range(max_retries):
            try:
                print(f"Requesting {amount_sol} SOL airdrop (attempt {attempt + 1}/{max_retries})...")
                lamports = int(amount_sol * 1_000_000_000)
                response = await self.client.request_airdrop(pubkey, lamports)
                
                if response.value:
                    print(f"Airdrop requested. Signature: {response.value}")
                    # Wait for confirmation
                    await self.client.confirm_transaction(response.value, commitment=Confirmed)
                    print("Airdrop confirmed!")
                    return str(response.value)
            except Exception as e:
                print(f"Airdrop attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4, 8, 16 seconds
                    print(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    print("All airdrop attempts failed. Continuing with current balance...")
                    raise Exception("Airdrop failed after all retries")
    
    async def send_transaction_with_memo(
        self,
        sender: Keypair,
        recipient: Pubkey,
        amount_sol: float,
        memo: str
    ) -> Tuple[str, str]:
        """
        Send SOL with a memo attached
        Returns: (transaction_signature, memo_content)
        """
        print(f"\nSending {amount_sol} SOL to {recipient}")
        print(f"Memo: {memo}")
        
        # Get latest blockhash
        latest_blockhash = await self.client.get_latest_blockhash()
        
        # Create transfer instruction
        lamports = int(amount_sol * 1_000_000_000)
        transfer_ix = transfer(
            TransferParams(
                from_pubkey=sender.pubkey(),
                to_pubkey=recipient,
                lamports=lamports
            )
        )
        
        # Create memo instruction
        memo_ix = self._create_memo_instruction(sender.pubkey(), memo)
        
        # Create message with both instructions
        message = MessageV0.try_compile(
            payer=sender.pubkey(),
            instructions=[transfer_ix, memo_ix],
            address_lookup_table_accounts=[],
            recent_blockhash=latest_blockhash.value.blockhash
        )
        
        # Create and sign transaction
        transaction = VersionedTransaction(message, [sender])
        
        # Send transaction
        response = await self.client.send_transaction(transaction)
        signature = str(response.value)
        
        print(f"Transaction sent. Signature: {signature}")
        
        # Wait for confirmation
        await self.client.confirm_transaction(response.value, commitment=Confirmed)
        print("Transaction confirmed!")
        
        return signature, memo
    
    async def send_memo_only(self, sender: Keypair, memo: str) -> str:
        """
        Send a memo-only transaction (no transfer)
        Useful for publishing proofs
        """
        print(f"\nPublishing memo: {memo}")
        
        # Get latest blockhash
        latest_blockhash = await self.client.get_latest_blockhash()
        
        # Create memo instruction
        memo_ix = self._create_memo_instruction(sender.pubkey(), memo)
        
        # Create message with memo instruction only
        message = MessageV0.try_compile(
            payer=sender.pubkey(),
            instructions=[memo_ix],
            address_lookup_table_accounts=[],
            recent_blockhash=latest_blockhash.value.blockhash
        )
        
        # Create and sign transaction
        transaction = VersionedTransaction(message, [sender])
        
        # Send transaction
        response = await self.client.send_transaction(transaction)
        signature = str(response.value)
        
        print(f"Memo published. Signature: {signature}")
        
        # Wait for confirmation
        await self.client.confirm_transaction(response.value, commitment=Confirmed)
        print("Memo transaction confirmed!")
        
        return signature
    
    def _create_memo_instruction(self, signer: Pubkey, memo: str):
        """Create a memo instruction"""
        from solders.instruction import Instruction, AccountMeta
        
        memo_bytes = memo.encode('utf-8')
        
        return Instruction(
            program_id=self.MEMO_PROGRAM_ID,
            data=memo_bytes,
            accounts=[AccountMeta(pubkey=signer, is_signer=True, is_writable=False)]
        )
    
    async def get_transaction_memo(self, signature: str) -> Optional[str]:
        """
        Retrieve memo from a transaction
        Returns the memo string if found, None otherwise
        """
        try:
            response = await self.client.get_transaction(
                signature,
                encoding="jsonParsed",
                commitment=Confirmed,
                max_supported_transaction_version=0
            )
            
            if response.value and response.value.transaction:
                tx = response.value.transaction
                if hasattr(tx, 'message') and hasattr(tx.message, 'instructions'):
                    for ix in tx.message.instructions:
                        # Check if this is a memo instruction
                        if hasattr(ix, 'program_id'):
                            if str(ix.program_id) == str(self.MEMO_PROGRAM_ID):
                                if hasattr(ix, 'data'):
                                    # Data is the memo text
                                    return ix.data.decode('utf-8') if isinstance(ix.data, bytes) else ix.data
            return None
        except Exception as e:
            print(f"Error retrieving transaction memo: {e}")
            return None
    
    async def close(self):
        """Close the RPC client"""
        await self.client.close()


class ServiceProvider:
    """Service execution utilities"""
    
    @staticmethod
    def compute_sha256(text: str) -> str:
        """Compute SHA256 hash of text"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def parse_service_request(memo: str) -> Optional[dict]:
        """
        Parse service request from memo
        Format: REQUEST:service_type:input_data
        Example: REQUEST:hash:hello_world
        """
        try:
            parts = memo.split(':', 2)
            if len(parts) == 3 and parts[0] == 'REQUEST':
                return {
                    'type': parts[1],
                    'input': parts[2]
                }
        except Exception as e:
            print(f"Error parsing service request: {e}")
        return None
    
    @staticmethod
    def create_service_response(service_type: str, result: str) -> str:
        """
        Create service response memo
        Format: RESPONSE:service_type:result
        """
        return f"RESPONSE:{service_type}:{result}"
    
    @staticmethod
    def create_verification_proof(tx_signature: str, verified: bool) -> str:
        """
        Create verification proof memo
        Format: PROOF:status:tx_signature
        """
        status = "verified" if verified else "failed"
        return f"PROOF:{status}:{tx_signature}"


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)
