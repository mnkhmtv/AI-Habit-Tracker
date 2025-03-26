import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from ml_model import HabitAnalyzer
import pickle

def train_model(csv_path):
    # Load data
    df = pd.read_csv(csv_path)
    
    # Initialize analyzer
    analyzer = HabitAnalyzer()
    
    # Prepare training data
    actual_times = []
    for times in df['actual_time']:
        # Assuming actual_time is stored as comma-separated string in CSV
        time_list = times.split(',')
        actual_times.extend([analyzer.time_to_minutes(t.strip()) for t in time_list])
    
    # Train model
    X = np.array(actual_times).reshape(-1, 1)
    analyzer.model.fit(X)
    
    # Save model
    with open('habit_model.pkl', 'wb') as f:
        pickle.dump(analyzer, f)
    
    print("Model trained and saved successfully!")

if __name__ == "__main__":
    # Example usage
    train_model('/Users/dminnakhmetova/AI-Habit-Tracker/datasets/habit_data.csv')