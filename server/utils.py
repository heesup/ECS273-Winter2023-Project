import os
import pandas as pd
import requests

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id , 'confirm': 1 }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def load_dataset(filter=False) -> pd.DataFrame:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(root_dir,"data/mod_data_Q1234_20_21_22.csv")
    if os.path.exists(csv_path):
        pass
    else:
        # Download
        print(f"Download {csv_path}",flush=True)
        file_id = '1UVrnYc6ruKVp-HxNmaPGnX8_XxHAzm3s'
        destination = 'DESTINATION FILE ON YOUR DISK'
        download_file_from_google_drive(file_id, csv_path)
        print(f"...Done!",flush=True)

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