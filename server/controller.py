import pandas as pd
import numpy as np
from sklearn.datasets import load_wine
from resources.hd_processing_template import perform_PCA, perform_TSNE
#from resources.network_process_template import contsruct_networkx
#from resources.text_processing_template import preprocess
#from resources.time_processing_template import prepare_time_template_data, apply_arima, apply_sarima

def processExample(method: str = 'PCA') -> tuple[list[dict], list[int]]:
    data: dict = load_wine()
    X: np.ndarray = data.data
    y: np.ndarray = data.target
    #feat_names: np.ndarray = data.feature_names
    target_names: np.ndarray = data.target_names

    if method == 'PCA':
        Z, _ = perform_PCA(X)
    elif method == 't-SNE':
        Z = perform_TSNE(X, perplexity = 10)
    else:
        raise ValueError("Requested a method that is not supported")
    points = pd.DataFrame(Z, columns=['posX', 'posY'])
    points['cluster'] = y
    # How to JSON serialize pandas dataframes and numpy arrays
    return points.to_dict(orient='records'), list(target_names)
