import requests
import os
import re
import json
import subprocess

def download_redgif_content(a_element, media_url, author_folder, post_id):

    # Extract the GIF IDs from the href attributes
    if "redgifs.com" in media_url:
        gif_id = media_url.split("/")[-1]
        print("GIF ID:", gif_id)
    else:
        print("Not a redgifs.com URL")

    # Download GIF content
    # Make API request using the extracted GIF IDs
    api_url = 'https://api.redgifs.com/v2/gifs'
    headers = {
        'accept': 'application/json',
        'Authorization': '',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Referer': 'https://www.redgifs.com/'  # Replace with the appropriate referer URL
    }
    params = {
        'ids': gif_id,
        'views': 'yes'
    }
    # Load token from file
    token_file = 'token.txt'
    if os.path.exists(token_file):
        with open(token_file, 'r') as file:
            token = file.read().strip()
            headers['Authorization'] = f'Bearer {token}'
    else:
        print('Token file not found.')
    response = requests.get(api_url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'gifs' in data and len(data['gifs']) > 0:
            for gif in data['gifs']:
                hd_url = gif['urls']['hd']
                response = requests.get(hd_url, headers=headers)
                if response.status_code == 200:
                    gif_id = gif['id']
                    filename = f'{post_id}.mp4'  # Rename the GIF file with the post ID
                    media_file_path = os.path.join(author_folder, filename)
                    with open(media_file_path, 'wb') as file:
                        file.write(response.content)
                    print(f'HD content downloaded successfully as {filename}.')
                else:
                    print(f'Error downloading HD content for GIF ID {gif_id}:', response.status_code)
                    continue  # Skip the post if the GIF media content fails to download
        else:
            print('No GIF data found in the response.')

    else:
        error_message = response.content.decode()
        error_data = json.loads(error_message)
        if "error" in error_data and error_data["error"]["description"] == "Could not verify your access token.":
            # Run get_token.py to update token
            subprocess.call(["python", "get_token.py"])
        else:
            print('Error:', response.status_code)
            print('Response content:', error_message)
    
    return response.status_code  # Return the response status code