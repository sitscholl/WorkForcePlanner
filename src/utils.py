from .data import GoogleSheetsHandler
from .config import load_model_class
from .worker import Workforce

def load_data(config, param_name):
    gsheets = GoogleSheetsHandler()
    gsheets.setup_credentials_from_file(config['gsheets']['credentials_file'])
    field_data = gsheets.run(
        spreadsheet_url=config['gsheets']['spreadsheet_url'], 
        worksheet_name=config['gsheets']['worksheet_name']
    )

    return field_data

def clean_data(data, config, param_name, include_target = True):
    if include_target:
        return data.dropna(subset=[config[param_name]['target']] + config[param_name]['predictors'])
    else:
        return data.dropna(subset=config[param_name]['predictors'])
    

def train_model(config, param_name, data):

    model = load_model_class(config, param_name)
    predictor = model()
    _ = predictor.train(
        data=data,
        target_column=config[param_name]['target'],
        feature_columns=config[param_name]['predictors'],
        cv_method=config[param_name]['cv_method'],
        cv_params=config[param_name]['cv_params']
    )

    return predictor

def load_workforce(workforce_file):
    if workforce_file.exists():
        workforce = Workforce()
        workforce.load(filename = workforce_file)
        return workforce
    return Workforce()