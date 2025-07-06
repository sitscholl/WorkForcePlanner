from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from .base import BasePredictor

class LinearRegressionPredictor(BasePredictor):
    def __init__(self):
        super().__init__()
        self._init_model()

    def _init_model(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()

    def _get_model_copy(self):
        return LinearRegression()