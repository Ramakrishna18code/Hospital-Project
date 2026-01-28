"""
Testing utilities and test data generators
"""

import random
import numpy as np
from datetime import datetime

class TestDataGenerator:
    """Generate test data for healthcare federated learning"""
    
    @staticmethod
    def generate_medical_data(n_samples=100, n_features=10):
        """
        Generate synthetic medical data
        
        Args:
            n_samples (int): Number of samples
            n_features (int): Number of features
        
        Returns:
            tuple: (features, labels)
        """
        X = np.random.rand(n_samples, n_features) * 100
        y = np.random.randint(0, 2, n_samples)
        
        return X.tolist(), y.tolist()
    
    @staticmethod
    def generate_model_parameters(n_params=50):
        """Generate random model parameters"""
        return {
            f'weight_{i}': random.uniform(-1, 1)
            for i in range(n_params)
        }
    
    @staticmethod
    def generate_user_data():
        """Generate test user data"""
        institutions = [
            "City Hospital",
            "Central Medical Center",
            "Regional Health Institute",
            "District Care Hospital",
            "Metropolitan Medical"
        ]
        
        return {
            "email": f"admin@{random.choice(institutions).replace(' ', '').lower()}.org",
            "password": "TestPassword123!",
            "institution": random.choice(institutions)
        }
    
    @staticmethod
    def generate_training_session_data():
        """Generate test training session data"""
        algorithms = [
            "federated_averaging",
            "fedprox",
            "momentum"
        ]
        
        models = [
            "random_forest",
            "svm",
            "neural_network"
        ]
        
        return {
            "model_type": random.choice(models),
            "algorithm": random.choice(algorithms)
        }


class APITestCase:
    """Base test case for API testing"""
    
    def __init__(self, client):
        self.client = client
    
    def register_user(self, email="test@hospital.org", password="Test123!", institution="Test Hospital"):
        """Register a test user"""
        response = self.client.post('/api/auth/register', json={
            'email': email,
            'password': password,
            'institution': institution
        })
        return response
    
    def login_user(self, email="test@hospital.org", password="Test123!"):
        """Login a test user"""
        response = self.client.post('/api/auth/login', json={
            'email': email,
            'password': password
        })
        return response
    
    def start_training(self, model_type="random_forest"):
        """Start a training session"""
        response = self.client.post('/api/fl/start-training', json={
            'model_type': model_type,
            'algorithm': 'federated_averaging'
        })
        return response
    
    def upload_model_update(self, session_id, parameters):
        """Upload a model update"""
        response = self.client.post('/api/fl/upload-model-update', json={
            'session_id': session_id,
            'model_parameters': parameters
        })
        return response
    
    def get_health_status(self):
        """Check API health"""
        response = self.client.get('/api/health')
        return response


# Test scenarios
TEST_SCENARIOS = {
    "complete_fl_workflow": {
        "description": "Complete federated learning workflow",
        "steps": [
            "Register institution",
            "Login user",
            "Start training session",
            "Train local model",
            "Upload encrypted model",
            "Aggregate models",
            "Verify on blockchain",
            "Get results"
        ]
    },
    "multi_institution_training": {
        "description": "Multiple institutions participating",
        "steps": [
            "Register institution 1",
            "Register institution 2",
            "Register institution 3",
            "Start training round",
            "Each institution trains locally",
            "Upload encrypted updates",
            "Aggregate from all participants",
            "Verify aggregation"
        ]
    },
    "anomaly_detection": {
        "description": "Detect anomalies in healthcare data",
        "steps": [
            "Prepare dataset",
            "Inject anomalies",
            "Run detection",
            "Verify detection rate"
        ]
    },
    "blockchain_verification": {
        "description": "Verify model updates on blockchain",
        "steps": [
            "Create model update",
            "Hash model",
            "Record on blockchain",
            "Verify hash",
            "Check chain integrity"
        ]
    }
}
