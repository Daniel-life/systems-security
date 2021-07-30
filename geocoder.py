import requests
import json
import socket

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

# Your API key, available from your account page
YOUR_GEOLOCATION_KEY = '3b1399cd7b1947a0a2b8fd3a3f92e285'

# URL to send the request to
request_url = 'https://ipgeolocation.abstractapi.com/v1/?api_key=' + YOUR_GEOLOCATION_KEY
# Send request and decode the result
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
