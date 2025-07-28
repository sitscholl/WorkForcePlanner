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

if __name__ == '__main__':

    import matplotlib.pyplot as plt
    from ..data.gsheets import GoogleSheetsHandler
    from ..config import load_config

    config = load_config('config/config.yaml')

    gsheets = GoogleSheetsHandler()
    gsheets.setup_credentials_from_file('gsheets_creds.json')
    field_data = gsheets.run(
        spreadsheet_url = config['gsheets']['spreadsheet_url'], 
        worksheet_name = config['gsheets']['worksheet_name']
        )

    field_data_clean = field_data.dropna(subset=[config['model']['target']] + config['model']['predictors'])

    predictor = LinearRegressionPredictor()
    metrics = predictor.train(
        data=field_data_clean,
        target_column=config['model']['target'],
        feature_columns=config['model']['predictors'],
        cv_method=config['model']['cv_method'],
        cv_params=config['model']['cv_params']
    )
    # print(predictor.get_feature_importance())
    # print(predictor.get_metrics())

    print(predictor.get_metrics()['overall_r2'])
    print(predictor.get_metrics()['cv_r2_mean'])

    field_data_clean['predictions'] = predictor.predict(field_data_clean)
    # print(field_data_clean)

    plt.plot(field_data_clean[config['model']['target']], field_data_clean['predictions'], 'o')
    plt.axline((0,0), slope=1, color = 'red')
    plt.xlabel('Actual Hours')
    plt.ylabel('Predicted Hours')
    plt.title('Actual vs. Predicted')
    plt.savefig('predictions_linreg.png', dpi = 300)