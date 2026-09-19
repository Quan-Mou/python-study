import requests

url = "https://api.apilayer.net/aviationstack/v1/flights"
params = {
    # "access_key": "xxx",
    "limit": "1",
    "offset": "0"
}

response = requests.get(url, params=params)
print(response.url) # 请求地址
print(response.status_code) # 返回的状态码
print(response.reason) 
# response
print(response.json()) # 以json形式返回