import os
import pandas as pd

def load_dataset(filter=False) -> pd.DataFrame:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(root_dir,"data/mod_data_Q1234_20_21_22.csv")
    data: dict = pd.read_csv(csv_path)

    if filter:
        data = filter_dataset(data)
    
    return data

def filter_dataset(data:pd.DataFrame()) -> pd.DataFrame:
    # Fill NA
    data = data.fillna(0)
    
    res =  [True for i in range(len(data.columns))]
    for i,col in enumerate(data.columns):
        # if "normalized" in col:
        # #if "raw" in col:
        #     res[i] = False
        # # Value check
        if 'smart' in col:
            if (data[col].min() == 0) & (data[col].max() == 0):
                # print(col)
                res[i] = False
    data = data.iloc[:,res]
    
    # Normalize data
    if 0:
        for i,col in enumerate(data.columns):
            if "raw" in col:
                data[col] = data[col] / data[col].abs().max()

    return data

if __name__ == "__main__":
    dataset = load_dataset()
    dataset = filter_dataset(dataset)
    print(dataset.head())