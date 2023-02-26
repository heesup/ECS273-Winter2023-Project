import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from time import time

import seaborn as sns
sns.set(style="whitegrid")

import warnings
warnings.filterwarnings('ignore')

# NOTE: current directory: ECS273-Winter2023/Assignment/Vue-Flask-Template/dashboard

def apply_arima(data: pd.DataFrame, column: str, plot=False):
    arima = ARIMA(data[column], order=(12,1,1))
    predictions = arima.fit().predict()
    
    if plot:
        plt.figure(figsize=(16,4))
        plt.plot(data['Total'], label="Actual")
        plt.plot(predictions, label="Predicted")
        plt.title('Sales in 1000s of Units', fontsize=20)
        plt.ylabel('Sales', fontsize=16)
        plt.legend()
    return predictions

def apply_sarima(data: pd.DataFrame, column: str, plot=False):
    sarima = SARIMAX(data[column],
                order=(1,1,1),
                seasonal_order=(1,1,0,12))
    predictions = sarima.fit().predict()
    
    if plot:
        plt.figure(figsize=(16,4))
        plt.plot(data, label="Actual")
        plt.plot(predictions, label="Predicted")
        plt.title('Sales in 1000s of Units', fontsize=20)
        plt.ylabel('Sales', fontsize=16)
        plt.legend()
    return predictions

###################        Example     ################### 
# sales = prepare_time_template_data()
# arima_prediction = apply_arima(sales, "Total")
# sarima_prediction = apply_sarima(sales, "Total")
##########################################################

def _parser(s):
    return datetime.strptime(s, '%Y-%m-%d')

def prepare_time_template_data(plot=False) -> pd.DataFrame:
    sales = pd.read_csv('../server/data/time_template.csv', parse_dates=[0], index_col=0, date_parser=_parser)

    #plot
    if plot:
        plt.figure(figsize=(14,4))
        plt.plot(sales)
        plt.title('Sales in 1000s of Units', fontsize=20)
        plt.ylabel('Sales', fontsize=16)
        
        plt.rc('figure',figsize=(14,8))
        plt.rc('font',size=15)

        result = seasonal_decompose(sales,model='additive')
        fig = result.plot()
        
        plot_acf(sales['Total'], lags=48);
        plot_pacf(sales['Total'], lags=30);
    return sales