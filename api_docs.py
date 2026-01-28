"""
API Documentation and Endpoints Reference
"""

API_DOCUMENTATION = {
    "title": "SecureHealth AI - Federated Learning Backend API",
    "version": "1.0.0",
    "description": "Privacy-preserving federated learning system for healthcare",
    
    "authentication": {
        "/api/auth/register": {
            "method": "POST",
            "description": "Register a new healthcare institution",
            "request_body": {
                "email": "admin@hospital.org",
                "password": "secure_password",
                "institution": "Hospital Name"
            },
            "response": {
                "success": True,
                "message": "Registration successful",
                "user_id": 1
            },
            "status_codes": [201, 400, 500]
        },
        "/api/auth/login": {
            "method": "POST",
            "description": "User login",
            "request_body": {
                "email": "admin@hospital.org",
                "password": "secure_password"
            },
            "response": {
                "success": True,
                "message": "Login successful",
                "user_id": 1,
                "email": "admin@hospital.org"
            },
            "status_codes": [200, 401, 403]
        },
        "/api/auth/logout": {
            "method": "POST",
            "description": "User logout",
            "response": {
                "success": True,
                "message": "Logged out successfully"
            },
            "status_codes": [200]
        }
    },
    
    "federated_learning": {
        "/api/fl/start-training": {
            "method": "POST",
            "description": "Start a new federated learning training round",
            "authentication_required": True,
            "request_body": {
                "model_type": "random_forest",
                "algorithm": "federated_averaging"
            },
            "response": {
                "success": True,
                "session_id": 1,
                "status": "initiated"
            },
            "status_codes": [201, 401, 500]
        },
        "/api/fl/upload-model-update": {
            "method": "POST",
            "description": "Upload encrypted local model update",
            "authentication_required": True,
            "request_body": {
                "session_id": 1,
                "model_parameters": {"weights": [0.1, 0.2, 0.3]}
            },
            "response": {
                "success": True,
                "model_hash": "abc123def456...",
                "update_id": 1
            },
            "status_codes": [201, 401, 500]
        },
        "/api/fl/aggregate-models": {
            "method": "POST",
            "description": "Aggregate models using SMPC",
            "authentication_required": True,
            "request_body": {
                "session_id": 1
            },
            "response": {
                "success": True,
                "aggregated_model_hash": "xyz789abc...",
                "round_number": 2
            },
            "status_codes": [200, 401, 404, 500]
        }
    },
    
    "machine_learning": {
        "/api/ml/train-local-model": {
            "method": "POST",
            "description": "Train a local machine learning model",
            "authentication_required": True,
            "request_body": {
                "training_data": [[1, 2, 3], [4, 5, 6]],
                "labels": [0, 1],
                "algorithm": "random_forest"
            },
            "response": {
                "success": True,
                "accuracy": 0.95,
                "algorithm": "random_forest"
            },
            "status_codes": [201, 401, 500]
        },
        "/api/ml/detect-anomalies": {
            "method": "POST",
            "description": "Detect anomalies in healthcare data",
            "authentication_required": True,
            "request_body": {
                "dataset": [[1, 2, 3], [4, 5, 100], [7, 8, 9]]
            },
            "response": {
                "success": True,
                "anomaly_count": 1,
                "anomaly_percentage": 33.33,
                "anomalies": [
                    {
                        "index": 1,
                        "anomaly_score": -0.85,
                        "severity": "high"
                    }
                ]
            },
            "status_codes": [200, 401, 500]
        }
    },
    
    "blockchain": {
        "/api/blockchain/verify-update": {
            "method": "POST",
            "description": "Verify model update on blockchain",
            "request_body": {
                "model_hash": "abc123def456..."
            },
            "response": {
                "success": True,
                "is_verified": True,
                "block_number": 5,
                "timestamp": "2024-01-28T10:30:00"
            },
            "status_codes": [200, 500]
        },
        "/api/blockchain/get-ledger": {
            "method": "GET",
            "description": "Get blockchain ledger records",
            "response": {
                "success": True,
                "total_blocks": 10,
                "ledger": [
                    {
                        "block_number": 10,
                        "transaction_hash": "xyz789...",
                        "timestamp": "2024-01-28T10:30:00",
                        "status": "verified"
                    }
                ]
            },
            "status_codes": [200, 500]
        }
    },
    
    "admin": {
        "/api/admin/verify-institution": {
            "method": "POST",
            "description": "Admin: Verify healthcare institution",
            "authentication_required": True,
            "admin_required": True,
            "request_body": {
                "institution_id": 1
            },
            "response": {
                "success": True,
                "institution": "Hospital Name"
            },
            "status_codes": [200, 403, 404, 500]
        },
        "/api/admin/get-training-status": {
            "method": "GET",
            "description": "Admin: Get training session status",
            "authentication_required": True,
            "admin_required": True,
            "response": {
                "success": True,
                "total_sessions": 5,
                "sessions": [
                    {
                        "session_id": 1,
                        "status": "aggregated",
                        "round_number": 2,
                        "algorithm": "federated_averaging"
                    }
                ]
            },
            "status_codes": [200, 403, 500]
        }
    },
    
    "dashboard": {
        "/api/dashboard/statistics": {
            "method": "GET",
            "description": "Get dashboard statistics",
            "authentication_required": True,
            "response": {
                "success": True,
                "statistics": {
                    "total_training_sessions": 5,
                    "total_model_updates": 15,
                    "completed_trainings": 3,
                    "average_accuracy": 0.92
                }
            },
            "status_codes": [200, 401, 500]
        }
    },
    
    "health": {
        "/api/health": {
            "method": "GET",
            "description": "Health check endpoint",
            "response": {
                "status": "healthy",
                "timestamp": "2024-01-28T10:30:00",
                "service": "SecureHealth AI - Federated Learning Backend"
            },
            "status_codes": [200]
        }
    },
    
    "status_codes": {
        "200": "OK - Request successful",
        "201": "Created - Resource created successfully",
        "400": "Bad Request - Invalid input",
        "401": "Unauthorized - Authentication required",
        "403": "Forbidden - Access denied",
        "404": "Not Found - Resource not found",
        "429": "Too Many Requests - Rate limit exceeded",
        "500": "Internal Server Error"
    }
}

def get_api_docs():
    """Return API documentation"""
    return API_DOCUMENTATION
