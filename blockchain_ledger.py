"""
Blockchain Ledger for Model Verification
Implements a simple blockchain for recording and verifying model updates
"""

import logging
import hashlib
import json
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

class BlockchainLedger:
    """Blockchain ledger for immutable model update records"""
    
    def __init__(self):
        self.chain: List[Dict] = []
        self.pending_transactions: List[Dict] = []
        self.difficulty = 2  # For proof of work
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """Create the genesis (first) block"""
        try:
            genesis_block = {
                'block_number': 0,
                'timestamp': datetime.utcnow().isoformat(),
                'transactions': [],
                'previous_hash': '0',
                'hash': None,
                'nonce': 0
            }
            
            genesis_block['hash'] = self._calculate_hash(genesis_block)
            self.chain.append(genesis_block)
            
            logger.info("Genesis block created")
        
        except Exception as e:
            logger.error(f"Error creating genesis block: {str(e)}")
            raise
    
    def _calculate_hash(self, block: Dict) -> str:
        """
        Calculate SHA-256 hash of a block
        
        Args:
            block (dict): Block to hash
        
        Returns:
            str: Hexadecimal hash
        """
        try:
            # Create a copy and remove hash for calculation
            block_copy = block.copy()
            block_copy.pop('hash', None)
            
            block_string = json.dumps(block_copy, sort_keys=True, default=str)
            return hashlib.sha256(block_string.encode()).hexdigest()
        
        except Exception as e:
            logger.error(f"Error calculating hash: {str(e)}")
            raise
    
    def add_transaction(self, model_hash: str, user_id: int, institution: str) -> Dict:
        """
        Add a transaction (model update) to pending transactions
        
        Args:
            model_hash (str): Hash of the model update
            user_id (int): ID of the user submitting
            institution (str): Institution name
        
        Returns:
            dict: Transaction information
        """
        try:
            transaction = {
                'model_hash': model_hash,
                'user_id': user_id,
                'institution': institution,
                'timestamp': datetime.utcnow().isoformat(),
                'transaction_hash': self._calculate_transaction_hash(model_hash, user_id)
            }
            
            self.pending_transactions.append(transaction)
            
            logger.info(f"Transaction added: {model_hash[:16]}...")
            return transaction
        
        except Exception as e:
            logger.error(f"Error adding transaction: {str(e)}")
            raise
    
    def _calculate_transaction_hash(self, model_hash: str, user_id: int) -> str:
        """Calculate hash for a transaction"""
        transaction_data = f"{model_hash}{user_id}{datetime.utcnow().isoformat()}"
        return hashlib.sha256(transaction_data.encode()).hexdigest()
    
    def mine_block(self) -> Dict:
        """
        Mine a new block with pending transactions
        
        Returns:
            dict: The newly mined block
        """
        try:
            if not self.pending_transactions:
                logger.warning("No pending transactions to mine")
                return None
            
            last_block = self.chain[-1]
            
            new_block = {
                'block_number': len(self.chain),
                'timestamp': datetime.utcnow().isoformat(),
                'transactions': self.pending_transactions.copy(),
                'previous_hash': last_block['hash'],
                'hash': None,
                'nonce': 0
            }
            
            # Proof of work
            new_block['hash'] = self._proof_of_work(new_block)
            
            # Add block to chain
            self.chain.append(new_block)
            
            # Clear pending transactions
            self.pending_transactions = []
            
            logger.info(f"Block {new_block['block_number']} mined successfully")
            return new_block
        
        except Exception as e:
            logger.error(f"Error mining block: {str(e)}")
            raise
    
    def _proof_of_work(self, block: Dict) -> str:
        """
        Find a hash with required number of leading zeros (simplified proof of work)
        
        Args:
            block (dict): Block to solve
        
        Returns:
            str: Valid hash meeting difficulty requirement
        """
        try:
            block_copy = block.copy()
            block_copy.pop('hash', None)
            
            nonce = 0
            hash_value = self._calculate_hash(block)
            
            while not hash_value.startswith('0' * self.difficulty):
                nonce += 1
                block_copy['nonce'] = nonce
                hash_value = self._calculate_hash(block_copy)
            
            return hash_value
        
        except Exception as e:
            logger.error(f"Error in proof of work: {str(e)}")
            raise
    
    def verify_hash(self, model_hash: str) -> bool:
        """
        Verify if a model hash exists in the blockchain
        
        Args:
            model_hash (str): Model hash to verify
        
        Returns:
            bool: True if hash is found and verified
        """
        try:
            for block in self.chain:
                for transaction in block['transactions']:
                    if transaction['model_hash'] == model_hash:
                        # Verify block integrity
                        if self._verify_block_integrity(block):
                            logger.info(f"Hash verified: {model_hash[:16]}...")
                            return True
            
            logger.warning(f"Hash not found or verification failed: {model_hash[:16]}...")
            return False
        
        except Exception as e:
            logger.error(f"Error verifying hash: {str(e)}")
            raise
    
    def _verify_block_integrity(self, block: Dict) -> bool:
        """Verify that a block hasn't been tampered with"""
        try:
            block_copy = block.copy()
            hash_to_verify = block_copy.pop('hash', None)
            calculated_hash = self._calculate_hash(block_copy)
            
            return hash_to_verify == calculated_hash
        
        except Exception as e:
            logger.error(f"Error verifying block integrity: {str(e)}")
            return False
    
    def verify_chain_integrity(self) -> Dict:
        """
        Verify the entire blockchain integrity
        
        Returns:
            dict: Verification results
        """
        try:
            results = {
                'valid': True,
                'total_blocks': len(self.chain),
                'invalid_blocks': [],
                'broken_links': []
            }
            
            for i in range(1, len(self.chain)):
                current_block = self.chain[i]
                previous_block = self.chain[i - 1]
                
                # Verify block integrity
                if not self._verify_block_integrity(current_block):
                    results['valid'] = False
                    results['invalid_blocks'].append(i)
                
                # Verify chain link
                if current_block['previous_hash'] != previous_block['hash']:
                    results['valid'] = False
                    results['broken_links'].append(i)
            
            if results['valid']:
                logger.info("Blockchain integrity verified successfully")
            else:
                logger.warning(f"Blockchain integrity issues found: {results}")
            
            return results
        
        except Exception as e:
            logger.error(f"Error verifying chain integrity: {str(e)}")
            raise
    
    def get_transaction_history(self, model_hash: str) -> List[Dict]:
        """
        Get history of a model hash in the blockchain
        
        Args:
            model_hash (str): Model hash to search for
        
        Returns:
            list: List of blocks containing this hash
        """
        try:
            history = []
            
            for block in self.chain:
                for transaction in block['transactions']:
                    if transaction['model_hash'] == model_hash:
                        history.append({
                            'block_number': block['block_number'],
                            'block_hash': block['hash'],
                            'timestamp': block['timestamp'],
                            'transaction': transaction
                        })
            
            logger.info(f"Transaction history retrieved: {len(history)} records")
            return history
        
        except Exception as e:
            logger.error(f"Error retrieving transaction history: {str(e)}")
            raise
    
    def get_block(self, block_number: int) -> Dict:
        """
        Get a specific block from the blockchain
        
        Args:
            block_number (int): Block number to retrieve
        
        Returns:
            dict: Block data
        """
        try:
            if block_number < len(self.chain):
                return self.chain[block_number]
            else:
                logger.warning(f"Block {block_number} not found")
                return None
        
        except Exception as e:
            logger.error(f"Error getting block: {str(e)}")
            raise
    
    def get_ledger_summary(self) -> Dict:
        """
        Get a summary of the blockchain
        
        Returns:
            dict: Blockchain summary
        """
        try:
            total_transactions = sum(len(block['transactions']) for block in self.chain)
            
            summary = {
                'total_blocks': len(self.chain),
                'total_transactions': total_transactions,
                'pending_transactions': len(self.pending_transactions),
                'chain_valid': self.verify_chain_integrity()['valid'],
                'latest_block': self.chain[-1] if self.chain else None
            }
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting ledger summary: {str(e)}")
            raise
    
    def get_next_block_number(self) -> int:
        """Get the next block number to be mined"""
        return len(self.chain)
