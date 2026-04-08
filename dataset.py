import pandas as pd

def load_dataset():
    """
    Loads the employee dataset into a Pandas DataFrame.
    """
    return pd.read_csv("Data/data.csv")