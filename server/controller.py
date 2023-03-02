import pandas as pd
import numpy as np
from sklearn.datasets import load_wine
from resources.hd_processing_template import perform_PCA, perform_TSNE
#from resources.network_process_template import contsruct_networkx
#from resources.text_processing_template import preprocess
#from resources.time_processing_template import prepare_time_template_data, apply_arima, apply_sarima
import os


def processExample(method: str = 'PCA') -> tuple[list[dict], list[int]]:
    root_dir = os.path.dirname(os.path.abspath(__file__))

    csv_path = os.path.join(root_dir,"data/data_Q1234_20_21_22.csv")
    data: dict = pd.read_csv(csv_path)
    data = data.fillna(0)
    X: np.ndarray = data.iloc[:,6:] # From smart_1_normalized
    print(X.head())
    y: np.ndarray = data["failure"]
    #feat_names: np.ndarray = data.feature_names
    target_names: np.ndarray = ["failure","healthy"]

    if method == 'PCA':
        Z, PCs = perform_PCA(X)
        print(PCs)
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