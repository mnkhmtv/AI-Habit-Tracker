from sklearn.cluster import KMeans
import numpy as np
from datetime import datetime

class HabitAnalyzer:
    def __init__(self):
        self.model = KMeans(n_clusters=1)  # Simple clustering for recommended time
        
    def time_to_minutes(self, time_str):
        """Convert HH:MM format to minutes since midnight"""
        h, m = map(int, time_str.split(':'))
        return h * 60 + m
    
    def minutes_to_time(self, minutes):
        """Convert minutes since midnight back to HH:MM"""
        h = minutes // 60
        m = minutes % 60
        return f"{h:02d}:{m:02d}"
    
    def analyze_habit(self, habit_data):
        selected_time = self.time_to_minutes(habit_data['selected_time'])
        actual_times = [self.time_to_minutes(t) for t in habit_data['actual_time']]
        
        if not actual_times:
            return {
                'streak': 0,
                'success_rate': 0.0,
                'avg_deviation': 0.0,
                'recommended_time': habit_data['selected_time']
            }
        
        # Calculate metrics
        deviations = [abs(selected_time - t) for t in actual_times]
        avg_deviation = np.mean(deviations)
        success_rate = sum(1 for d in deviations if d <= 30) / len(actual_times)  # Success if within 30 minutes
        
        # Calculate streak
        streak = 0
        if len(actual_times) > 1:
            sorted_times = sorted(actual_times)
            for i in range(1, len(sorted_times)):
                if sorted_times[i] - sorted_times[i-1] <= 1440:  # Within 24 hours
                    streak += 1
        
        # Predict recommended time using clustering
        X = np.array(actual_times).reshape(-1, 1)
        self.model.fit(X)
        recommended_minutes = int(self.model.cluster_centers_[0][0])
        recommended_time = self.minutes_to_time(recommended_minutes)
        
        return {
            'streak': streak,
            'success_rate': float(success_rate),
            'avg_deviation': float(avg_deviation),
            'recommended_time': recommended_time
        }