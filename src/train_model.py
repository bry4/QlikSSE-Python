import pandas as pd
import numpy as np
import pickle
import sidetable
from sklearn.preprocessing import LabelEncoder
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import xgboost as xgb
import json

def main():

    ## Handling categorical variables
    label_encoder = LabelEncoder()

    ## Training data
    train = pd.read_csv('./data/train.csv')

    with open('./model_data/str_columns.json', 'w') as f:
        json.dump(list(train.select_dtypes("O").columns), f)

    for col in train.select_dtypes("O").columns:
        train[col] = label_encoder.fit_transform(train[col].astype('str'))

    ## Missing and Unnecesary Data
    missing_df = train.stb.missing()

    corr_df = train.corrwith(train["SalePrice"],method ='pearson').abs() * 100
    remove_columns = list(corr_df[corr_df > 50].index)
    remove_columns.remove('SalePrice')

    train = train.drop(remove_columns, axis=1)

    ### Imputing Null Values
    my_imputer = IterativeImputer()
    train_imputed = my_imputer.fit_transform(train.drop('SalePrice', axis=1))

    ## Train Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        train_imputed, train['SalePrice'], test_size=0.25, random_state=42
    )

    ## Random Forest Regressor
    rf_regressor = RandomForestRegressor(n_estimators = 100, random_state=42)
    rf_regressor.fit(X_train, y_train)

    filename = './model_data/rf_regressor.pickle'
    pickle.dump(rf_regressor, open(filename, 'wb'))

    ## XGBoost
    xgb_model = xgb.XGBRegressor(learning_rate=0.01,
                            n_estimators=1000,
                            max_depth = 10)
    xgb_model.fit(X_train,y_train)

    filename = './model_data/xgboost.pickle'
    pickle.dump(xgb_model, open(filename, 'wb'))

    ## Score
    csv_score = pd.DataFrame(data={
        'model': ['Random Forest','XGBoost'],
        'score': [rf_regressor.score(X_test, y_test),xgb_model.score(X_test, y_test)]})

    csv_score.to_csv('./model_data/score.csv',index=False)

    with open('./model_data/remove_columns.json', 'w') as f:
        json.dump(remove_columns, f)

if __name__ == '__main__':

    try:
        main()
    except Exception as e:
        print("Error: ",e)

