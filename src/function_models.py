import pandas as pd
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.preprocessing import LabelEncoder
import json
import pickle
import numpy as np

def transform(test):
    my_imputer = IterativeImputer()
    label_encoder = LabelEncoder()

    ## Script para conectar con data de Qlik (por ejemplo práctico se ha concatenado los campos)
    with open('./model_data/remove_columns.json','r') as f:
        remove_columns=json.load(f)

    with open('./model_data/str_columns.json','r') as f:
        str_columns=json.load(f)

    for col in str_columns:
        test[col] = test[col].replace('NA', np.nan)
        test[col] = label_encoder.fit_transform(test[col].astype('str'))
    
    for col in test.columns:
        if col not in str_columns:
            test[col] = pd.to_numeric(test[col], errors='coerce')

    test = test.drop(remove_columns, axis=1)
    test_imputed = my_imputer.fit_transform(test)

    return test_imputed

def random_forest(df):

    df_rf = transform(df)

    rf_model = pickle.load(open('./model_data/rf_regressor.pickle','rb'))
    rf_pred = rf_model.predict(df_rf)

    df_final = pd.DataFrame({'Id': df['Id'], 'SalePrice':rf_pred})

    return df_final

def xgboost(df):

    df_xgb = transform(df)

    xgb_model = pickle.load(open('./model_data/xgboost.pickle','rb'))
    xgb_pred = xgb_model.predict(df_xgb)

    df_final = pd.DataFrame({'Id': df['Id'], 'SalePrice':xgb_pred})

    return df_final
