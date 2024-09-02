import requests

url = 'http://172.16.20.163:5007/compressed_oxygen_detection'


response = requests.get(url)

if response.status_code == 200:
    print(response.text)
else:
    print(response.text)