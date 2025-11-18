import pandas as pd

#df = pd.read_parquet("out_entities/articles/gkg_raw.parquet")
#print(df.shape)         # number of rows, columns
#print(df.columns)       # column names
#print(df.head())        # first 5 rows

#df = pd.read_parquet("theme_id_map.parquet")
#print(df.shape)         # number of rows, columns
#print(df.columns)       # column names
#print(df.head())        # first 5 rows

def __settings(display: bool):
    if(display):
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

def __show_parquet(path: str):
    df = pd.read_parquet(path)
    print(df.shape)         # number of rows, columns  
    print(df.columns)       # column names
    print(df)        # first 5 rows

def main():
    settings=int(input("Please Select:\n1| Display Some\n2| Display All\n"))
    settings=settings-1
    __settings(settings)
    target_file = int(input("Please choose a parquet to view:\n1| articles\n2| locations\n3| orgs\n4| persons\n5| theme_id_map\n6| theme_list\n"))
    path=""
    if(target_file==1):
        path="GDELT/out_entities/articles/gkg_raw.parquet"
    elif(target_file==2):
        path="GDELT/out_entities/locations/gkg_locations.parquet"
    elif(target_file==3):
        path="GDELT/out_entities/orgs/gkg_orgs.parquet"
    elif(target_file==4):
        path="GDELT/out_entities/persons/gkg_persons.parquet"
    elif(target_file==5):
        path="GDELT/theme_id_map.parquet"
    elif(target_file==6):
        path="GDELT/theme_list.parquet"
    else:
        print("Error: invalid path\npath: " + path)
        return
    
    __show_parquet(path)
    return