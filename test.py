import requests

def getTxt(url: str) -> str:
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.text  # Return the content as a string
        else:
            raise Exception(f"Failed to retrieve the file. Status code: {response.status_code}")
    
    except Exception as e:
        # Handle exceptions (e.g., network issues, invalid URL)
        return str(e)
    
print(getTxt("https://pastebin.com/raw/hnugV7hG"))