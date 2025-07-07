from .data import GoogleSheetsHandler
from .config import load_model_class
from .worker import Workforce

def load_data_and_train_model(config, param_name):
    model = load_model_class(config, param_name)

    gsheets = GoogleSheetsHandler()
    gsheets.setup_credentials_from_file('gsheets_creds.json')
    field_data = gsheets.run(
        spreadsheet_url=config['gsheets']['spreadsheet_url'], 
        worksheet_name=config['gsheets']['worksheet_name']
    )

    field_data_clean = field_data.dropna(subset=[config[param_name]['target']] + config[param_name]['predictors'])

    predictor = model()
    _ = predictor.train(
        data=field_data_clean,
        target_column=config[param_name]['target'],
        feature_columns=config[param_name]['predictors'],
        cv_method=config[param_name]['cv_method'],
        cv_params=config[param_name]['cv_params']
    )

    field_data_clean['predicted_hours'] = predictor.predict(field_data_clean)

    return predictor, field_data_clean

def load_workforce(workforce_file):
    if workforce_file.exists():
        workforce = Workforce()
        workforce.load(filename = workforce_file)
        return workforce
    return Workforce()