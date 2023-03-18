import pandas as pd
import numpy as np
import os

from utils import load_dataset, filter_dataset, download_file_from_google_drive
from lifelines import KaplanMeierFitter
from humanize import naturalsize
from failure_detection.survival_model import make_model

from sklearn.decomposition import PCA
from sklearn import preprocessing

def perform_PCA(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    scaler = preprocessing.StandardScaler()
    X = scaler.fit_transform(X)

    pca = PCA(n_components=2)
    pca.fit(X)  # Learn the projection matrix
    Z = pca.transform(X) # Project the given data with the learnt projection matrix
    
    PC1, PC2 = pca.components_ # Since n_components = 2
    PCs = np.vstack((PC1.reshape(1, -1), PC2.reshape(1, -1))) # Rows refer to each PC; Columns refer to each data attribute
    return Z, PCs

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


def processExample(mfg: str = 'All') -> tuple[list[dict], list[int]]:

    global dataset
    data = dataset.copy()
    if mfg == "All":
        pass
    elif mfg in ['Seagate', 'TOSHIBA', 'HGST', 'WDC', 'Micron', 'HP', 'Hitachi', 'DELLBOSS']:
        data = data[data["MFG"] == mfg]
    else:
        raise ValueError("Requested a method that is not supported")
    #print(data.head())
    #print(data.shape, flush=True)
    data.reset_index(drop=True, inplace=True) # Solve Missing index problem
    
    res =  [False for i in range(len(data.columns))]
    for i,col in enumerate(data.columns):
        if 'smart' in col:
            res[i] = True
    X: np.ndarray = data.iloc[:,res] # From smart_1_normalized

    y: np.ndarray = data["failure"]
    #feat_names: np.ndarray = data.feature_names
    target_names: np.ndarray = ["healthy","failure"]

    Z, PCs = perform_PCA(X)
    
    PC1 = list(PCs[0])
    PC2 = list(PCs[1])
    i1 = PC1.index(max(PCs[0]))
    i2 = PC2.index(max(PCs[1]))
    # print(data.iloc[:,6:-1].columns[i1])
    # print(data.iloc[:,6:-1].columns[i2])
    #print(PCs)

    points = pd.DataFrame(Z, columns=['posX', 'posY'])
    #print("************y***********",flush=True)
    #print(y,flush=True)
    points['cluster'] = y
    #print(points.shape, flush=True)
    #print(points, flush=True)
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

    if os.path.exists(csv_path):
        pass
    else:
        # Download
        print(f"Download {csv_path}",flush=True)
        file_id = '1-0RfmKMbE2eXQ_tj9hnGdBT-RxychNz0'
        download_file_from_google_drive(file_id, csv_path)
        print(f"...Done!",flush=True)
        
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


def processKMSurvivalCurveSerialData(manufacturer):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(root_dir, 'data/pdsurv_2020_2022.csv')
    pdsurv = pd.read_csv(csv_path)
    print('[INFO] Data load count : ', pdsurv.count())

    YEARS = 365.25
    res_df = pd.DataFrame(columns=['MFG', 'label','capacity', 'x', 'y', 'y_upper', 'y_lower'])

    mask = pdsurv['manufacturer'] == manufacturer
    gcols = ["model_introduced", "model_capacity", "model"]
    capacity_category = []
    for group, grouped_df in pdsurv[mask].groupby(gcols):

        # Get last model value
        model_introduced, model_capacity, model = group

        model_list = model.split()

        if(len(model_list) > 1) and  ( manufacturer == 'Seagate' or manufacturer == 'Hitachi' or manufacturer == 'TOSHIBA' or manufacturer == 'WDC') :
            model = model_list[-1]
            if model == 'HN' and len(model) == 2 and manufacturer == 'Seagate':
                model = model_list[0]
            
            if model == 'SSD' and manufacturer == 'Seagate':
                model = manufacturer+model

        if len(grouped_df) < 100:
            # skip small sample groups
            continue

        label = f"{model} ({naturalsize(model_capacity)}, {model_introduced[:4]})"
        capacity = naturalsize(model_capacity)
        capacity_category.append(capacity)
        kmf = KaplanMeierFitter()
        kmf.fit(grouped_df['duration'] / YEARS, grouped_df['failure'])

        confidence_intervals = kmf.confidence_interval_

        x = kmf.survival_function_.index.values
        y = kmf.survival_function_['KM_estimate'].values
        y_upper = confidence_intervals['KM_estimate_upper_0.95'].values
        y_lower = confidence_intervals['KM_estimate_lower_0.95'].values

        for i in range(len(x)):
            new_row = {'MFG': manufacturer, 'label': label,'capacity':capacity, 'x': x[i], 'y': y[i], 'y_upper': y_upper[i], 'y_lower': y_lower[i]}
            res_df.loc[len(res_df)] = new_row

    y: np.ndarray = res_df['label']
    capacity_category = list(set(capacity_category))
    capacity_category.sort(key=lambda x:float(x.split(' ')[0])*1000 if x.split(' ')[-1] =='TB' else float(x.split(' ')[0]))
    #print(capacity_category)

    res_df = make_model(res_df)
    print(res_df.tail())

    return res_df.to_dict(orient='records'), list(y.drop_duplicates()), capacity_category


# Load dataset globally
dataset = load_dataset()
dataset = filter_dataset(dataset)

if __name__ == "__main__":
    # For debugging
    # processExample()
    #processBarChart()
    #processExample("Seagate")
    processKMSurvivalCurveSerialData("Seagate")