import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import time
import re
from urllib.parse import urlparse, unquote
import os
from redgif_element import download_redgif_content
from imgur_element import download_imgur_content
import urllib.parse
from datetime import datetime, timedelta
 
options = webdriver.ChromeOptions()
#options.add_argument('--headless')
#options.add_argument('--no-sandbox')
#options.add_argument('--user-data-dir=/var/www/html/vk/reddit/p95')

# to run on local PC
options.add_argument('--user-data-dir=C:/Users/mindj/AppData/Local/Google/Chrome/User Data/Profile 4')
options.add_argument('chromedriver.exe')  # Set the path to chromedriver.exe here

driver = webdriver.Chrome(options=options)

# Define the URL of the Reddit user's page
url = "https://www.reddit.com/r/BeautifulFemales/"

# Use Selenium to render the page with JavaScript
driver.get(url)

# Wait for the page to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

#time.sleep(300)

scroll_times = 1 # Number of times to scroll down
scroll_delay = 5  # Delay between each scroll action
previous_scroll_position = 0

for _ in range(scroll_times):
    # Scroll down to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_delay)

    # Get the current scroll position
    current_scroll_position = driver.execute_script("return window.pageYOffset;")
    
    # Check if the scroll position has changed
    if current_scroll_position == previous_scroll_position:
        print("End of page reached.")
        break
    
    # Update the previous scroll position
    previous_scroll_position = current_scroll_position

# Extract the page source after rendering
page_source = driver.page_source

# Create a BeautifulSoup object from the page source
soup = BeautifulSoup(page_source, "html.parser")

# Find all the post elements on the page
post_elements = soup.find_all("div", attrs={"data-testid": "post-container"})

# Extract the author name from the URL
subreddit_name = urlparse(url).path.strip("/r/")

# Create a folder with the author's name
author_folder = os.path.join(os.getcwd(), subreddit_name)
os.makedirs(author_folder, exist_ok=True)

# Save the page source in HTML format
#html_file_path = os.path.join(author_folder, f"{subreddit_name}_page_source.html")
#with open(html_file_path, "w", encoding="utf-8") as html_file:
#    html_file.write(page_source)

# Load the existing track record and skipped record
track_record_file = os.path.join(os.getcwd(), "successfully_download_id.txt")
skip_record_file = os.path.join(os.getcwd(), "Skip_id.txt")
if os.path.exists(track_record_file):
    with open(track_record_file, "r") as track_record:
        existing_posts = track_record.read().splitlines()
else:
    existing_posts = []

if os.path.exists(skip_record_file):
    with open(skip_record_file, "r") as skip_record:
        skipped_posts = skip_record.read().splitlines()
else:
    skipped_posts = []


# Iterate over the post elements and extract the desired data
for post_element in post_elements:
    # Check if the post element has the parent with the specific class to skip
    if post_element.find_parent("div", class_="_274hVfCVJjK6-eGJKLQjgQ"):
        continue

    # Extract the postId
    post_id = post_element.get("id")
    
    # Trim Extracted the postId
    post_id = post_id.replace("t3_", "")  # Trim the "t3_" prefix

    # Skip the post if it is already in the track record
    if post_id in existing_posts:
        print("Skipping post:", post_id, "- Already in the successfully download")
        print("-----------------------------------")
        continue

    # Skip the post if it is already in the skipped record
    if post_id in skipped_posts:
        print("Skipping post:", post_id, "- Already in the skipped record")
        print("-----------------------------------")
        continue
    
    # Extract the title
    title_element = post_element.find("h3", class_="_eYtD2XCVieq6emjKBH3m")
    title = title_element.text.strip()

    # Extract the upvote count
    upvote_element = post_element.find("div", class_="_1rZYMD_4xY3gRcSS3p8ODO")
    upvote_count = upvote_element.text.strip() if upvote_element else "0"

    # Extract anchor tag with the specified attributes
    permalink_element = post_element.find("a", attrs={"data-click-id": "comments"})
    if permalink_element:
        permalink = permalink_element.get("href")
        permalink = urllib.parse.urljoin("https://www.reddit.com", permalink)

    # Extract the author_name
    username_element = post_element.find("a", class_="_2tbHP6ZydRpjI44J3syuqC", attrs={"data-testid": "post_author_link"})
    if username_element:
        author_name = username_element.text.lstrip("u/")

    # Extract subreddit data and trim "r/" from the subreddit name
    #subreddit_element = post_element.find("a", class_="_3ryJoIoycVkA88fy40qNJc", href=True)
    #subreddit_url = subreddit_element["href"]
    #subreddit_name = subreddit_url.split("/")[2]

    # Extract the over_18
    over_18_element = post_element.find("span", class_="_2VF2J19pUIMSLJFky-7PEI")
    result = {}
    if over_18_element and over_18_element.text:
        result["over_18"] = True
        result["text"] = over_18_element.text
    else:
        result["over_18"] = False

    # Extract the Post created_utc
    date_element = post_element.find("span", class_="_2VF2J19pUIMSLJFky-7PEI", attrs={"data-testid": "post_timestamp"})
    if date_element:
        date_data = date_element.text.strip()
        # Mapping of time units to timedelta units
        time_units = {"days": "days", "hours": "hours", "minutes": "minutes"}
        # Extract the numeric value and unit from date_data
        value, unit = date_data.split()[0:2]
        if unit in time_units:
            # Calculate the timedelta
            delta = timedelta(**{time_units[unit]: int(value)})
        else:
            # Invalid date data
            delta = timedelta()
        # Get the current UTC time
        current_time_utc = datetime.utcnow()
        # Subtract the timedelta from the current time to get the post time
        post_time_utc = current_time_utc - delta
        # Convert the post time to UNIX timestamp format
        created_utc = int(post_time_utc.timestamp())

    # Extract the flair_name if the element exists
    flair_element = post_element.find("span", class_="_1jNPl3YUk6zbpLWdjaJT1r")
    flair_name = flair_element.text.strip() if flair_element else ""

    # Extract the additional flair if the element exists
    additional_flair_element = post_element.find("div", class_="_2X6EB3ZhEeXCh1eIVA64XM")
    additional_flair = additional_flair_element.text.strip() if additional_flair_element else ""

    # Combine the main flair and additional flair
    combined_flair = f"{flair_name} {additional_flair}".strip()

    # Find the <img> element within the post_element
    img_element = post_element.find("img", alt="Post image")
    video_element = post_element.find("video", class_="tErWI93xEKrI2OkozPs7J")
    a_element = post_element.find("a", class_="_13svhQIUZqD9PVzFcLwOKT")

    # Skip the post if image or video element not found
    if not img_element and not video_element and not a_element:
        continue

    image_url = None  # Define the image_url variable
    video_url = None  # Define the video_url variable

    if img_element:
        # Extract the image URL
        image_url = img_element.get("src")
        
        if 'external-preview.redd.it' in image_url:
            # Extract the href attribute
            href = a_element.get("href")
            media_url = href

            # Call the imgur content downloader function
            status_code = download_imgur_content(a_element, media_url, author_folder, post_id)
            if status_code != 200:
                print("Skipping imgur for post:", post_id, "- Failed to download content")
                print("-----------------------------------")
                continue
        else:
            # Download and save the image content 
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                image_content = image_response.content
                # Create a file path for the image content
                image_file_path = os.path.join(author_folder, f"{post_id}.jpg")
                # Save the image content to the file
                with open(image_file_path, "wb") as image_file:
                    image_file.write(image_content)
                # Create the media_url by replacing the domain and removing query parameters
                media_url = image_url.replace("preview.redd.it", "i.redd.it").split('?')[0]
            else:
                print("Skipping image for post:", post_id, "- Failed to download image content")
                continue

            
    elif video_element:
        # Find the <video> element within the post_element
        # Extract the video URL
        video_url = video_element.find("source").get("src")

    elif a_element:
        # Extract the href attribute
        href = a_element.get("href")
        media_url = href

        # Check the domain and call the appropriate content downloader function
        if 'redgifs.com' in media_url:
            # Call the redgif content downloader function
            status_code = download_redgif_content(a_element, media_url, author_folder, post_id)
            if status_code != 200:
                print("Skipping redgif for post:", post_id, "- Failed to download content")
                continue

        elif 'imgur.com' in media_url:
            # Call the imgur content downloader function
            status_code = download_imgur_content(a_element, media_url, author_folder, post_id)
            if status_code != 200:
                print("Skipping imgur for post:", post_id, "- Failed to download content")
                print("-----------------------------------")
                continue

        else:
            print("Unsupported domain:", media_url)
        

    # Download and save the video content
    if video_url:
        video_response = requests.get(video_url)
        if video_response.status_code == 200:
            video_content = video_response.content
            # Create a file path for the video content
            video_file_path = os.path.join(author_folder, f"{post_id}.mp4")
            # Save the video content to the file
            with open(video_file_path, "wb") as video_file:
                video_file.write(video_content)
            # Create the media_url by replacing the domain and removing query parameters           
            media_url = video_url.replace("preview.redd.it", "i.redd.it").split('?')[0]
        else:
            print("Skipping video for post:", post_id, "- Failed to download video content")
            continue

    
    # Create a dictionary to storethe post data
    post_data = {
        "id": post_id,
        "author": author_name,
        "title": title,
        "subreddit": subreddit_name,
        "score": upvote_count,
        "link_flair_text": combined_flair,
        "url": media_url,
        "permalink": permalink,
        "over_18": result["over_18"],
        "created_utc:": created_utc
    }


    # Print or process the extracted data as per your requirement
    print("Post ID:", post_id)
    print("Author:", author_name)
    print("Subreddit:", subreddit_name)
    print("Title:", title)
    print("Upvote Score:", upvote_count)
    print("flair:", combined_flair)
    print("Media URL:", media_url)
    print("Permalink:", permalink)
    print("Over 18:", post_data["over_18"])
    print("Post Created:", date_data)
    print("-----------------------------------")


    # Add the post_id to the track record
    existing_posts.append(post_id)

    # Update the track record file
    with open(track_record_file, "a") as track_record:
        track_record.write(post_id + "\n")

   # Create a JSON file path for the post
    post_json_path = os.path.join(author_folder, f"{post_id}.json")

    # Save the post data in JSON format only if the media content is successfully downloaded
    if image_url or video_url or a_element:
        with open(post_json_path, "w") as json_file:
            json.dump(post_data, json_file, indent=4)
    else:
        print("Skipping JSON for post:", post_id, "- No media content available")



# Close the Selenium driver
driver.quit()
