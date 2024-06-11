from business_app import *
"""import os
import pandas as pd
from io import BytesIO
directory_path = "business_app/files/trial_balances/"
xlsx_files = [file for file in os.listdir(directory_path) if file.endswith('.xlsx')]

excel_writer = pd.ExcelWriter('combined_files.xlsx')

for i, file_name in enumerate(xlsx_files):
    print(file_name)
    file_path = os.path.join(directory_path, file_name)
    with open(file_path, 'rb') as f:
        file_data = BytesIO(f.read())
        df = pd.read_excel(file_data)
        df.to_excel(excel_writer, sheet_name=file_name, index=False)

excel_writer._save()
"""