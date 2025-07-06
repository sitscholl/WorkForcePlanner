from sklearn.ensemble import RandomForestRegressor

from .base import BasePredictor

class RandomForestPredictor(BasePredictor):
    def __init__(self):
        super().__init__()
        self._init_model()

    def _init_model(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = None

    def _get_model_copy(self):
        return RandomForestRegressor(n_estimators=100, random_state=42)

if __name__ == '__main__':

    import matplotlib.pyplot as plt
    from ..data.gsheets import GoogleSheetsHandler

    gsheets = GoogleSheetsHandler()
    gsheets.setup_credentials_from_file('gsheets_creds.json')
    field_data = gsheets.run(
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/1l8lHoWk1VBZ0tzLOQ6JXGxVbD7B37CIN2xbysK_JDCA/edit", 
        worksheet_name = "Wiesen"
        )

    field_data_clean = field_data.dropna(subset=['Hours Zupfen', 'Variety', 'Tree Age', 'Count Zupfen'])

    predictor = RandomForestPredictor()
    metrics = predictor.train(
        data=field_data_clean,
        target_column='Hours Zupfen',
        feature_columns=['Variety', "Tree Age", 'Count Zupfen'],
        categorical_columns=['Variety'],
        cv_method='group_kfold',
        cv_params={'group_column': 'Year', 'n_splits': -1}
    )
    # print(predictor.get_feature_importance())
    # print(predictor.get_metrics())

    print(predictor.get_metrics()['overall_r2'])
    print(predictor.get_metrics()['cv_r2_mean'])

    field_data_clean['predictions'] = predictor.predict(field_data_clean)
    print(field_data_clean)

    plt.plot(field_data_clean['Hours Zupfen'], field_data_clean['predictions'], 'o')
    plt.axline((0,0), slope=1, color = 'red')
    plt.xlabel('Actual Hours')
    plt.ylabel('Predicted Hours')
    plt.title('Actual vs. Predicted')
    plt.savefig('predictions_randfor.png', dpi = 300)