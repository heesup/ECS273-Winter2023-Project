from csv import writer
from csv import reader
new_column_text = 'Something text'

def get_MFG_vale(model):
    # CT - Crucial Technology but also Micron Technology 
    # MT - Micron Technology
    # ST - Seagate Technology
    mfg_str = 'None'

    model_dvd_str = model.split(" ")
    if len(model_dvd_str) >= 2 and model_dvd_str[1] != "HN":
        mfg_str = model_dvd_str[0]
        if mfg_str == 'WD':
            mfg_str = 'WDC'
    else:
        if model_dvd_str[0][:2] == 'CT':
            mfg_str = 'Micron'
        elif model_dvd_str[0][:2] == 'MT':
            mfg_str = 'Micron'
        elif model_dvd_str[0][:2] == 'ST':
            mfg_str = 'Seagate'

    if mfg_str == 'None':
        print(model)
    return mfg_str


with open('data_Q1234_20_21_22.csv', 'r') as read_object, \
    open('mod_data_Q1234_20_21_22.csv', 'w', newline='') as write_object:
    csv_reader = reader(read_object)
    csv_writer = writer(write_object)
    cnt = 0
    for row in csv_reader:
        if cnt == 0:
            row.append('MFG')
        else:
            mfg_org = row[3]
            row.append( get_MFG_vale(mfg_org) )
            csv_writer.writerow(row)
        cnt = cnt + 1
