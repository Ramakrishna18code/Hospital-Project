"""
Database Models for SecureHealth AI
SQLAlchemy ORM models for all database entities
"""

from app import db
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON

class User(db.Model):
    """User model for healthcare professionals"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    institution = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')  # user, admin
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    institution_rel = db.relationship('Institution', backref='user', lazy=True)
    training_sessions = db.relationship('TrainingSession', backref='user', lazy=True)
    model_updates = db.relationship('ModelUpdate', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'institution': self.institution,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


class Institution(db.Model):
    """Healthcare institution model"""
    __tablename__ = 'institutions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='pending_verification')  # pending_verification, verified, blocked
    verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    training_participants = db.relationship('TrainingSessionParticipant', backref='institution', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'created_at': self.created_at.isoformat()
        }


class TrainingSession(db.Model):
    """Federated learning training session"""
    __tablename__ = 'training_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    model_type = db.Column(db.String(100), nullable=False)  # random_forest, svm, neural_network, etc
    algorithm = db.Column(db.String(100), nullable=False)  # federated_averaging, fedavg, etc
    status = db.Column(db.String(50), default='initiated')  # initiated, training, aggregating, aggregated, completed
    round_number = db.Column(db.Integer, default=1)
    total_participants = db.Column(db.Integer, default=0)
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    global_model = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    model_updates = db.relationship('ModelUpdate', backref='training_session', lazy=True)
    participants = db.relationship('TrainingSessionParticipant', backref='training_session', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'model_type': self.model_type,
            'algorithm': self.algorithm,
            'status': self.status,
            'round_number': self.round_number,
            'total_participants': self.total_participants,
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ModelUpdate(db.Model):
    """Model update from healthcare institution"""
    __tablename__ = 'model_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    encrypted_parameters = db.Column(JSON, nullable=False)
    model_hash = db.Column(db.String(255), unique=True, nullable=False, index=True)
    status = db.Column(db.String(50), default='received')  # received, verified, aggregated, rejected
    accuracy = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'model_hash': self.model_hash,
            'status': self.status,
            'accuracy': self.accuracy,
            'created_at': self.created_at.isoformat()
        }


class BlockchainRecord(db.Model):
    """Blockchain ledger record for model updates"""
    __tablename__ = 'blockchain_records'
    
    id = db.Column(db.Integer, primary_key=True)
    model_update_id = db.Column(db.Integer, db.ForeignKey('model_updates.id'), nullable=False)
    transaction_hash = db.Column(db.String(255), unique=True, nullable=False, index=True)
    previous_hash = db.Column(db.String(255))
    block_number = db.Column(db.Integer, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='verified')  # verified, pending, rejected
    verification_count = db.Column(db.Integer, default=1)
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_hash': self.transaction_hash,
            'block_number': self.block_number,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'verification_count': self.verification_count
        }


class TrainingSessionParticipant(db.Model):
    """Participants in a training session"""
    __tablename__ = 'training_session_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'), nullable=False)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    status = db.Column(db.String(50), default='active')  # active, inactive, completed
    model_update_id = db.Column(db.Integer, db.ForeignKey('model_updates.id'))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'institution_id': self.institution_id,
            'status': self.status,
            'joined_at': self.joined_at.isoformat()
        }


class AnomalyRecord(db.Model):
    """Record of detected anomalies"""
    __tablename__ = 'anomaly_records'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    anomaly_type = db.Column(db.String(100), nullable=False)  # data_poisoning, model_inversion, etc
    severity = db.Column(db.String(50), default='low')  # low, medium, high, critical
    description = db.Column(db.Text)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'anomaly_type': self.anomaly_type,
            'severity': self.severity,
            'description': self.description,
            'detected_at': self.detected_at.isoformat(),
            'resolved': self.resolved
        }
