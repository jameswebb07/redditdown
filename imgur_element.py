import requests
import os

def download_imgur_content(a_element, media_url, author_folder, post_id):
    if media_url.endswith(".gifv"):
        media_url = media_url[:-5] + ".mp4"  # Replace .gifv with .mp4 in the URL

    response = requests.get(media_url)
    if response.status_code == 200:
        # Content download was successful
        imgur_content = response.content

        # Create a file path for the Imgur content
        imgur_file_path = os.path.join(author_folder, f"{post_id}" + os.path.splitext(media_url)[1])
        # Save the Imgur content to the file
        with open(imgur_file_path, "wb") as imgur_file:
            imgur_file.write(imgur_content)

        file_size = os.path.getsize(imgur_file_path)
        if file_size < 1024:  # Check if file size is less than 1KB (1024 bytes)
            os.remove(imgur_file_path)  # Delete the file
            print(f"Download failed for post: {post_id} - File size is less than 1KB")

            # Add the post_id to the skipped record
            skip_record_file = os.path.join(os.getcwd(), "Skip_id.txt")
            with open(skip_record_file, "a") as skip_record:
                skip_record.write(post_id + "\n")
            return 404
    else:
        print(f"Skipping post: {post_id} - Failed to download Imgur content for URL: {media_url}")

        # Add the post_id to the skipped record
        skip_record_file = os.path.join(os.getcwd(), "Skip_id.txt")
        with open(skip_record_file, "a") as skip_record:
            skip_record.write(post_id + "\n")
        return 404

    return response.status_code  # Return the response status code

