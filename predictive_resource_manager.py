#!/usr/bin/env python3
"""
Predictive Resource Manager

This system uses machine learning and pattern recognition to predict resource needs
and proactively allocate models and resources before they're needed.
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

@dataclass
class ResourcePrediction:
    """Prediction for resource needs"""
    timestamp: datetime
    predicted_memory_mb: float
    predicted_cpu_percent: float
    predicted_active_models: int
    predicted_task_load: float
    confidence: float
    horizon_minutes: int
    reasoning: str

@dataclass
class UsagePattern:
    """Usage pattern for predictive analysis"""
    pattern_id: str
    hour_of_day: int
    day_of_week: int
    typical_memory_usage: float
    typical_cpu_usage: float
    typical_model_count: int
    typical_task_rate: float
    frequency: int
    last_seen: datetime

class PredictiveResourceManager:
    """
    Predictive resource management system that anticipates needs and optimizes allocation
    """
    
    def __init__(self, system_monitor, model_manager, agent_coordinator):
        self.system_monitor = system_monitor
        self.model_manager = model_manager
        self.agent_coordinator = agent_coordinator
        
        # Prediction models
        self.memory_predictor = None
        self.cpu_predictor = None
        self.task_predictor = None
        
        # Historical data for learning
        self.usage_history = deque(maxlen=2000)  # Keep 2000 data points
        self.patterns = {}
        self.prediction_cache = {}
        
        # Configuration
        self.prediction_horizons = [15, 30, 60, 120, 240]  # minutes
        self.pattern_detection_enabled = True
        self.proactive_loading_enabled = True
        self.learning_enabled = True
        
        # Performance tracking
        self.prediction_accuracy = deque(maxlen=100)
        self.proactive_hits = 0  # Successful proactive allocations
        self.proactive_misses = 0  # Unnecessary proactive allocations
        
        # Setup logging
        self.logger = logging.getLogger("PredictiveManager")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    async def start_predictive_management(self, interval_seconds: int = 300):  # 5 minutes
        """Start predictive resource management"""
        self.logger.info("Started predictive resource management")
        
        while True:
            try:
                # Collect current usage data
                await self._collect_usage_data()
                
                # Update prediction models
                if self.learning_enabled and len(self.usage_history) > 20:
                    await self._update_prediction_models()
                
                # Detect usage patterns
                if self.pattern_detection_enabled:
                    await self._detect_usage_patterns()
                
                # Make predictions
                predictions = await self._make_predictions()
                
                # Take proactive actions
                if self.proactive_loading_enabled and predictions:
                    await self._take_proactive_actions(predictions)
                
                # Validate previous predictions
                await self._validate_predictions()
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Predictive management error: {e}")
                await asyncio.sleep(interval_seconds)
    
    async def _collect_usage_data(self):
        """Collect current usage data for learning"""
        try:
            # Get current system metrics
            if hasattr(self.system_monitor, 'metrics_history') and self.system_monitor.metrics_history:
                latest_metrics = self.system_monitor.metrics_history[-1]
                
                # Get current time features
                now = datetime.now()
                
                usage_data = {
                    'timestamp': now,
                    'hour_of_day': now.hour,
                    'day_of_week': now.weekday(),
                    'memory_percent': latest_metrics.memory_percent,
                    'cpu_percent': latest_metrics.cpu_percent,
                    'active_models': latest_metrics.active_models,
                    'active_agents': latest_metrics.active_agents,
                    'pending_tasks': latest_metrics.pending_tasks,
                    'throughput': latest_metrics.throughput_tasks_per_minute
                }
                
                self.usage_history.append(usage_data)
                
        except Exception as e:
            self.logger.error(f"Failed to collect usage data: {e}")
    
    async def _update_prediction_models(self):
        """Update machine learning prediction models"""
        try:
            if len(self.usage_history) < 30:  # Need minimum data
                return
            
            # Prepare training data
            X, y_memory, y_cpu, y_tasks = self._prepare_training_data()
            
            if len(X) < 10:
                return
            
            # Train memory predictor
            self.memory_predictor = LinearRegression()
            self.memory_predictor.fit(X, y_memory)
            
            # Train CPU predictor
            self.cpu_predictor = LinearRegression()
            self.cpu_predictor.fit(X, y_cpu)
            
            # Train task load predictor
            self.task_predictor = LinearRegression()
            self.task_predictor.fit(X, y_tasks)
            
            self.logger.debug("Updated prediction models")
            
        except Exception as e:
            self.logger.error(f"Failed to update prediction models: {e}")
    
    def _prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Prepare training data for machine learning models"""
        
        # Convert usage history to feature matrix
        features = []
        memory_targets = []
        cpu_targets = []
        task_targets = []
        
        history_list = list(self.usage_history)
        
        # Use sliding window for feature extraction
        for i in range(10, len(history_list)):  # Need some history for features
            current = history_list[i]
            
            # Time-based features
            feature_vector = [
                current['hour_of_day'],
                current['day_of_week'],
                # Recent averages (last 5 data points)
                np.mean([history_list[j]['memory_percent'] for j in range(i-5, i)]),
                np.mean([history_list[j]['cpu_percent'] for j in range(i-5, i)]),
                np.mean([history_list[j]['active_models'] for j in range(i-5, i)]),
                np.mean([history_list[j]['throughput'] for j in range(i-5, i)]),
                # Trends (difference from 10 periods ago)
                current['memory_percent'] - history_list[i-10]['memory_percent'],
                current['cpu_percent'] - history_list[i-10]['cpu_percent'],
            ]
            
            features.append(feature_vector)
            memory_targets.append(current['memory_percent'])
            cpu_targets.append(current['cpu_percent'])
            task_targets.append(current['throughput'])
        
        return (np.array(features), 
                np.array(memory_targets), 
                np.array(cpu_targets), 
                np.array(task_targets))
    
    async def _detect_usage_patterns(self):
        """Detect recurring usage patterns"""
        try:
            if len(self.usage_history) < 50:
                return
            
            # Group usage by hour and day
            pattern_groups = defaultdict(list)
            
            for usage in list(self.usage_history)[-200:]:  # Last 200 data points
                key = (usage['hour_of_day'], usage['day_of_week'])
                pattern_groups[key].append(usage)
            
            # Analyze patterns
            for (hour, day), usages in pattern_groups.items():
                if len(usages) >= 3:  # Need multiple occurrences
                    pattern_id = f"h{hour}_d{day}"
                    
                    avg_memory = np.mean([u['memory_percent'] for u in usages])
                    avg_cpu = np.mean([u['cpu_percent'] for u in usages])
                    avg_models = np.mean([u['active_models'] for u in usages])
                    avg_tasks = np.mean([u['throughput'] for u in usages])
                    
                    self.patterns[pattern_id] = UsagePattern(
                        pattern_id=pattern_id,
                        hour_of_day=hour,
                        day_of_week=day,
                        typical_memory_usage=avg_memory,
                        typical_cpu_usage=avg_cpu,
                        typical_model_count=int(avg_models),
                        typical_task_rate=avg_tasks,
                        frequency=len(usages),
                        last_seen=max(u['timestamp'] for u in usages)
                    )
            
            self.logger.debug(f"Detected {len(self.patterns)} usage patterns")
            
        except Exception as e:
            self.logger.error(f"Pattern detection failed: {e}")
    
    async def _make_predictions(self) -> List[ResourcePrediction]:
        """Make resource predictions for different time horizons"""
        predictions = []
        
        try:
            current_time = datetime.now()
            
            # Get current features
            if not self.usage_history:
                return predictions
            
            current_usage = list(self.usage_history)[-1]
            
            for horizon in self.prediction_horizons:
                prediction = await self._predict_for_horizon(current_time, horizon, current_usage)
                if prediction:
                    predictions.append(prediction)
            
            # Cache predictions
            self.prediction_cache[current_time] = predictions
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
        
        return predictions
    
    async def _predict_for_horizon(self, current_time: datetime, horizon_minutes: int, 
                                 current_usage: Dict) -> Optional[ResourcePrediction]:
        """Make prediction for specific time horizon"""
        try:
            future_time = current_time + timedelta(minutes=horizon_minutes)
            
            # Method 1: Pattern-based prediction
            pattern_pred = self._predict_from_patterns(future_time)
            
            # Method 2: ML-based prediction (if models are trained)
            ml_pred = self._predict_from_ml(current_usage, horizon_minutes)
            
            # Method 3: Trend-based prediction
            trend_pred = self._predict_from_trends(horizon_minutes)
            
            # Combine predictions with confidence weighting
            predictions = [p for p in [pattern_pred, ml_pred, trend_pred] if p is not None]
            
            if not predictions:
                return None
            
            # Weighted average based on confidence
            total_weight = sum(p['confidence'] for p in predictions)
            if total_weight == 0:
                return None
            
            combined_memory = sum(p['memory'] * p['confidence'] for p in predictions) / total_weight
            combined_cpu = sum(p['cpu'] * p['confidence'] for p in predictions) / total_weight
            combined_models = sum(p['models'] * p['confidence'] for p in predictions) / total_weight
            combined_tasks = sum(p['tasks'] * p['confidence'] for p in predictions) / total_weight
            combined_confidence = total_weight / len(predictions) / 100  # Normalize
            
            reasoning = f"Combined prediction from {len(predictions)} methods"
            
            return ResourcePrediction(
                timestamp=current_time,
                predicted_memory_mb=combined_memory,
                predicted_cpu_percent=combined_cpu,
                predicted_active_models=int(combined_models),
                predicted_task_load=combined_tasks,
                confidence=min(combined_confidence, 1.0),
                horizon_minutes=horizon_minutes,
                reasoning=reasoning
            )
            
        except Exception as e:
            self.logger.error(f"Horizon prediction failed: {e}")
            return None
    
    def _predict_from_patterns(self, future_time: datetime) -> Optional[Dict]:
        """Predict based on historical patterns"""
        pattern_key = f"h{future_time.hour}_d{future_time.weekday()}"
        
        if pattern_key in self.patterns:
            pattern = self.patterns[pattern_key]
            return {
                'memory': pattern.typical_memory_usage,
                'cpu': pattern.typical_cpu_usage,
                'models': pattern.typical_model_count,
                'tasks': pattern.typical_task_rate,
                'confidence': min(pattern.frequency * 10, 80)  # Higher confidence with more occurrences
            }
        
        return None
    
    def _predict_from_ml(self, current_usage: Dict, horizon_minutes: int) -> Optional[Dict]:
        """Predict using machine learning models"""
        if not all([self.memory_predictor, self.cpu_predictor, self.task_predictor]):
            return None
        
        try:
            # Prepare feature vector for prediction
            feature_vector = np.array([[
                current_usage['hour_of_day'],
                current_usage['day_of_week'],
                current_usage['memory_percent'],
                current_usage['cpu_percent'],
                current_usage['active_models'],
                current_usage['throughput'],
                0,  # Trend placeholder
                0   # Trend placeholder
            ]])
            
            memory_pred = self.memory_predictor.predict(feature_vector)[0]
            cpu_pred = self.cpu_predictor.predict(feature_vector)[0]
            task_pred = self.task_predictor.predict(feature_vector)[0]
            
            # Estimate model count based on memory and task load
            model_pred = max(1, int(memory_pred / 30))  # Rough estimate
            
            return {
                'memory': max(0, memory_pred),
                'cpu': max(0, min(100, cpu_pred)),
                'models': model_pred,
                'tasks': max(0, task_pred),
                'confidence': 70  # ML confidence
            }
            
        except Exception as e:
            self.logger.error(f"ML prediction failed: {e}")
            return None
    
    def _predict_from_trends(self, horizon_minutes: int) -> Optional[Dict]:
        """Predict based on recent trends"""
        if len(self.usage_history) < 10:
            return None
        
        try:
            recent_data = list(self.usage_history)[-10:]
            
            # Calculate trends
            memory_trend = (recent_data[-1]['memory_percent'] - recent_data[0]['memory_percent']) / 10
            cpu_trend = (recent_data[-1]['cpu_percent'] - recent_data[0]['cpu_percent']) / 10
            task_trend = (recent_data[-1]['throughput'] - recent_data[0]['throughput']) / 10
            
            # Project trends forward
            current = recent_data[-1]
            periods_ahead = horizon_minutes / 5  # Assuming 5-minute intervals
            
            predicted_memory = current['memory_percent'] + (memory_trend * periods_ahead)
            predicted_cpu = current['cpu_percent'] + (cpu_trend * periods_ahead)
            predicted_tasks = current['throughput'] + (task_trend * periods_ahead)
            
            return {
                'memory': max(0, min(100, predicted_memory)),
                'cpu': max(0, min(100, predicted_cpu)),
                'models': current['active_models'],  # Assume stable
                'tasks': max(0, predicted_tasks),
                'confidence': 50  # Medium confidence for trend-based
            }
            
        except Exception as e:
            self.logger.error(f"Trend prediction failed: {e}")
            return None
    
    async def _take_proactive_actions(self, predictions: List[ResourcePrediction]):
        """Take proactive actions based on predictions"""
        
        for prediction in predictions:
            try:
                # Only act on high-confidence, near-term predictions
                if prediction.confidence < 0.6 or prediction.horizon_minutes > 60:
                    continue
                
                actions_taken = []
                
                # Memory pressure predicted
                if prediction.predicted_memory_mb > 85:
                    action = await self._prepare_for_memory_pressure(prediction)
                    if action:
                        actions_taken.append(action)
                
                # High task load predicted
                if prediction.predicted_task_load > 5:
                    action = await self._prepare_for_high_load(prediction)
                    if action:
                        actions_taken.append(action)
                
                # Model scaling predicted
                current_models = self.usage_history[-1]['active_models'] if self.usage_history else 0
                if prediction.predicted_active_models > current_models + 1:
                    action = await self._prepare_for_model_scaling(prediction)
                    if action:
                        actions_taken.append(action)
                
                if actions_taken:
                    self.logger.info(f"Proactive actions: {', '.join(actions_taken)} "
                                   f"(confidence: {prediction.confidence:.1%}, "
                                   f"horizon: {prediction.horizon_minutes}min)")
                
            except Exception as e:
                self.logger.error(f"Proactive action failed: {e}")
    
    async def _prepare_for_memory_pressure(self, prediction: ResourcePrediction) -> Optional[str]:
        """Prepare for predicted memory pressure"""
        try:
            # In real implementation, this would trigger preemptive model unloading
            self.logger.debug(f"Preparing for memory pressure: {prediction.predicted_memory_mb:.1f}%")
            return "memory_prep"
        except:
            return None
    
    async def _prepare_for_high_load(self, prediction: ResourcePrediction) -> Optional[str]:
        """Prepare for predicted high task load"""
        try:
            # In real implementation, this would pre-warm models or scale resources
            self.logger.debug(f"Preparing for high load: {prediction.predicted_task_load:.1f} tasks/min")
            return "load_prep"
        except:
            return None
    
    async def _prepare_for_model_scaling(self, prediction: ResourcePrediction) -> Optional[str]:
        """Prepare for predicted model scaling needs"""
        try:
            # In real implementation, this would preload likely-needed models
            self.logger.debug(f"Preparing for model scaling: {prediction.predicted_active_models} models")
            return "scale_prep"
        except:
            return None
    
    async def _validate_predictions(self):
        """Validate previous predictions against actual usage"""
        try:
            if not self.usage_history or not self.prediction_cache:
                return
            
            current_time = datetime.now()
            current_usage = self.usage_history[-1]
            
            # Find predictions made 15+ minutes ago to validate
            for pred_time, predictions in list(self.prediction_cache.items()):
                time_diff = (current_time - pred_time).total_seconds() / 60
                
                # Find prediction closest to current time difference
                matching_pred = None
                for pred in predictions:
                    if abs(pred.horizon_minutes - time_diff) < 5:  # Within 5 minutes
                        matching_pred = pred
                        break
                
                if matching_pred:
                    # Calculate accuracy
                    memory_error = abs(matching_pred.predicted_memory_mb - current_usage['memory_percent'])
                    cpu_error = abs(matching_pred.predicted_cpu_percent - current_usage['cpu_percent'])
                    
                    accuracy = 1.0 - (memory_error + cpu_error) / 200  # Normalize to 0-1
                    accuracy = max(0, accuracy)
                    
                    self.prediction_accuracy.append(accuracy)
                    
                    # Clean up old predictions
                    if time_diff > 240:  # Remove predictions older than 4 hours
                        del self.prediction_cache[pred_time]
            
        except Exception as e:
            self.logger.error(f"Prediction validation failed: {e}")
    
    def get_predictive_analytics(self) -> Dict[str, Any]:
        """Get analytics about predictive performance"""
        
        avg_accuracy = np.mean(self.prediction_accuracy) if self.prediction_accuracy else 0
        total_proactive = self.proactive_hits + self.proactive_misses
        proactive_success_rate = self.proactive_hits / total_proactive if total_proactive > 0 else 0
        
        return {
            "prediction_accuracy": avg_accuracy,
            "predictions_made": len(self.prediction_accuracy),
            "patterns_detected": len(self.patterns),
            "usage_history_size": len(self.usage_history),
            "proactive_success_rate": proactive_success_rate,
            "proactive_actions": {
                "hits": self.proactive_hits,
                "misses": self.proactive_misses,
                "total": total_proactive
            },
            "models_trained": {
                "memory": self.memory_predictor is not None,
                "cpu": self.cpu_predictor is not None,
                "tasks": self.task_predictor is not None
            }
        }

async def test_predictive_manager():
    """Test the predictive resource manager"""
    print("Testing Predictive Resource Manager...")
    
    # Mock dependencies
    class MockSystemMonitor:
        def __init__(self):
            self.metrics_history = deque()
            # Add some mock data
            from real_time_system_monitor import SystemMetrics
            for i in range(50):
                metrics = SystemMetrics(
                    timestamp=datetime.now() - timedelta(minutes=i*5),
                    cpu_percent=30 + (i % 20),
                    memory_percent=50 + (i % 30),
                    memory_available_gb=4.0,
                    active_models=2 + (i % 3),
                    active_agents=3,
                    pending_tasks=i % 5,
                    response_time_ms=100,
                    throughput_tasks_per_minute=i % 10
                )
                self.metrics_history.append(metrics)
    
    monitor = MockSystemMonitor()
    predictor = PredictiveResourceManager(monitor, None, None)
    
    # Test data collection
    await predictor._collect_usage_data()
    print(f"✓ Collected usage data: {len(predictor.usage_history)} entries")
    
    # Test pattern detection
    await predictor._detect_usage_patterns()
    print(f"✓ Detected {len(predictor.patterns)} usage patterns")
    
    # Test prediction
    predictions = await predictor._make_predictions()
    print(f"✓ Made {len(predictions)} predictions")
    
    if predictions:
        pred = predictions[0]
        print(f"  Sample prediction: {pred.predicted_memory_mb:.1f}% memory, "
              f"{pred.predicted_cpu_percent:.1f}% CPU in {pred.horizon_minutes}min "
              f"(confidence: {pred.confidence:.1%})")
    
    # Test analytics
    analytics = predictor.get_predictive_analytics()
    print(f"✓ Analytics: {analytics['patterns_detected']} patterns, "
          f"{analytics['usage_history_size']} history entries")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_predictive_manager())
    exit(0 if result else 1)
