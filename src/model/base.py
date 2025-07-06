import numpy as np
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
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.target_column = None
        self.is_trained = False
        self.metrics = {}
        self.cv_results = {}

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
        Train the model on the provided data with flexible cross-validation.
        
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
        # Store column information
        self.target_column = target_column
        self.feature_columns = feature_columns
        
        # Prepare data
        data_clean = data.dropna(subset=[target_column] + feature_columns)
        X = data_clean[feature_columns].copy()
        y = data_clean[target_column].copy()
        
        # Handle missing values
        # X = X.fillna(X.mean())
        # y = y.fillna(y.mean())
        
        # Set default cv_params if not provided
        if cv_params is None:
            cv_params = {}
        
        # Perform cross-validation based on method
        if cv_method == 'simple_split':
            self._simple_split_validation(X, y, cv_params, random_state)
        elif cv_method == 'kfold':
            self._kfold_validation(X, y, cv_params, random_state)
        elif cv_method == 'leave_one_out':
            self._leave_one_out_validation(X, y)
        elif cv_method == 'group_kfold':
            self._group_kfold_validation(X, y, data_clean, cv_params, random_state)
        elif cv_method == 'time_series':
            self._time_series_validation(X, y, cv_params)
        else:
            raise ValueError(f"Unknown cv_method: {cv_method}")
        
        # Train final model on all data
        if self.scaler is not None:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = X
        
        self.model.fit(X_scaled, y)
        
        # Add feature importance for random forest
        if self.model_type == 'random_forest':
            feature_importance = dict(zip(feature_columns, self.model.feature_importances_))
            self.metrics['feature_importance'] = feature_importance
        
        self.is_trained = True
        return self.metrics
    
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
            
            # Calculate metrics
            r2_scores.append(r2_score(y_test_fold, y_pred))
            mse_scores.append(mean_squared_error(y_test_fold, y_pred))
            mae_scores.append(mean_absolute_error(y_test_fold, y_pred))
        
        # Store cross-validation results
        self.cv_results = {
            'r2_scores': r2_scores,
            'mse_scores': mse_scores,
            'mae_scores': mae_scores,
            'n_folds': len(r2_scores)
        }
        
        # Calculate summary metrics
        self.metrics = {
            'cv_method': cv_method_name,
            'cv_r2_mean': np.mean(r2_scores),
            'cv_r2_std': np.std(r2_scores),
            'cv_mse_mean': np.mean(mse_scores),
            'cv_mse_std': np.std(mse_scores),
            'cv_mae_mean': np.mean(mae_scores),
            'cv_mae_std': np.std(mae_scores),
            'cv_r2_scores': r2_scores,
            'cv_mse_scores': mse_scores,
            'cv_mae_scores': mae_scores
        }
        
    def predict(self, data):
        """Make predictions on new data."""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X = data[self.feature_columns].copy()
        X = X.fillna(X.mean())
        
        if self.scaler is not None:
            X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X
        
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
        
        if self.model_type != 'random_forest':
            raise ValueError("Feature importance only available for random forest model")
        
        return self.metrics.get('feature_importance', {})
