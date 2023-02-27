import pandas as pd
import os


def compare_df(prev_df, next_df):
    #compare = prev["serial_number"] == next["serial_number"]
    prev_list = prev_df["serial_number"]
    next_list = next_df["serial_number"]
    stay = [serial for serial in prev_list if serial in next_list]
    deleted = [serial for serial in prev_list if serial not in next_list]
    new = [serial for serial in next_list if serial not in prev_list]

    # print(stay)
    # print(deleted)
    # print(new)
    

if __name__ == "__main__":
    
    data_root = "../Dataset/data_Q4_2022"
    csv_list = ["2022-10-01.csv", "2022-10-02.csv"]
    prev = []
    for csv_file in csv_list:
        csv_path = os.path.join(data_root, csv_file)
        date = csv_file.split(".")[0]
        df = pd.read_csv(csv_path)
        df = df.fillna(0)
        
        print(df.head())

        # Compare df if prev exists
        if len(prev) > 0:
            compare_df(prev, df)

        prev = df
            