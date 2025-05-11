import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.neighbors import NearestNeighbors
import joblib
import os
from datetime import datetime, timedelta

class HabitRecommender:
    def __init__(self, survey_data_path='datasets/survey_data.csv', 
                 habits_catalog_path='datasets/habits_catalog.csv'):
        self.survey_data_path = survey_data_path
        self.habits_catalog_path = habits_catalog_path
        self.model_path = 'data/habit_recommender_model.pkl'
        self.mlb_path = 'data/mlb_transformer.pkl'
        
        self.survey_data = pd.read_csv(survey_data_path)
        self.habits_catalog = pd.read_csv(habits_catalog_path)
        
        # Create model directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Rename columns to standard format for internal processing
        self._rename_columns()
        
        # Initialize or load model
        if os.path.exists(self.model_path) and os.path.exists(self.mlb_path):
            self.load_model()
        else:
            self.train_model()
    
    def _rename_columns(self):
        """Rename columns from Russian to standard internal format."""
        # Map Russian column names to internal format
        column_mapping = {
            'Отметка времени': 'timestamp',
            'Ваш возраст': 'age',
            'Ваш пол': 'gender',
            'Какие привычки у вас уже есть? (Можно выбрать несколько)': 'existing_habits',
            'Что вы хотите улучшить? (Можно выбрать несколько)': 'improvement_areas',
            'Сколько времени готовы тратить ежедневно на новую привычку?': 'time_commitment',
            'Какое время суток предпочитаете для выполнения привычки?': 'preferred_time',
            'Что мешает вам внедрять новые привычки? (Можно выбрать несколько):': 'barriers'
        }
        
        # Rename columns in the survey data
        self.survey_data = self.survey_data.rename(columns=column_mapping)
    
    def preprocess_data(self):
        # Process existing habits and improvement areas as multi-label features
        df = self.survey_data.copy()
        
        # Create multi-label binarizer for categorical features
        self.mlb_existing_habits = MultiLabelBinarizer()
        self.mlb_improvement = MultiLabelBinarizer()
        self.mlb_barriers = MultiLabelBinarizer()
        
        # Transform multi-label data
        df['existing_habits_list'] = df['existing_habits'].str.split(',')
        df['improvement_areas_list'] = df['improvement_areas'].str.split(',')
        df['barriers_list'] = df['barriers'].str.split(',')
        
        existing_habits_binary = self.mlb_existing_habits.fit_transform(df['existing_habits_list'])
        improvement_areas_binary = self.mlb_improvement.fit_transform(df['improvement_areas_list'])
        barriers_binary = self.mlb_barriers.fit_transform(df['barriers_list'])
        
        # Create binary feature names
        existing_habits_features = [f'existing_{habit}' for habit in self.mlb_existing_habits.classes_]
        improvement_features = [f'improve_{area}' for area in self.mlb_improvement.classes_]
        barriers_features = [f'barrier_{barrier}' for barrier in self.mlb_barriers.classes_]
        
        # Create binary DataFrames
        existing_habits_df = pd.DataFrame(existing_habits_binary, columns=existing_habits_features)
        improvement_df = pd.DataFrame(improvement_areas_binary, columns=improvement_features)
        barriers_df = pd.DataFrame(barriers_binary, columns=barriers_features)
        
        # Convert categorical variables to one-hot encoding
        age_dummies = pd.get_dummies(df['age'], prefix='age')
        gender_dummies = pd.get_dummies(df['gender'], prefix='gender')
        time_commitment_dummies = pd.get_dummies(df['time_commitment'], prefix='time')
        preferred_time_dummies = pd.get_dummies(df['preferred_time'], prefix='preferred_time')
        
        # Combine all features
        feature_df = pd.concat([
            age_dummies, gender_dummies, 
            existing_habits_df, improvement_df, barriers_df,
            time_commitment_dummies, preferred_time_dummies
        ], axis=1)
        
        return feature_df
    
    def train_model(self):
        # Preprocess training data
        feature_df = self.preprocess_data()
        
        # Train the model (KNN-based collaborative filtering)
        self.model = NearestNeighbors(n_neighbors=3, algorithm='ball_tree')
        self.model.fit(feature_df)
        
        # Save the model and transformers
        joblib.dump(self.model, self.model_path)
        
        # Save the MLBs in a dictionary
        mlb_dict = {
            'existing_habits': self.mlb_existing_habits,
            'improvement': self.mlb_improvement,
            'barriers': self.mlb_barriers
        }
        joblib.dump(mlb_dict, self.mlb_path)
    
    def load_model(self):
        self.model = joblib.load(self.model_path)
        
        # Load the MLBs
        mlb_dict = joblib.load(self.mlb_path)
        self.mlb_existing_habits = mlb_dict['existing_habits']
        self.mlb_improvement = mlb_dict['improvement']
        self.mlb_barriers = mlb_dict['barriers']
    
    def preprocess_user_data(self, user_data):
        # Convert user data to same format as training data
        user_df = pd.DataFrame([user_data])
        
        # Transform multi-label data
        user_df['existing_habits_list'] = user_df['existing_habits'].str.split(',')
        user_df['improvement_areas_list'] = user_df['improvement_areas'].str.split(',')
        user_df['barriers_list'] = user_df['barriers'].str.split(',')
        
        existing_habits_binary = self.mlb_existing_habits.transform(user_df['existing_habits_list'])
        improvement_areas_binary = self.mlb_improvement.transform(user_df['improvement_areas_list'])
        barriers_binary = self.mlb_barriers.transform(user_df['barriers_list'])
        
        # Create binary feature names
        existing_habits_features = [f'existing_{habit}' for habit in self.mlb_existing_habits.classes_]
        improvement_features = [f'improve_{area}' for area in self.mlb_improvement.classes_]
        barriers_features = [f'barrier_{barrier}' for barrier in self.mlb_barriers.classes_]
        
        # Create binary DataFrames
        existing_habits_df = pd.DataFrame(existing_habits_binary, columns=existing_habits_features)
        improvement_df = pd.DataFrame(improvement_areas_binary, columns=improvement_features)
        barriers_df = pd.DataFrame(barriers_binary, columns=barriers_features)
        
        # Create dummies for categorical variables with all possible categories
        age_dummies = pd.DataFrame(0, index=user_df.index, 
                                  columns=[f'age_{category}' for category in ['18-25', '26-35', '36-45', '45+']])
        if f'age_{user_df["age"].iloc[0]}' in age_dummies.columns:
            age_dummies.loc[0, f'age_{user_df["age"].iloc[0]}'] = 1
        
        gender_dummies = pd.DataFrame(0, index=user_df.index, 
                                     columns=[f'gender_{category}' for category in ['Мужской', 'Женский']])
        if f'gender_{user_df["gender"].iloc[0]}' in gender_dummies.columns:
            gender_dummies.loc[0, f'gender_{user_df["gender"].iloc[0]}'] = 1
        
        time_commitment_dummies = pd.DataFrame(0, index=user_df.index, 
                                             columns=[f'time_{category}' for category in ['5 минут', '15 минут', '30 минут', '1 час']])
        if f'time_{user_df["time_commitment"].iloc[0]}' in time_commitment_dummies.columns:
            time_commitment_dummies.loc[0, f'time_{user_df["time_commitment"].iloc[0]}'] = 1
        
        preferred_time_dummies = pd.DataFrame(0, index=user_df.index, 
                                            columns=[f'preferred_time_{category}' for category in ['Утро', 'День', 'Вечер', 'Не важно']])
        if f'preferred_time_{user_df["preferred_time"].iloc[0]}' in preferred_time_dummies.columns:
            preferred_time_dummies.loc[0, f'preferred_time_{user_df["preferred_time"].iloc[0]}'] = 1
        
        # Combine all features
        feature_df = pd.concat([
            age_dummies, gender_dummies, 
            existing_habits_df, improvement_df, barriers_df,
            time_commitment_dummies, preferred_time_dummies
        ], axis=1)
        
        # Ensure all columns from the training data are present
        all_training_features = list(joblib.load(self.model_path).feature_names_in_)
        for col in all_training_features:
            if col not in feature_df.columns:
                feature_df[col] = 0
        
        # Ensure columns are in the same order as training
        feature_df = feature_df[all_training_features]
        
        return feature_df
    
    def recommend_habits(self, user_data, n_recommendations=5):
        # Preprocess user data
        user_features = self.preprocess_user_data(user_data)
        
        # Find similar users
        distances, indices = self.model.kneighbors(user_features)
        
        # Get improvement areas for recommendations
        improvement_areas = user_data['improvement_areas'].split(',')
        
        # Filter habits catalog based on user's improvement areas and time commitment
        time_commitment = user_data['time_commitment']
        
        # Convert time_commitment to minutes for comparison
        time_mins = 0
        if '5 минут' in time_commitment:
            time_mins = 5
        elif '15 минут' in time_commitment:
            time_mins = 15
        elif '30 минут' in time_commitment:
            time_mins = 30
        elif '1 час' in time_commitment:
            time_mins = 60
        
        # Filter habits based on improvement areas (mapping to categories)
        category_mapping = {
            'Физическое здоровье': 'Физическое здоровье',
            'Ментальное здоровье': 'Ментальное здоровье',
            'Продуктивность': 'Продуктивность',
            'Финансы': 'Финансы',
            'Отношения': 'Отношения'
        }
        
        filtered_categories = [category_mapping[area.strip()] for area in improvement_areas if area.strip() in category_mapping]
        
        # Get habits in the user's categories of interest
        filtered_habits = self.habits_catalog[self.habits_catalog['category'].isin(filtered_categories)].copy()
        
        # Further filter based on time commitment
        filtered_habits['min_time'] = filtered_habits['time_required'].apply(
            lambda x: int(x.split('-')[0].split()[0]) if '-' in x else int(x.split()[0])
        )
        
        # Allow for habits that take same or less time than user is willing to commit
        filtered_habits = filtered_habits[filtered_habits['min_time'] <= time_mins + 5]
        
        # If no habits match the criteria, return a few general ones
        if len(filtered_habits) == 0:
            filtered_habits = self.habits_catalog[self.habits_catalog['time_required'].str.contains(f"{time_mins}")].head(n_recommendations)
        
        # If still no habits, return the first n from the catalog
        if len(filtered_habits) == 0:
            filtered_habits = self.habits_catalog.head(n_recommendations)
        
        # Sort by how well they match the time requirement
        filtered_habits['time_diff'] = filtered_habits['min_time'].apply(lambda x: abs(x - time_mins))
        filtered_habits = filtered_habits.sort_values(by=['time_diff'])
        
        # Return top recommendations
        recommendations = filtered_habits.head(n_recommendations).to_dict('records')
        
        return recommendations
    
    def recommend_optimal_time(self, tracking_data, current_selected_time):
        """Recommend optimal time based on user's tracking data."""
        if not tracking_data or len(tracking_data) < 3:
            # Not enough data yet
            return current_selected_time
        
        # Extract actual times from tracking data
        actual_times = [entry['actual_time'] for entry in tracking_data 
                      if entry['completed'] and entry['actual_time']]
        
        if not actual_times:
            return current_selected_time
        
        # Convert times to datetime objects for averaging
        time_objects = []
        for time_str in actual_times:
            try:
                time_obj = datetime.strptime(time_str, '%H:%M').time()
                time_objects.append(time_obj)
            except (ValueError, TypeError):
                continue
        
        if not time_objects:
            return current_selected_time
        
        # Calculate average time
        total_seconds = sum((t.hour * 3600 + t.minute * 60 + t.second) for t in time_objects)
        avg_seconds = total_seconds // len(time_objects)
        
        avg_hours = avg_seconds // 3600
        avg_minutes = (avg_seconds % 3600) // 60
        
        # Format as HH:MM
        recommended_time = f"{avg_hours:02d}:{avg_minutes:02d}"
        
        # Only recommend if significantly different from current time
        current_time_obj = datetime.strptime(current_selected_time, '%H:%M').time()
        recommended_time_obj = datetime.strptime(recommended_time, '%H:%M').time()
        
        current_seconds = current_time_obj.hour * 3600 + current_time_obj.minute * 60
        recommended_seconds = recommended_time_obj.hour * 3600 + recommended_time_obj.minute * 60
        
        # If difference is more than 2 hours, recommend the new time
        if abs(current_seconds - recommended_seconds) > 7200:
            return recommended_time
        
        return current_selected_time 