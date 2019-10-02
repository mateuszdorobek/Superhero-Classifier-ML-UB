# Imports

import numpy as np
import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt

# Load Data

def load_data() -> pd.Series:
    csv_train = pd.read_csv('superhero-or-supervillain/train.csv').assign(train = 1) 
    csv_test = pd.read_csv('superhero-or-supervillain/test.csv').assign(train = 0) 
    csv = pd.concat([csv_train,csv_test], sort=True)
    return csv

# Analyze Data

def nans_ctr(csv) -> pd.Series:
    return csv.isna().sum()

def unique_ctr(csv) -> pd.Series():
    unique = pd.Series()
    for col in list(csv):
        if(csv.columns.contains(col)):
            unique.at[col] = len(csv[col].unique())
    return unique

def val_types(csv) -> pd.Series():
    val_type = pd.Series()
    for col in list(csv):
        if not csv.columns.contains(col):
            continue
        if csv[col].dtype == np.float64:
            val_type.at[col] = np.float64
        elif csv[col].dtype == np.int64:
            val_type.at[col] = np.int64
        elif csv[col].dtype == np.int32:
            val_type.at[col] = np.int32
        elif csv[col].dtype == object:
            val_type.at[col] = object
        elif csv[col].dtype == bool:
            val_type.at[col] = bool
        else:
            print(f"No common value type found in val_types() - {csv[col].dtype}")
    return val_type

def min_max_val(csv) -> pd.Series():
    min_val = pd.Series()
    max_val = pd.Series()
    val_type = val_types(csv)
    for col in list(csv):
        if val_type[col] != object:
            min_val.at[col] = csv[col].min()
            max_val.at[col] = csv[col].max()
        else:    
            min_val.at[col] = None
            max_val.at[col] = None
    return min_val, max_val        
            
def get_stats(csv):
    nans = nans_ctr(csv)
    unique = unique_ctr(csv)
    val_type = val_types(csv)
    min_val, max_val = min_max_val(csv)
    result = pd.DataFrame({ 'nans': nans, 'unique': unique, 'val_type': val_type, 'min_val': min_val, 'max_val': max_val}) 
    return result
    
def bool_to_integer(csv, stats) -> pd.DataFrame():
    for col in csv.columns:
        if csv[col].dtype == bool:
            csv[col] = csv[col].astype(int)
    return csv

if __name__ == "__main__":
    csv = load_data()
    stats = get_stats(csv)
    print(*(stats["val_type"].unique()),sep="\n")
    with pd.option_context('display.max_rows', 500, 'display.max_columns', 500, 'display.width', 1000):
        print(stats)