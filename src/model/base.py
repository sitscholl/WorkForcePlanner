import numpy as np
import pandas as pd
from sklearn.model_selection import (
    train_test_split, LeaveOneOut, 
    GroupKFold, TimeSeriesSplit, KFold
)
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

import warnings
from abc import ABC, abstractmethod
warnings.filterwarnings('ignore')

class BasePredictor(ABC):
    def __init__(self, categorical_encoding='onehot'):
        """
        Initialize the predictor with specified model type and encoding method.
        
        Args:
            model_type (str): Either 'linear' or 'random_forest'
            categorical_encoding (str): Either 'onehot' or 'label'
        """
        self.categorical_encoding = categorical_encoding
        self.model = None
        self.scaler = None
        self.categorical_encoders = {}  # Store encoders for each categorical column
        self.feature_columns = None
        self.categorical_columns = None
        self.numerical_columns = None
        self.target_column = None
        self.is_trained = False
        self.metrics = {}
        self.cv_results = {}
        self.encoded_feature_names = None  # Store final feature names after encoding

    @abstractmethod
    def _init_model(self):
        """Initialize the specific ML model."""
        pass

    @abstractmethod
    def _get_model_copy(self):
        """Return a new instance of the model for cross-validation."""
        pass

    def train(self, data, target_column, feature_columns, 
              cv_method='simple_split', cv_params=None, random_state=42):
        """
        Train the model on the provided data with flexible cross-validation and with categorical variable support.
        
        Args:
            data (pd.DataFrame): The training data
            target_column (str): Name of the target column (working hours)
            feature_columns (list): List of feature column names to use as predictors
            cv_method (str): Cross-validation method:
                - 'simple_split': Traditional train-test split
                - 'kfold': K-fold cross-validation
                - 'leave_one_out': Leave-one-out cross-validation
                - 'group_kfold': Grouped K-fold (e.g., by year)
                - 'time_series': Time series split
            cv_params (dict): Parameters for cross-validation method
            random_state (int): Random state for reproducibility
            
        Returns:
            dict: Training metrics including cross-validation results
        """

        if data[[target_column] + feature_columns].isna().any().any():
            raise ValueError("Data contains missing values")
                
        # Store column information
        self.target_column = target_column
        self.feature_columns = feature_columns
        self.categorical_columns = [i for i in feature_columns if data[i].dtype == 'object']
        self.numerical_columns = [col for col in feature_columns if col not in self.categorical_columns]
        
        # Initialize model
        self._init_model()
        
        # Prepare data
        # data_clean = data.dropna(subset=[target_column] + feature_columns)
        X_encoded, y = self._prepare_data(data, fit_encoders=True)
                        
        # Set default cv_params if not provided
        if cv_params is None:
            cv_params = {}
        
        # Perform cross-validation based on method
        if cv_method == 'simple_split':
            self._simple_split_validation(X_encoded, y, cv_params, random_state)
        elif cv_method == 'kfold':
            self._kfold_validation(X_encoded, y, cv_params, random_state)
        elif cv_method == 'leave_one_out':
            self._leave_one_out_validation(X_encoded, y)
        elif cv_method == 'group_kfold':
            self._group_kfold_validation(X_encoded, y, data, cv_params, random_state)
        elif cv_method == 'time_series':
            self._time_series_validation(X_encoded, y, cv_params)
        else:
            raise ValueError(f"Unknown cv_method: {cv_method}")
        
        # Train final model on all data
        if self.scaler is not None:
            X_scaled = self.scaler.fit_transform(X_encoded)
        else:
            X_scaled = X_encoded
        
        self.model.fit(X_scaled, y)
        
        # Add feature importance for random forest
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = dict(zip(feature_columns, self.model.feature_importances_))
            self.metrics['feature_importance'] = feature_importance
        
        self.is_trained = True
        return self.metrics

    def _prepare_data(self, data, fit_encoders=False):
        """
        Prepare data by encoding categorical variables and handling missing values.
        
        Args:
            data (pd.DataFrame): Input data
            fit_encoders (bool): Whether to fit the encoders (True for training, False for prediction)
            
        Returns:
            tuple: (X_encoded, y) where X_encoded is the processed feature matrix
        """
        # Extract target
        if self.target_column not in data.columns:
            raise ValueError(f"Target column '{self.target_column}' not found in data")
        y = data[self.target_column].copy()
        
        # Handle numerical columns
        if not all(col in data.columns for col in self.numerical_columns):
            raise ValueError(f"Not all numerical columns {self.numerical_columns} found in data")
        X_numerical = data[self.numerical_columns].copy()
        
        # Handle categorical columns
        X_categorical_encoded = pd.DataFrame()
        
        for col in self.categorical_columns:
            if col not in data.columns:
                raise ValueError(f"Categorical column '{col}' not found in data")
            
            # Fill missing values with mode or 'Unknown'
            col_data = data[col].fillna('Unknown')
            
            if fit_encoders:
                # Fit and transform during training
                if self.categorical_encoding == 'onehot':
                    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
                    encoded_data = encoder.fit_transform(col_data.values.reshape(-1, 1))
                    
                    # Create column names
                    feature_names = [f"{col}_{category}" for category in encoder.categories_[0]]
                    encoded_df = pd.DataFrame(encoded_data, columns=feature_names, index=data.index)
                    
                elif self.categorical_encoding == 'label':
                    encoder = LabelEncoder()
                    encoded_data = encoder.fit_transform(col_data)
                    encoded_df = pd.DataFrame({col: encoded_data}, index=data.index)
                    feature_names = [col]
                
                self.categorical_encoders[col] = encoder
                
            else:
                # Transform using fitted encoders during prediction
                encoder = self.categorical_encoders[col]
                
                if self.categorical_encoding == 'onehot':
                    encoded_data = encoder.transform(col_data.values.reshape(-1, 1))
                    feature_names = [f"{col}_{category}" for category in encoder.categories_[0]]
                    encoded_df = pd.DataFrame(encoded_data, columns=feature_names, index=data.index)
                    
                elif self.categorical_encoding == 'label':
                    # Handle unknown categories in label encoding
                    encoded_data = []
                    for value in col_data:
                        try:
                            encoded_data.append(encoder.transform([value])[0])
                        except ValueError:
                            # Unknown category, assign -1 or most frequent class
                            encoded_data.append(-1)
                    
                    encoded_df = pd.DataFrame({col: encoded_data}, index=data.index)
                    feature_names = [col]
            
            X_categorical_encoded = pd.concat([X_categorical_encoded, encoded_df], axis=1)
        
        # Combine numerical and categorical features
        X_encoded = pd.concat([X_numerical, X_categorical_encoded], axis=1)
        
        # Store feature names for later use
        if fit_encoders:
            self.encoded_feature_names = list(X_encoded.columns)
                
        return X_encoded, y
    
    def _simple_split_validation(self, X, y, cv_params, random_state):
        """Traditional train-test split validation."""
        test_size = cv_params.get('test_size', 0.2)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Scale and train
        if self.scaler is not None:
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
        else:
            X_train_scaled = X_train
            X_test_scaled = X_test
        
        temp_model = self._get_model_copy()
        temp_model.fit(X_train_scaled, y_train)
        
        y_pred_train = temp_model.predict(X_train_scaled)
        y_pred_test = temp_model.predict(X_test_scaled)
        
        self.metrics = {
            'cv_method': 'simple_split',
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test),
            'train_mse': mean_squared_error(y_train, y_pred_train),
            'test_mse': mean_squared_error(y_test, y_pred_test),
            'train_mae': mean_absolute_error(y_train, y_pred_train),
            'test_mae': mean_absolute_error(y_test, y_pred_test)
        }
    
    def _kfold_validation(self, X, y, cv_params, random_state):
        """K-fold cross-validation."""
        n_splits = cv_params.get('n_splits', 5)
        cv = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
        
        self._perform_cross_validation(X, y, cv, 'kfold')
    
    def _leave_one_out_validation(self, X, y):
        """Leave-one-out cross-validation."""
        cv = LeaveOneOut()
        self._perform_cross_validation(X, y, cv, 'leave_one_out')
    
    def _group_kfold_validation(self, X, y, data, cv_params, random_state):
        """Grouped K-fold cross-validation (e.g., by year)."""
        group_column = cv_params.get('group_column', 'Year')
        n_splits = cv_params.get('n_splits', 3)
        
        if group_column not in data.columns:
            raise ValueError(f"Group column '{group_column}' not found in data")

        if n_splits < 0:
            n_splits = len(data[group_column].unique())-1
        
        groups = data[group_column]
        cv = GroupKFold(n_splits=n_splits)
        
        self._perform_cross_validation(X, y, cv, 'group_kfold', groups=groups)
        
        # Add group information to metrics
        unique_groups = sorted(groups.unique())
        self.metrics['groups'] = unique_groups
        self.metrics['group_column'] = group_column
    
    def _time_series_validation(self, X, y, cv_params):
        """Time series cross-validation."""
        n_splits = cv_params.get('n_splits', 5)
        cv = TimeSeriesSplit(n_splits=n_splits)
        
        self._perform_cross_validation(X, y, cv, 'time_series')
    
    def _perform_cross_validation(self, X, y, cv, cv_method_name, groups=None):
        """Perform cross-validation and calculate metrics."""
        r2_scores = []
        mse_scores = []
        mae_scores = []
        predictions_all = []
        actuals_all = []
        
        cv_iterator = cv.split(X, y, groups) if groups is not None else cv.split(X, y)
        
        for fold, (train_idx, test_idx) in enumerate(cv_iterator):
            X_train_fold, X_test_fold = X.iloc[train_idx], X.iloc[test_idx]
            y_train_fold, y_test_fold = y.iloc[train_idx], y.iloc[test_idx]
            
            # Scale if necessary
            if self.scaler is not None:
                scaler_fold = StandardScaler()
                X_train_scaled = scaler_fold.fit_transform(X_train_fold)
                X_test_scaled = scaler_fold.transform(X_test_fold)
            else:
                X_train_scaled = X_train_fold
                X_test_scaled = X_test_fold
            
            # Train and predict
            temp_model = self._get_model_copy()
            temp_model.fit(X_train_scaled, y_train_fold)
            y_pred = temp_model.predict(X_test_scaled)

            # Store predictions and actuals for overall metrics
            predictions_all.extend(y_pred)
            actuals_all.extend(y_test_fold.values)
            
            # Calculate fold-specific metrics
            mse_scores.append(mean_squared_error(y_test_fold, y_pred))
            mae_scores.append(mean_absolute_error(y_test_fold, y_pred))

            # Only calculate R² if we have more than one sample in the test fold
            if len(y_test_fold) > 1:
                r2_fold = r2_score(y_test_fold, y_pred)
                r2_scores.append(r2_fold)
            # For single samples, we'll calculate overall R² later

        # Convert to numpy arrays for easier handling
        predictions_all = np.array(predictions_all)
        actuals_all = np.array(actuals_all)
        
        # Calculate overall metrics across all predictions
        overall_r2 = r2_score(actuals_all, predictions_all)
        overall_mse = mean_squared_error(actuals_all, predictions_all)
        overall_mae = mean_absolute_error(actuals_all, predictions_all)
        
        # Store cross-validation results
        self.cv_results = {
            'fold_mse_scores': mse_scores,
            'fold_mae_scores': mae_scores,
            'fold_r2_scores': r2_scores if r2_scores else None,  # None if no fold had >1 sample
            'overall_predictions': predictions_all,
            'overall_actuals': actuals_all,
            'n_folds': len(mse_scores)
        }
        
        # Calculate summary metrics
        self.metrics = {
            'cv_method': cv_method_name,
            'cv_mse_mean': np.mean(mse_scores),
            'cv_mse_std': np.std(mse_scores),
            'cv_mae_mean': np.mean(mae_scores),
            'cv_mae_std': np.std(mae_scores),
            'overall_r2': overall_r2,  # R² calculated on all predictions vs actuals
            'overall_mse': overall_mse,
            'overall_mae': overall_mae,
            'cv_mse_scores': mse_scores,
            'cv_mae_scores': mae_scores
        }

        # Add fold-wise R² statistics only if available
        if r2_scores:
            self.metrics.update({
                'cv_r2_mean': np.mean(r2_scores),
                'cv_r2_std': np.std(r2_scores),
                'cv_r2_scores': r2_scores
            })
        else:
            # For methods like Leave-One-Out, we only have overall R²
            self.metrics.update({
                'cv_r2_mean': overall_r2,
                'cv_r2_std': None,  # Can't calculate std from single overall value
                'cv_r2_scores': None
            })
        
    def predict(self, data):
        """Make predictions on new data."""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # data_clean = data.dropna(subset=[self.target_column] + self.feature_columns)
        X_encoded, _ = self._prepare_data(data, fit_encoders=False)

        # Ensure columns match training data (add missing columns as zeros, drop extras)
        X_encoded = X_encoded.reindex(columns=self.encoded_feature_names, fill_value=0)
        
        if self.scaler is not None:
            X_scaled = self.scaler.transform(X_encoded)
        else:
            X_scaled = X_encoded
        
        predictions = self.model.predict(X_scaled)
        return predictions
    
    def get_metrics(self):
        """Get training metrics."""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        return self.metrics
    
    def get_cv_results(self):
        """Get detailed cross-validation results."""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        return self.cv_results
    
    def get_feature_importance(self):
        """Get feature importance (only for random forest)."""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
                
        return self.metrics.get('feature_importance', {})

    def get_variety_impact(self):
        """
        Get the impact of different apple varieties (only for one-hot encoded random forest).
        
        Returns:
            dict: Variety impacts sorted by importance
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        if self.model_type != 'random_forest' or self.categorical_encoding != 'onehot':
            raise ValueError("Variety impact analysis only available for random forest with one-hot encoding")
        
        feature_importance = self.metrics.get('feature_importance', {})
        
        # Extract variety-related features
        variety_impacts = {}
        for feature_name, importance in feature_importance.items():
            if 'Variety_' in feature_name:
                variety = feature_name.replace('Variety_', '')
                variety_impacts[variety] = importance
        
        # Sort by importance
        return dict(sorted(variety_impacts.items(), key=lambda x: x[1], reverse=True))
