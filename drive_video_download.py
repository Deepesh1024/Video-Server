import re
import gdown
import os

import re
import gdown
import os

def download_drive_url(url , save_path="video.mp4"):
    print(f"Downloading from Google Drive URL: {url}")
    pattern = r"https?://drive\.google\.com/(?:(?:file/d/|open\?id=)([a-zA-Z0-9_-]+)(?:/view.*)?|uc\?export=download&id=([a-zA-Z0-9_-]+))$"
    match = re.search(pattern, url)
    
    if match:
        file_id = match.group(1) or match.group(2)
        direct_url = f"https://drive.google.com/uc?id={file_id}"
        try:
            gdown.download(direct_url, output=save_path, quiet=False)
            if not os.path.exists(save_path):
                raise Exception("Download failed: File not found")
            print(f"Video downloaded successfully to {save_path}")
            return {"message": f"Video downloaded to {save_path}"}, 200
        except Exception as e:
            error_msg = str(e)
            if "Cannot retrieve the public link" in error_msg:
                error_msg = "Google Drive file is not publicly accessible. Please set sharing to 'Anyone with the link'."
            print(f"Error downloading video: {error_msg}")
            return {"error": error_msg}, 400
    else:
        print(f"Invalid Google Drive URL: {url}")
        return {"error": f"Invalid Google Drive URL: {url}"}, 400

# Remove or comment out the test code to avoid errors when importing the module
# download_drive_url("https://drive.google.com/file/d/1y-h2WUw-DUjvZo0KOREFRyBOx8YxQtaa/view?usp=sharing")