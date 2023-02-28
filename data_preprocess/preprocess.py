import pandas as pd
import os
import numpy as np
from tqdm import tqdm

def get_filelist(filepath):
    return [f for f in os.listdir(filepath) if os.path.isfile(os.path.join(filepath, f))]

def compare_df(prev_df, next_df):

    prev_set = set(prev_df["serial_number"])
    next_set = set(next_df["serial_number"])
    deleted = prev_set - next_set
    stay = prev_set & next_set
    new = next_set - prev_set

    # Debug
    if 0:
        print(deleted)
        print(new)
        print(list(deleted)[0] in list(prev_df["serial_number"]))
        print(list(new)[0] in list(prev_df["serial_number"]))
        print(list(new)[0] in list(next_df["serial_number"]))

    return list(deleted), list(stay), list(new)

if __name__ == "__main__":
    
    
    if 0:
        #csv_list = ["2022-10-01.csv", "2022-11-01.csv","2022-12-01.csv"]
        csv_list = ["../Dataset/data_Q1_2020/2020-01-01.csv", "../Dataset/data_Q1_2021/2021-01-01.csv", "../Dataset/data_Q1_2022/2022-01-01.csv"]
    elif 0:
        data_root = "../Dataset/data_Q4_2022"
        csv_list = [os.path.join(data_root,x) for x in get_filelist(data_root) if 'csv' in x]
    else:
        data_root = "../Dataset"
        quarters = ["Q1","Q2","Q3","Q4"]
        years = ["2020","2021","2022"]
        csv_list = []
        for year in years:
            for quarter in quarters:
                data_root = os.path.join("../Dataset",f"data_{quarter}_{year}")
                csv_list += [os.path.join(data_root,x) for x in get_filelist(data_root) if 'csv' in x]
        print(len(csv_list))

    prev = []
    failure_records = pd.DataFrame()
    alive_records = pd.DataFrame()
    
    for i, csv_path in enumerate(tqdm(csv_list)):
        date = csv_path.split("/")[-1].split(".")[0]
        df = pd.read_csv(csv_path)
        df = df.fillna(0)
        
        # print(df.head())

        # Compare df if prev exists
        if len(prev) > 0:
            deleted, stay, new  = compare_df(prev, df)

            # Add failure records
            deleted_disks = prev.loc[prev["serial_number"].isin(deleted)]
            #print(deleted_disks.head())
            #print(deleted_disks["failure"])

            failed_disks = prev.loc[prev["serial_number"].isin(deleted) & prev["failure"] == 1]
            #print(failed_disks.head())
            #print(failed_disks["failure"])

            failure_records = pd.concat([failure_records,failed_disks])

        # Update prev
        prev = df

        # If last file
        if i == len(csv_list)-1:
            failed_disks = df.loc[df["failure"] == 1]
            failure_records = pd.concat([failure_records,failed_disks])

            alive_records = df.loc[df["failure"] == 0]
        
            # print(alive_records.head())

    final_df = pd.concat([failure_records, alive_records])
    final_df.to_csv('out.csv')  