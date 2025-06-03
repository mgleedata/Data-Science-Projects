import pandas 
import requests
from bs4 import BeautifulSoup

url = 'https://nuforc.org/webreports/ndxevent.html '
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

links = soup.find_all('a')[1:]

for link in links:
    url = link.get('href')
    text = link.get_text()
    

# define URL
base_url = 'https://nuforc.org/webreports/'

# define base for URL
url = base_url + 'ndxevent.html'
response = requests.get(url)

# parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# find all table rows
rows = soup.find_all('tr')

# initialize empty dataFrame 
all_data = pd.DataFrame()

# Loop over the rows
for row in rows[1:]:  # skip the header row
   
    link_nonhref = row.find('a')
    link = row.find('a').get('href')
    print(link_nonhref.get_text())
  
    full_url = base_url + link
   
    page = requests.get(full_url)
    page_soup = BeautifulSoup(page.text, 'html.parser')

   
    table = page_soup.find_all('table')
    df = pd.read_html(str(table))[0]
    df['Year Full'] = link_nonhref.get_text()
    
    #concatenate data
    all_data = pd.concat([all_data, df])
    
#initial clean up of "Year Full" and "Data / Time"
    
all_data = all_data[all_data['Year Full'] != 'UNSPECIFIED / APPROXIMATE']
all_data['Year Full'] = pd.to_datetime(all_data['Year Full'], format='%Y', errors='coerce').dt.year
all_data['Date / Time'] = all_data['Date / Time'].dt.replace(year=all_data['Year Full'])
