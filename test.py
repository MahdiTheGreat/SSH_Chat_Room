import pandas as pd

user_records=pd.read_csv("UserRecords.csv")
username="mahdi"
password="1234q"
temp=user_records.query("user_id==@username and password==@password")
print()