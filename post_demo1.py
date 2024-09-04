import requests

url = 'http://127.0.0.1:5007/compressed_oxygen_status'


response = requests.get(url)

if response.status_code == 200:
    print(response.text)
else:
    print(response.text)