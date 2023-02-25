import requests
import json
import socket
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
# URL to send the request to
request_url = 'https://api.ipgeolocation.io/ipgeo?apiKey=264dc73d2ac44acf98985ed04c85b2cf'
response = requests.get(request_url)
result = json.loads(response.content)
print(result)
info = {
    'city': result['city'],
    'country': result['country'],
    'continent': result['continent'],
    'is_vpn': result['security']['is_vpn']
    }

for i in info:
    print(i, ":", info[i])
