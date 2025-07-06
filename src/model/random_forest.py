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

    from ..data.gsheets import GoogleSheetsHandler

    gsheets = GoogleSheetsHandler()
    gsheets.setup_credentials_from_file('gsheets_creds.json')
    field_data = gsheets.run(
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/1l8lHoWk1VBZ0tzLOQ6JXGxVbD7B37CIN2xbysK_JDCA/edit", 
        worksheet_name = "Wiesen"
        )

    predictor = RandomForestPredictor()
    metrics = predictor.train(
        data=field_data,
        target_column='Hours Zupfen',
        feature_columns=['Variety', 'Count Zupfen'],
        cv_method='group_kfold',
        cv_params={'group_column': 'Year', 'n_splits': -1}
    )
    print(metrics)