import requests

url = "http://wpage.unina.it/cotroneo/"

# User Agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  

    # If the request is successful, save the content
    with open("cotroneo.html", "wb") as f:
        f.write(response.content)

except requests.exceptions.HTTPError as err:
    print(f"HTTP Error: {err}")
except Exception as err:
    print(f"An error occurred: {err}")