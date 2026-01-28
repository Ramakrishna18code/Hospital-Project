"""
Machine Learning Engine for Healthcare Data
Implements various ML algorithms for healthcare classification and anomaly detection
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
import joblib
import logging

logger = logging.getLogger(__name__)

class MLEngine:
    """Machine Learning Engine for healthcare applications"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.models = {}
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
    
    def train_model(self, algorithm, X_train, y_train):
        """
        Train a machine learning model
        
        Args:
            algorithm (str): Algorithm type (random_forest, svm, knn, logistic_regression, decision_tree, naive_bayes)
            X_train (array-like): Training features
            y_train (array-like): Training labels
        
        Returns:
            model: Trained model object
        """
        try:
            X_train = np.array(X_train)
            y_train = np.array(y_train)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            
            if algorithm == 'random_forest':
                model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=15,
                    random_state=42,
                    n_jobs=-1
                )
            
            elif algorithm == 'svm':
                model = SVC(kernel='rbf', gamma='scale', random_state=42)
            
            elif algorithm == 'knn':
                model = KNeighborsClassifier(n_neighbors=5)
            
            elif algorithm == 'logistic_regression':
                model = LogisticRegression(max_iter=1000, random_state=42)
            
            elif algorithm == 'decision_tree':
                model = DecisionTreeClassifier(max_depth=15, random_state=42)
            
            elif algorithm == 'naive_bayes':
                model = GaussianNB()
            
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Store model
            self.models[algorithm] = {
                'model': model,
                'scaler': self.scaler,
                'algorithm': algorithm
            }
            
            logger.info(f"Model trained successfully: {algorithm}")
            return model
        
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
    
    def evaluate_model(self, model, X_test, y_test):
        """
        Evaluate model performance
        
        Args:
            model: Trained model
            X_test (array-like): Test features
            y_test (array-like): Test labels
        
        Returns:
            dict: Performance metrics
        """
        try:
            X_test = np.array(X_test)
            y_test = np.array(y_test)
            
            # Scale features
            X_test_scaled = self.scaler.transform(X_test)
            
            # Make predictions
            y_pred = model.predict(X_test_scaled)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            
            metrics = {
                'accuracy': round(accuracy, 4),
                'precision': round(precision, 4),
                'recall': round(recall, 4),
                'f1_score': round(f1, 4)
            }
            
            logger.info(f"Model evaluation - Accuracy: {accuracy:.4f}")
            return metrics
        
        except Exception as e:
            logger.error(f"Error evaluating model: {str(e)}")
            raise
    
    def predict(self, model, X, algorithm='random_forest'):
        """
        Make predictions using trained model
        
        Args:
            model: Trained model
            X (array-like): Input features
            algorithm (str): Algorithm type
        
        Returns:
            array: Predictions
        """
        try:
            X = np.array(X)
            X_scaled = self.scaler.transform(X)
            predictions = model.predict(X_scaled)
            return predictions.tolist()
        
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            raise
    
    def detect_anomalies(self, dataset, contamination=0.1):
        """
        Detect anomalies in healthcare data using Isolation Forest
        
        Args:
            dataset (list): List of data points
            contamination (float): Expected proportion of anomalies
        
        Returns:
            list: Indices of detected anomalies
        """
        try:
            dataset = np.array(dataset)
            
            # Scale features
            dataset_scaled = self.scaler.fit_transform(dataset)
            
            # Train anomaly detector
            self.anomaly_detector = IsolationForest(
                contamination=contamination,
                random_state=42
            )
            
            # Detect anomalies (-1 for anomalies, 1 for normal)
            predictions = self.anomaly_detector.fit_predict(dataset_scaled)
            
            # Get anomaly indices
            anomaly_indices = np.where(predictions == -1)[0].tolist()
            
            # Get anomaly scores
            anomaly_scores = self.anomaly_detector.score_samples(dataset_scaled)
            
            anomalies = []
            for idx in anomaly_indices:
                anomalies.append({
                    'index': idx,
                    'anomaly_score': round(float(anomaly_scores[idx]), 4),
                    'severity': self._classify_severity(anomaly_scores[idx])
                })
            
            logger.info(f"Anomalies detected: {len(anomalies)} out of {len(dataset)}")
            return anomalies
        
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            raise
    
    def _classify_severity(self, anomaly_score):
        """Classify anomaly severity based on score"""
        if anomaly_score < -0.5:
            return 'critical'
        elif anomaly_score < -0.3:
            return 'high'
        elif anomaly_score < -0.1:
            return 'medium'
        else:
            return 'low'
    
    def get_feature_importance(self, model, feature_names=None):
        """
        Get feature importance from trained model
        
        Args:
            model: Trained model
            feature_names (list): Feature names
        
        Returns:
            dict: Feature importance scores
        """
        try:
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                
                if feature_names:
                    importance_dict = dict(zip(feature_names, importances.tolist()))
                    return sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
                else:
                    return importances.tolist()
            else:
                logger.warning("Model does not have feature importance attribute")
                return None
        
        except Exception as e:
            logger.error(f"Error getting feature importance: {str(e)}")
            raise
    
    def save_model(self, model, filename):
        """Save trained model to file"""
        try:
            joblib.dump(model, f'{filename}.pkl')
            logger.info(f"Model saved: {filename}.pkl")
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise
    
    def load_model(self, filename):
        """Load trained model from file"""
        try:
            model = joblib.load(f'{filename}.pkl')
            logger.info(f"Model loaded: {filename}.pkl")
            return model
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
