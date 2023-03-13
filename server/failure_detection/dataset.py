import torch
from torch.utils.data import Dataset
import pandas as pd

import sys, os
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir,"../"))
from utils import load_dataset

class HddSmartDataset(Dataset):

    def __init__(self,use_raw=True,use_normalized=True,use_mfg=True):

        self.data_df = load_dataset(filter=True)
        self.targets = self.data_df['failure']

        self.data_values = self.data_df
        if use_mfg:
            self.data_values = pd.get_dummies(self.data_values, columns = ['MFG'])
            
        res =  [False for i in range(len(self.data_values.columns))]
        for i,col in enumerate(self.data_values.columns):
            if use_mfg:
                if "MFG_" in col:
                    res[i] = True
            if use_raw:
                if "raw" in col:
                    res[i] = True
            if use_normalized:
                if "normalized" in col:
                    res[i] = True
                    self.data_values[col]/=100
        self.data_values = self.data_values.iloc[:,res]
        print(self.data_values.head())

        pass

    def __len__(self):
        return len(self.data_df)

    def __getitem__(self, index):
        label = self.targets[index]
        target = torch.zeros(2)
        target[label] = 1.0

        values = torch.FloatTensor(self.data_values.iloc[index])

        return label, values, target


if __name__ == "__main__":
    dataset = HddSmartDataset()

    for label, values, target in dataset:
        print(label,values, target )
        break