import requests

url = "https://api.redgifs.com/v2/auth/temporary"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    token = data["token"]

    with open("token.txt", "w") as file:
        file.write(token)
        print("Token saved successfully.")
else:
    print("Failed to retrieve token. Status code:", response.status_code)
