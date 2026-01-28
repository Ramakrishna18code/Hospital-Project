"""
SecureHealth AI - Federated Learning Backend Server
Main Flask API Server for Healthcare Federated Learning System
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime
import logging

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'securehealth-ai-2024-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///securehealth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for frontend communication
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize database
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import modules
from models import User, Institution, TrainingSession, ModelUpdate, BlockchainRecord
from ml_engine import MLEngine
from federated_learning import FederatedLearningOrchestrator
from smpc_engine import SMPCEngine
from blockchain_ledger import BlockchainLedger

# Initialize engines
ml_engine = MLEngine()
fl_orchestrator = FederatedLearningOrchestrator()
smpc_engine = SMPCEngine()
blockchain_ledger = BlockchainLedger()

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new healthcare institution"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password') or not data.get('institution'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            institution=data['institution'],
            password_hash=generate_password_hash(data['password']),
            role='admin'
        )
        
        # Create institution
        institution = Institution(
            name=data['institution'],
            user_id=user.id,
            status='pending_verification'
        )
        
        db.session.add(user)
        db.session.add(institution)
        db.session.commit()
        
        logger.info(f"New institution registered: {data['institution']}")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful. Awaiting admin verification.',
            'user_id': user.id
        }), 201
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check institution status
        institution = Institution.query.filter_by(user_id=user.id).first()
        if institution and institution.status != 'verified':
            return jsonify({'error': 'Institution not verified yet'}), 403
        
        session['user_id'] = user.id
        session['email'] = user.email
        
        logger.info(f"User logged in: {user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user_id': user.id,
            'email': user.email,
            'institution': user.institution
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


# ============================================
# FEDERATED LEARNING ROUTES
# ============================================

@app.route('/api/fl/start-training', methods=['POST'])
def start_training():
    """Start a new federated learning training round"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        user = User.query.get(session['user_id'])
        
        # Create training session
        training_session = TrainingSession(
            user_id=user.id,
            model_type=data.get('model_type', 'random_forest'),
            algorithm=data.get('algorithm', 'federated_averaging'),
            status='initiated',
            round_number=1
        )
        
        db.session.add(training_session)
        db.session.commit()
        
        logger.info(f"Training session started: {training_session.id}")
        
        return jsonify({
            'success': True,
            'message': 'Training session started',
            'session_id': training_session.id,
            'status': 'initiated'
        }), 201
    
    except Exception as e:
        logger.error(f"Training start error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to start training'}), 500


@app.route('/api/fl/upload-model-update', methods=['POST'])
def upload_model_update():
    """Upload encrypted local model update"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        session_id = data.get('session_id')
        model_parameters = data.get('model_parameters')
        
        # Encrypt parameters using SMPC
        encrypted_params = smpc_engine.encrypt_parameters(model_parameters)
        
        # Generate hash for blockchain
        model_hash = smpc_engine.generate_hash(encrypted_params)
        
        # Create model update record
        model_update = ModelUpdate(
            session_id=session_id,
            user_id=session['user_id'],
            encrypted_parameters=encrypted_params,
            model_hash=model_hash,
            status='received'
        )
        
        db.session.add(model_update)
        db.session.commit()
        
        # Record on blockchain
        blockchain_record = BlockchainRecord(
            model_update_id=model_update.id,
            transaction_hash=model_hash,
            block_number=blockchain_ledger.get_next_block_number(),
            timestamp=datetime.utcnow(),
            status='verified'
        )
        
        db.session.add(blockchain_record)
        db.session.commit()
        
        logger.info(f"Model update received and verified: {model_hash}")
        
        return jsonify({
            'success': True,
            'message': 'Model update received and encrypted',
            'model_hash': model_hash,
            'update_id': model_update.id
        }), 201
    
    except Exception as e:
        logger.error(f"Model upload error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to upload model'}), 500


@app.route('/api/fl/aggregate-models', methods=['POST'])
def aggregate_models():
    """Aggregate models using SMPC"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        # Get all model updates for this session
        updates = ModelUpdate.query.filter_by(
            session_id=session_id,
            status='received'
        ).all()
        
        if not updates:
            return jsonify({'error': 'No model updates found'}), 404
        
        # Decrypt and aggregate using SMPC
        encrypted_params_list = [update.encrypted_parameters for update in updates]
        aggregated_model = smpc_engine.secure_aggregate(encrypted_params_list)
        
        # Update training session
        session_record = TrainingSession.query.get(session_id)
        session_record.global_model = aggregated_model
        session_record.status = 'aggregated'
        session_record.round_number += 1
        
        # Mark updates as aggregated
        for update in updates:
            update.status = 'aggregated'
        
        db.session.commit()
        
        logger.info(f"Models aggregated for session: {session_id}")
        
        return jsonify({
            'success': True,
            'message': 'Models aggregated successfully',
            'aggregated_model_hash': smpc_engine.generate_hash(aggregated_model),
            'round_number': session_record.round_number
        }), 200
    
    except Exception as e:
        logger.error(f"Aggregation error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Aggregation failed'}), 500


# ============================================
# ML MODEL ROUTES
# ============================================

@app.route('/api/ml/train-local-model', methods=['POST'])
def train_local_model():
    """Train a local machine learning model"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        training_data = data.get('training_data')
        labels = data.get('labels')
        algorithm = data.get('algorithm', 'random_forest')
        
        # Train model
        model = ml_engine.train_model(algorithm, training_data, labels)
        accuracy = ml_engine.evaluate_model(model, training_data, labels)
        
        logger.info(f"Local model trained with accuracy: {accuracy}")
        
        return jsonify({
            'success': True,
            'message': 'Local model trained successfully',
            'accuracy': accuracy,
            'algorithm': algorithm,
            'model_type': type(model).__name__
        }), 201
    
    except Exception as e:
        logger.error(f"Model training error: {str(e)}")
        return jsonify({'error': 'Model training failed'}), 500


@app.route('/api/ml/detect-anomalies', methods=['POST'])
def detect_anomalies():
    """Detect anomalies in healthcare data"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        dataset = data.get('dataset')
        
        # Detect anomalies
        anomalies = ml_engine.detect_anomalies(dataset)
        anomaly_count = len(anomalies)
        anomaly_percentage = (anomaly_count / len(dataset)) * 100 if dataset else 0
        
        logger.info(f"Anomalies detected: {anomaly_count}/{len(dataset)}")
        
        return jsonify({
            'success': True,
            'message': 'Anomaly detection completed',
            'anomaly_count': anomaly_count,
            'total_samples': len(dataset),
            'anomaly_percentage': round(anomaly_percentage, 2),
            'anomalies': anomalies[:10]  # Return first 10
        }), 200
    
    except Exception as e:
        logger.error(f"Anomaly detection error: {str(e)}")
        return jsonify({'error': 'Anomaly detection failed'}), 500


# ============================================
# BLOCKCHAIN ROUTES
# ============================================

@app.route('/api/blockchain/verify-update', methods=['POST'])
def verify_blockchain_update():
    """Verify model update on blockchain"""
    try:
        data = request.get_json()
        model_hash = data.get('model_hash')
        
        # Verify in blockchain
        is_verified = blockchain_ledger.verify_hash(model_hash)
        
        record = BlockchainRecord.query.filter_by(transaction_hash=model_hash).first()
        
        return jsonify({
            'success': True,
            'message': 'Blockchain verification complete',
            'model_hash': model_hash,
            'is_verified': is_verified,
            'block_number': record.block_number if record else None,
            'timestamp': record.timestamp.isoformat() if record else None
        }), 200
    
    except Exception as e:
        logger.error(f"Blockchain verification error: {str(e)}")
        return jsonify({'error': 'Verification failed'}), 500


@app.route('/api/blockchain/get-ledger', methods=['GET'])
def get_blockchain_ledger():
    """Get blockchain ledger records"""
    try:
        records = BlockchainRecord.query.order_by(BlockchainRecord.block_number.desc()).limit(50).all()
        
        ledger_data = [{
            'block_number': r.block_number,
            'transaction_hash': r.transaction_hash,
            'timestamp': r.timestamp.isoformat(),
            'status': r.status
        } for r in records]
        
        return jsonify({
            'success': True,
            'message': 'Blockchain ledger retrieved',
            'total_blocks': len(ledger_data),
            'ledger': ledger_data
        }), 200
    
    except Exception as e:
        logger.error(f"Ledger retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve ledger'}), 500


# ============================================
# ADMIN ROUTES
# ============================================

@app.route('/api/admin/verify-institution', methods=['POST'])
def verify_institution():
    """Admin: Verify healthcare institution"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get(session['user_id'])
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        institution_id = data.get('institution_id')
        
        institution = Institution.query.get(institution_id)
        if not institution:
            return jsonify({'error': 'Institution not found'}), 404
        
        institution.status = 'verified'
        institution.verified_at = datetime.utcnow()
        
        # Activate associated user
        user_to_verify = User.query.get(institution.user_id)
        user_to_verify.is_active = True
        
        db.session.commit()
        
        logger.info(f"Institution verified: {institution.name}")
        
        return jsonify({
            'success': True,
            'message': 'Institution verified successfully',
            'institution': institution.name
        }), 200
    
    except Exception as e:
        logger.error(f"Institution verification error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Verification failed'}), 500


@app.route('/api/admin/get-training-status', methods=['GET'])
def get_training_status():
    """Admin: Get training session status"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get(session['user_id'])
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        sessions = TrainingSession.query.all()
        
        status_data = [{
            'session_id': s.id,
            'status': s.status,
            'round_number': s.round_number,
            'algorithm': s.algorithm,
            'created_at': s.created_at.isoformat()
        } for s in sessions]
        
        return jsonify({
            'success': True,
            'message': 'Training sessions retrieved',
            'total_sessions': len(status_data),
            'sessions': status_data
        }), 200
    
    except Exception as e:
        logger.error(f"Status retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve status'}), 500


# ============================================
# DASHBOARD ROUTES
# ============================================

@app.route('/api/dashboard/statistics', methods=['GET'])
def get_dashboard_statistics():
    """Get dashboard statistics"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user_id = session['user_id']
        
        # Count statistics
        total_training_sessions = TrainingSession.query.filter_by(user_id=user_id).count()
        total_model_updates = ModelUpdate.query.filter_by(user_id=user_id).count()
        completed_trainings = TrainingSession.query.filter_by(user_id=user_id, status='completed').count()
        
        # Get average accuracy
        sessions = TrainingSession.query.filter_by(user_id=user_id).all()
        avg_accuracy = sum(s.accuracy for s in sessions if s.accuracy) / len(sessions) if sessions else 0
        
        return jsonify({
            'success': True,
            'message': 'Dashboard statistics retrieved',
            'statistics': {
                'total_training_sessions': total_training_sessions,
                'total_model_updates': total_model_updates,
                'completed_trainings': completed_trainings,
                'average_accuracy': round(avg_accuracy, 2)
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Dashboard statistics error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500


# ============================================
# HEALTH CHECK ROUTE
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'SecureHealth AI - Federated Learning Backend'
    }), 200


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")
    
    logger.info("Starting SecureHealth AI - Federated Learning Backend")
    app.run(debug=True, host='0.0.0.0', port=5000)
