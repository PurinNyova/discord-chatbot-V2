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
    
print(getTxt("https://cdn.discordapp.com/attachments/1176437973487726612/1318479486387224646/personality.txt?ex=67627935&is=676127b5&hm=f0273242feed422bc5fa215e3b735fce75257b498bd01efc10ed2993f5ce09e3&"))