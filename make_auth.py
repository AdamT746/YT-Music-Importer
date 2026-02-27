import json

auth_data = {
    "User-Agent": "",
    "Accept": "*/*",
    "Accept-Language": "",
    "Content-Type": "",
    "X-Goog-AuthUser": "",
    "x-origin": "",
    "Authorization": "",
    "Cookie": ""
}

with open("headers_auth.json", "w") as f:
    json.dump(auth_data, f, indent=4)
    
print("SUCCESS: headers_auth.json correctly formatted and created!")