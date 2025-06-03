import requests
import pandas as pd

# send a get request to the API 
response = requests.get('https://ssd-api.jpl.nasa.gov/cad.api?date-min=1900-01-01&date-max=2023-08-02&diameter=true&fullname=true')

# convert to JSON
data = response.json()

# convert JSON to dataFrame
df = pd.DataFrame(data=data['data'], columns=data['fields'])

# convert dataFrame to a csv file
df.to_csv('neo_updated.csv', index=False)