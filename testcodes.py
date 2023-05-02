import urllib.request
import os

# Download Yemen admin shape file
url = 'https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
req = urllib.request.Request(url, headers=headers)
response = urllib.request.urlopen(req)

# Save the file in temp directory
temp_dir = os.getenv('TEMP')
file_name = os.path.join(temp_dir, 'ne_10m_admin_0_countries.zip')
with open(file_name, 'wb') as f:
    f.write(response.read())

# Open the shape file
iface.addVectorLayer(file_name, 'Yemen Admin', 'ogr')