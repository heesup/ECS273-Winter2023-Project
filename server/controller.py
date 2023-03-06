import pandas as pd
import numpy as np
from sklearn.datasets import load_wine
from resources.hd_processing_template import perform_PCA, perform_TSNE
#from resources.network_process_template import contsruct_networkx
#from resources.text_processing_template import preprocess
#from resources.time_processing_template import prepare_time_template_data, apply_arima, apply_sarima
import os


def filter_dataset(data):

    res =  [True for i in range(len(data.columns))]
    for i,col in enumerate(data.columns):
        if "normalized" in col:
        #if "raw" in col:
            res[i] = False

        # Value check
        if 'smart' in col:
            if (data[col].min() == 0) & (data[col].max() == 0):
                # print(col)
                res[i] = False

    data = data.iloc[:,res]
    data = data.fillna(0)
    
    if 0:
        for i,col in enumerate(data.columns):
            if "raw" in col:
                data[col] = data[col] / data[col].abs().max()

    return data

def load_dataset():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(root_dir,"data/mod_data_Q1234_20_21_22.csv")
    data: dict = pd.read_csv(csv_path)
    return data

def processBarChart() -> tuple[list[dict], list[int]]:

    data = load_dataset()
    data = filter_dataset(data)

def processExample(method: str = 'PCA') -> tuple[list[dict], list[int]]:

    data = load_dataset()
    data = filter_dataset(data)
    res =  [False for i in range(len(data.columns))]
    for i,col in enumerate(data.columns):
        if 'smart' in col:
            res[i] = True
    X: np.ndarray = data.iloc[:,res] # From smart_1_normalized
    # print(X.head())

    y: np.ndarray = data["failure"]
    #feat_names: np.ndarray = data.feature_names
    target_names: np.ndarray = ["failure","healthy"]

    if method == 'PCA':
        Z, PCs = perform_PCA(X)
        PC1 = list(PCs[0])
        PC2 = list(PCs[1])
        i1 = PC1.index(max(PCs[0]))
        i2 = PC2.index(max(PCs[1]))
        # print(data.iloc[:,6:-1].columns[i1])
        # print(data.iloc[:,6:-1].columns[i2])
        #print(PCs)
    elif method == 't-SNE':
        Z = perform_TSNE(X, perplexity = 10)
    else:
        raise ValueError("Requested a method that is not supported")
    points = pd.DataFrame(Z, columns=['posX', 'posY'])
    points['cluster'] = y
    # How to JSON serialize pandas dataframes and numpy arrays
    return points.to_dict(orient='records'), list(target_names)


if __name__ == "__main__":
    processExample()