import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import summary_table
import numpy as np

def make_model(data):

    capacity_category = list(set(data['capacity']))
    capacity_category.sort(key=lambda x:float(x.split(' ')[0])*1000 if x.split(' ')[-1] =='TB' else float(x.split(' ')[0]))

    for capacity in capacity_category:
        print(capacity,flush=True)

        capacity_data = data[data['capacity'] == capacity]
        #print(capacity_data.head())
        if 0:
            formula = 'y ~ x'
            model = smf.glm(formula = formula, data=capacity_data, family=sm.families.Binomial())
        else:
            model = sm.OLS(capacity_data.y, sm.add_constant(capacity_data.x))
        result = model.fit()
        # print(result.summary())
        # Make GLM
        simulated_x = np.linspace(0,6,10)
        predictions = result.predict()
        sm_pred = result.get_prediction(sm.add_constant(simulated_x))\
                  .summary_frame(alpha=0.1)
        # print(sm_pred.head())

        mfg = ["Simulation" for i in range(len(simulated_x))]
        label = [f"Simulation ({capacity})" for i in range(len(simulated_x))]
        capacity_list = [capacity for i in range(len(simulated_x))]
        simulated = pd.DataFrame({"MFG":mfg,"label":label,"capacity":capacity_list,
                                  "x":simulated_x, "y":sm_pred["mean"],
                                   "y_upper":sm_pred["mean_ci_upper"],
                                   "y_lower":sm_pred["mean_ci_lower"]})
        
        simulated.sort_values(by=['x'],inplace=True)
        data = pd.concat([data, simulated])
        # print(data.head())
        print(data.tail(),flush=True)
        

    return data

    