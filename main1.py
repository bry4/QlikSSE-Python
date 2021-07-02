from src import *
import pandas as pd

data = pd.read_csv("data/test.csv")

result = random_forest(data)

print(result)

#print(data)
#print(data.select_dtypes("O").columns)
