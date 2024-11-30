import pandas as pd

df1 = pd.read_csv('airport_routes.csv')
df2 = pd.read_csv('processed_routes_china.csv')
df3 = pd.read_csv('processed_routes_japan.csv')

merged = pd.concat([df1, df2, df3], ignore_index=True)

merged.to_csv('merged_routes.csv', index=False)