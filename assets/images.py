import os
import requests

# Define the URL for the image
image_url = "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ambessa_0.jpg"

# Define the local path to save the image
images_folder = "champion_images"
image_name = "Ambessa.png"
image_path = os.path.join(images_folder, image_name)

# Ensure the images folder exists
os.makedirs(images_folder, exist_ok=True)

# Download the image
response = requests.get(image_url, stream=True)
if response.status_code == 200:
    with open(image_path, 'wb') as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)
    print(f"Image downloaded successfully: {image_path}")
else:
    print(f"Failed to download image. Status code: {response.status_code}")
