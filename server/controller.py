import pandas as pd
import numpy as np
from sklearn.datasets import load_wine
from resources.hd_processing_template import perform_PCA, perform_TSNE
#from resources.network_process_template import contsruct_networkx
#from resources.text_processing_template import preprocess
#from resources.time_processing_template import prepare_time_template_data, apply_arima, apply_sarima
import os

from utils import load_dataset, filter_dataset
from lifelines import KaplanMeierFitter


def processBarChart(method: str = 'failure') -> tuple[list[dict], list[int]]:

    global dataset 
    data = dataset.copy()

    # Additional filtering
    data = data[(data["capacity_bytes"] > 0)]
    data["capacity_TB"] = data["capacity_bytes"] //1000//1000//1000/1000
    data = data[data["capacity_TB"] >= 2]
   
    data["power_on_years"] = data["smart_9_raw"] / 24 / 365

    # Do Processing
    if method == "count":
        table = data.pivot_table( values = 'failure', index = ['MFG', 'capacity_TB'],aggfunc=len)
    elif method == 'failure':
        table = data.pivot_table( values = 'failure', index = ['MFG', 'capacity_TB'],aggfunc=np.mean)
    else:
        # power_on_years
        table = data.pivot_table( values = method, index = ['MFG', 'capacity_TB'],aggfunc=np.mean)

    table.columns = ['value']
    table["cluster"] = table.index

    return table.to_dict(orient='records'), list(table.index)


def processExample(method: str = 'PCA') -> tuple[list[dict], list[int]]:

    global dataset
    data = dataset.copy()

    res =  [False for i in range(len(data.columns))]
    for i,col in enumerate(data.columns):
        if 'smart' in col:
            res[i] = True
    X: np.ndarray = data.iloc[:,res] # From smart_1_normalized
    # print(X.head())

    y: np.ndarray = data["failure"]
    #feat_names: np.ndarray = data.feature_names
    target_names: np.ndarray = ["healthy","failure"]

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
    if 0:
        points = pd.DataFrame(Z, columns=['posX', 'posY'])
        points['cluster'] = y
    else:
        # For debug speed-up
        if 0:
            test_sample = 100
            points = pd.DataFrame(Z[:test_sample], columns=['posX', 'posY'])
            points['cluster'] = y[:test_sample]
        else:
            points = pd.DataFrame(Z, columns=['posX', 'posY'])
            points['cluster'] = y

    # How to JSON serialize pandas dataframes and numpy arrays
    return points.to_dict(orient='records'), list(target_names)


def processParallelData(manufacturer: str = 'all') -> tuple[list[dict], list[int]]:

    global dataset 
    data = dataset.copy()
    # prll_data: dict = pd.read_csv(csv_path, usecols=['smart_5_normalized','smart_187_normalized','smart_188_normalized','smart_197_normalized','smart_198_normalized','MFG','failure'])
    # prll_data: dict = pd.read_csv(csv_path, usecols=['smart_1_normalized', 'smart_3_normalized', 'smart_5_normalized', 'smart_7_normalized', 'smart_194_normalized','smart_197_normalized','smart_198_normalized','MFG'])

    # prll_data = data[['smart_1_normalized', 'smart_3_normalized', 'smart_5_normalized', 'smart_7_normalized', 'smart_9_normalized','smart_194_normalized', 'smart_197_normalized', 'smart_198_normalized','MFG','failure']]
    prll_data = data[['smart_5_normalized','smart_187_normalized','smart_188_normalized','smart_197_normalized','smart_198_normalized','MFG','failure']]

    print(manufacturer)

    if manufacturer != 'All':
        prll_data = prll_data[prll_data['MFG'] == manufacturer]

    # For test - reduce loaded data size
    # prll_data = prll_data.iloc[:10000]

    # Do Processing
    res_data = pd.DataFrame(data=prll_data)
    #y: np.ndarray = manufacturer_data
    # y: np.ndarray = prll_data['MFG']
    y: np.ndarray = prll_data['failure']

    return res_data.to_dict(orient='records'), list(y.drop_duplicates()), prll_data.columns.tolist()


def processKMSurvivalCurveData():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(root_dir, 'data/pdsurv_2020_2022.csv')

    pdsurv = pd.read_csv(csv_path)
    grp_pdsurv = pdsurv.groupby("manufacturer")
    YEARS = 365.25

    res_df = pd.DataFrame(columns=['MFG', 'x', 'y', 'y_upper', 'y_lower'])

    for name, grouped_df in grp_pdsurv:
        # skip small sample manufacturers
        if len(grouped_df) < 100:
            continue
        
        kmf = KaplanMeierFitter()
        kmf.fit(grouped_df.duration/YEARS,  event_observed=grouped_df.failure)
        
        confidence_intervals = kmf.confidence_interval_

        x = kmf.survival_function_.index.values
        y = kmf.survival_function_['KM_estimate'].values
        y_upper = confidence_intervals['KM_estimate_upper_0.95'].values
        y_lower = confidence_intervals['KM_estimate_lower_0.95'].values

        for i in range(len(x)):
            new_row = {'MFG': name, 'x': x[i], 'y': y[i], 'y_upper': y_upper[i], 'y_lower': y_lower[i]}
            res_df.loc[len(res_df)] = new_row

    y: np.ndarray = res_df['MFG']
    return res_df.to_dict(orient='records'), list(y.drop_duplicates())

# Load dataset globally
dataset = load_dataset()
dataset = filter_dataset(dataset)

if __name__ == "__main__":
    # For debugging
    # processExample()
    processBarChart()