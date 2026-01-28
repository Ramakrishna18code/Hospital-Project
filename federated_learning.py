"""
Federated Learning Orchestrator
Manages federated learning rounds and coordinates between institutions
"""

import logging
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

class FederatedLearningOrchestrator:
    """Orchestrates federated learning training rounds"""
    
    def __init__(self):
        self.current_round = 0
        self.participants = {}
        self.global_model = None
        self.training_history = []
    
    def initialize_round(self, round_number, algorithm='federated_averaging'):
        """
        Initialize a new federated learning round
        
        Args:
            round_number (int): Current round number
            algorithm (str): FL algorithm (federated_averaging, fedprox, etc)
        
        Returns:
            dict: Round initialization info
        """
        try:
            self.current_round = round_number
            
            round_info = {
                'round_number': round_number,
                'algorithm': algorithm,
                'status': 'initialized',
                'timestamp': datetime.utcnow().isoformat(),
                'participants': len(self.participants)
            }
            
            logger.info(f"Federated learning round {round_number} initialized")
            return round_info
        
        except Exception as e:
            logger.error(f"Error initializing round: {str(e)}")
            raise
    
    def register_participant(self, participant_id, institution_name):
        """
        Register a healthcare institution as FL participant
        
        Args:
            participant_id (str): Unique participant identifier
            institution_name (str): Name of institution
        
        Returns:
            dict: Participant registration info
        """
        try:
            if participant_id in self.participants:
                logger.warning(f"Participant {participant_id} already registered")
                return {'status': 'already_registered'}
            
            self.participants[participant_id] = {
                'institution': institution_name,
                'status': 'active',
                'registered_at': datetime.utcnow().isoformat(),
                'rounds_participated': 0,
                'model_updates_submitted': 0
            }
            
            logger.info(f"Participant registered: {participant_id} ({institution_name})")
            return {
                'status': 'success',
                'participant_id': participant_id,
                'message': 'Participant registered successfully'
            }
        
        except Exception as e:
            logger.error(f"Error registering participant: {str(e)}")
            raise
    
    def federated_averaging(self, model_weights_list, weights=None):
        """
        Federated Averaging algorithm - simple averaging of model weights
        
        Args:
            model_weights_list (list): List of model weights from participants
            weights (list): Optional weights for each participant
        
        Returns:
            array: Averaged global model weights
        """
        try:
            if not model_weights_list:
                raise ValueError("No model weights provided")
            
            model_weights_array = np.array(model_weights_list)
            
            if weights is None:
                # Simple average
                global_weights = np.mean(model_weights_array, axis=0)
            else:
                # Weighted average
                weights = np.array(weights)
                weights = weights / weights.sum()  # Normalize weights
                global_weights = np.average(model_weights_array, axis=0, weights=weights)
            
            logger.info(f"Federated averaging completed for {len(model_weights_list)} participants")
            return global_weights.tolist()
        
        except Exception as e:
            logger.error(f"Error in federated averaging: {str(e)}")
            raise
    
    def weighted_averaging(self, model_weights_list, data_sizes):
        """
        Weighted Federated Averaging based on local dataset sizes
        
        Args:
            model_weights_list (list): List of model weights
            data_sizes (list): Number of samples per participant
        
        Returns:
            array: Weighted averaged global model
        """
        try:
            total_size = sum(data_sizes)
            weights = [size / total_size for size in data_sizes]
            
            global_model = self.federated_averaging(model_weights_list, weights)
            
            logger.info(f"Weighted averaging completed with sizes: {data_sizes}")
            return global_model
        
        except Exception as e:
            logger.error(f"Error in weighted averaging: {str(e)}")
            raise
    
    def update_participant_stats(self, participant_id, accuracy):
        """
        Update participant statistics after local training
        
        Args:
            participant_id (str): Participant identifier
            accuracy (float): Local model accuracy
        
        Returns:
            dict: Updated participant info
        """
        try:
            if participant_id not in self.participants:
                raise ValueError(f"Participant {participant_id} not found")
            
            participant = self.participants[participant_id]
            participant['rounds_participated'] += 1
            participant['model_updates_submitted'] += 1
            participant['last_accuracy'] = accuracy
            participant['last_update'] = datetime.utcnow().isoformat()
            
            logger.info(f"Participant {participant_id} updated: Accuracy={accuracy}")
            return participant
        
        except Exception as e:
            logger.error(f"Error updating participant stats: {str(e)}")
            raise
    
    def check_convergence(self, accuracy_history, threshold=0.01, patience=3):
        """
        Check if model has converged
        
        Args:
            accuracy_history (list): List of accuracy scores
            threshold (float): Minimum improvement threshold
            patience (int): Number of rounds without improvement before stopping
        
        Returns:
            dict: Convergence status
        """
        try:
            if len(accuracy_history) < patience:
                return {'converged': False, 'message': 'Not enough history'}
            
            recent_improvements = []
            for i in range(len(accuracy_history) - patience, len(accuracy_history)):
                if i > 0:
                    improvement = accuracy_history[i] - accuracy_history[i-1]
                    recent_improvements.append(improvement)
            
            max_improvement = max(recent_improvements) if recent_improvements else 0
            
            if max_improvement < threshold:
                return {
                    'converged': True,
                    'message': f'Model converged after {len(accuracy_history)} rounds',
                    'final_accuracy': accuracy_history[-1]
                }
            else:
                return {
                    'converged': False,
                    'message': f'Model still improving. Max improvement: {max_improvement}',
                    'current_accuracy': accuracy_history[-1]
                }
        
        except Exception as e:
            logger.error(f"Error checking convergence: {str(e)}")
            raise
    
    def get_participant_status(self, participant_id=None):
        """
        Get status of participant(s)
        
        Args:
            participant_id (str): Optional specific participant
        
        Returns:
            dict: Participant status information
        """
        try:
            if participant_id:
                if participant_id not in self.participants:
                    return {'error': 'Participant not found'}
                return self.participants[participant_id]
            else:
                return {
                    'total_participants': len(self.participants),
                    'participants': self.participants,
                    'current_round': self.current_round
                }
        
        except Exception as e:
            logger.error(f"Error getting participant status: {str(e)}")
            raise
    
    def remove_participant(self, participant_id):
        """
        Remove participant from federated learning
        
        Args:
            participant_id (str): Participant identifier
        
        Returns:
            dict: Removal confirmation
        """
        try:
            if participant_id in self.participants:
                del self.participants[participant_id]
                logger.info(f"Participant removed: {participant_id}")
                return {'status': 'success', 'message': 'Participant removed'}
            else:
                return {'status': 'error', 'message': 'Participant not found'}
        
        except Exception as e:
            logger.error(f"Error removing participant: {str(e)}")
            raise
