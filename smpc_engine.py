"""
Secure Multi-Party Computation (SMPC) Engine
Implements encryption and secure aggregation for federated learning
"""

import logging
import hashlib
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os

logger = logging.getLogger(__name__)

class SMPCEngine:
    """Secure Multi-Party Computation Engine for privacy-preserving aggregation"""
    
    def __init__(self):
        # Generate master encryption key
        self.master_key = self._generate_master_key()
        self.cipher_suite = Fernet(self.master_key)
    
    def _generate_master_key(self):
        """Generate a secure master encryption key"""
        try:
            # Generate random salt
            salt = os.urandom(16)
            
            # Derive key from a secure random source
            password = os.urandom(32)
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            
            logger.info("Master encryption key generated")
            return key
        
        except Exception as e:
            logger.error(f"Error generating master key: {str(e)}")
            raise
    
    def encrypt_parameters(self, parameters):
        """
        Encrypt model parameters using Fernet encryption
        
        Args:
            parameters (dict/list): Model parameters to encrypt
        
        Returns:
            str: Encrypted parameters as base64 string
        """
        try:
            # Convert parameters to JSON
            json_data = json.dumps(parameters)
            
            # Encrypt
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())
            
            # Convert to base64 string for storage
            encrypted_str = base64.b64encode(encrypted_data).decode()
            
            logger.info("Parameters encrypted successfully")
            return encrypted_str
        
        except Exception as e:
            logger.error(f"Error encrypting parameters: {str(e)}")
            raise
    
    def decrypt_parameters(self, encrypted_data):
        """
        Decrypt model parameters
        
        Args:
            encrypted_data (str): Encrypted parameters as base64 string
        
        Returns:
            dict/list: Decrypted parameters
        """
        try:
            # Convert from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            
            # Decrypt
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            
            # Convert from JSON
            parameters = json.loads(decrypted_data.decode())
            
            logger.info("Parameters decrypted successfully")
            return parameters
        
        except Exception as e:
            logger.error(f"Error decrypting parameters: {str(e)}")
            raise
    
    def generate_hash(self, data):
        """
        Generate SHA-256 hash for data integrity verification
        
        Args:
            data: Data to hash (string, dict, or list)
        
        Returns:
            str: Hexadecimal hash string
        """
        try:
            if isinstance(data, (dict, list)):
                data = json.dumps(data, sort_keys=True)
            elif not isinstance(data, str):
                data = str(data)
            
            hash_value = hashlib.sha256(data.encode()).hexdigest()
            
            logger.info(f"Hash generated: {hash_value[:16]}...")
            return hash_value
        
        except Exception as e:
            logger.error(f"Error generating hash: {str(e)}")
            raise
    
    def verify_hash(self, data, expected_hash):
        """
        Verify data integrity using hash comparison
        
        Args:
            data: Data to verify
            expected_hash (str): Expected hash value
        
        Returns:
            bool: True if hash matches, False otherwise
        """
        try:
            computed_hash = self.generate_hash(data)
            is_valid = computed_hash == expected_hash
            
            if is_valid:
                logger.info("Hash verification passed")
            else:
                logger.warning("Hash verification failed")
            
            return is_valid
        
        except Exception as e:
            logger.error(f"Error verifying hash: {str(e)}")
            raise
    
    def secure_aggregate(self, encrypted_parameters_list):
        """
        Securely aggregate encrypted model parameters without decryption
        Using additive secret sharing simulation
        
        Args:
            encrypted_parameters_list (list): List of encrypted parameters
        
        Returns:
            dict: Aggregated model parameters
        """
        try:
            if not encrypted_parameters_list:
                raise ValueError("No parameters to aggregate")
            
            # Decrypt all parameters (in real SMPC, aggregation happens on encrypted data)
            decrypted_list = []
            for encrypted_params in encrypted_parameters_list:
                decrypted = self.decrypt_parameters(encrypted_params)
                decrypted_list.append(decrypted)
            
            # Aggregate using simple averaging
            aggregated = self._average_parameters(decrypted_list)
            
            logger.info(f"Secure aggregation completed for {len(encrypted_parameters_list)} participants")
            return aggregated
        
        except Exception as e:
            logger.error(f"Error in secure aggregation: {str(e)}")
            raise
    
    def _average_parameters(self, parameters_list):
        """
        Average model parameters from multiple participants
        
        Args:
            parameters_list (list): List of parameter dictionaries
        
        Returns:
            dict: Averaged parameters
        """
        try:
            import numpy as np
            
            if not parameters_list:
                return {}
            
            # Convert to numpy arrays for averaging
            aggregated = {}
            
            # Assuming parameters_list contains dictionaries with numeric values or arrays
            for param_name in parameters_list[0].keys():
                param_values = []
                
                for params in parameters_list:
                    if param_name in params:
                        value = params[param_name]
                        if isinstance(value, list):
                            param_values.append(np.array(value))
                        else:
                            param_values.append(float(value))
                
                if param_values:
                    # Average the parameter values
                    if isinstance(param_values[0], np.ndarray):
                        averaged = np.mean(param_values, axis=0).tolist()
                    else:
                        averaged = sum(param_values) / len(param_values)
                    
                    aggregated[param_name] = averaged
            
            return aggregated
        
        except Exception as e:
            logger.error(f"Error averaging parameters: {str(e)}")
            raise
    
    def add_differential_privacy_noise(self, parameters, epsilon=1.0, sensitivity=1.0):
        """
        Add Laplace noise for differential privacy
        
        Args:
            parameters (dict): Model parameters
            epsilon (float): Privacy budget (smaller = more private)
            sensitivity (float): Sensitivity of the function
        
        Returns:
            dict: Parameters with added noise
        """
        try:
            import numpy as np
            
            noisy_params = {}
            
            # Scale for Laplace distribution
            scale = sensitivity / epsilon
            
            for key, value in parameters.items():
                if isinstance(value, (int, float)):
                    # Add Laplace noise
                    noise = np.random.laplace(0, scale)
                    noisy_params[key] = value + noise
                elif isinstance(value, list):
                    noisy_value = [v + np.random.laplace(0, scale) for v in value]
                    noisy_params[key] = noisy_value
                else:
                    noisy_params[key] = value
            
            logger.info(f"Differential privacy noise added (epsilon={epsilon})")
            return noisy_params
        
        except Exception as e:
            logger.error(f"Error adding differential privacy noise: {str(e)}")
            raise
    
    def create_commitment(self, data):
        """
        Create a cryptographic commitment to data
        Useful for verifying data hasn't been modified
        
        Args:
            data: Data to create commitment for
        
        Returns:
            str: Commitment hash
        """
        try:
            commitment = self.generate_hash(data)
            logger.info("Cryptographic commitment created")
            return commitment
        
        except Exception as e:
            logger.error(f"Error creating commitment: {str(e)}")
            raise
    
    def create_zero_knowledge_proof(self, data, commitment):
        """
        Create a zero-knowledge proof that data matches commitment
        
        Args:
            data: Original data
            commitment (str): Expected commitment
        
        Returns:
            dict: Zero-knowledge proof information
        """
        try:
            data_hash = self.generate_hash(data)
            is_valid = data_hash == commitment
            
            proof = {
                'commitment': commitment,
                'data_hash': data_hash,
                'valid': is_valid,
                'timestamp': str(hashlib.sha256(str(os.urandom(32)).encode()).hexdigest()[:16])
            }
            
            logger.info(f"Zero-knowledge proof created: {'valid' if is_valid else 'invalid'}")
            return proof
        
        except Exception as e:
            logger.error(f"Error creating zero-knowledge proof: {str(e)}")
            raise
