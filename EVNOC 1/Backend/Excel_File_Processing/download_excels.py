from Excel_File_Processing.sharepoint import SharePoint
import pandas as pd
from datetime import datetime,timedelta
import os

# set the folder name
folder_name = 'Excel_Files'

# For Main File
# set file name
file_nm1 = 'charger_type_counts.xlsx'

date=datetime.now().date().strftime("%Y-%m-%d")
# set file path
file_name1 = f'/home/evadmin/EV_NOC/Backend/app/controllers/{date}.xlsx'

# get file
def get_charger_counts_df_from_file():
    if os.path.isfile(file_name1):
        print("File already downloaded")
        df = pd.read_excel(f'/home/evadmin/EV_NOC/Backend/app/controllers/{date}.xlsx')
    else:
        prev_date=str(datetime.strptime(date,"%Y-%m-%d") - timedelta(1)).split(" ")[0]
        deletefilepath=f'/home/evadmin/EV_NOC/Backend/app/controllers/{prev_date}.xlsx'
        if os.path.isfile(deletefilepath):
            os.remove(deletefilepath)
            print("removed older file")
        file1  = SharePoint().download_file(file_nm1, folder_name)
    # save file
        with open(file_name1, 'wb') as f:
            f.write(file1)
            print("Excel file downloaded successfully -- Main Data File")
            f.close()

        df = pd.read_excel(f'/home/evadmin/EV_NOC/Backend/app/controllers/{date}.xlsx')
    return df




